#  Copyright 2020 Oliver Cope
#
#  Licensed under the Apache License, Version 2.0 (the "License");
#  you may not use this file except in compliance with the License.
#  You may obtain a copy of the License at
#
#      http://www.apache.org/licenses/LICENSE-2.0
#
#  Unless required by applicable law or agreed to in writing, software
#  distributed under the License is distributed on an "AS IS" BASIS,
#  WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
#  See the License for the specific language governing permissions and
#  limitations under the License.

from collections.abc import Sequence
from itertools import chain
from itertools import islice
from typing import Callable
from typing import Iterable
from typing import List
from typing import Mapping
from typing import Optional
from typing import Union
from typing import TYPE_CHECKING
import dataclasses
import sys
import logging
import typing as t

import sqlparse

from .parsing import compile_bind_parameters
from .parsing import split_statements
from .parsing import compile_includes
from .parsing import get_placeholder_info
from .parsing import Metadata
from . import parsing
from .mapobject import mapobject
from .mapobject import make_rowspec
from .mapobject import joinedload
from .mapobject import RowMapper
from . import exceptions
from .types import Connection
from .types import Cursor


if TYPE_CHECKING:
    from embrace.module import Module

known_styles: dict[type, str] = {}

_marker = object()
T = t.TypeVar("T")
U = t.TypeVar("U")
V = t.TypeVar("V")

logger = logging.getLogger(__name__)


def get_param_style(conn: Connection, known_styles=known_styles) -> str:
    conncls = conn.__class__
    try:
        return known_styles[conncls]
    except KeyError:
        modname = conncls.__module__
        while modname:
            try:
                style = sys.modules[modname].paramstyle  # type: ignore
                known_styles[conncls] = style
                return style
            except AttributeError:
                if "." in modname:
                    modname = modname.rsplit(".", 1)[0]
                else:
                    break
    raise TypeError(f"Can't find paramstyle for connection {conn!r}")


class ResultSet(t.Generic[T, U]):
    __slots__ = ["cursor", "row_mapper", "maprows"]

    def __init__(self, cursor, row_mapper: RowMapper):
        self.cursor = cursor
        self.row_mapper = row_mapper
        if row_mapper:
            self.maprows = self.row_mapper.make_row_mapper()
        else:
            self.maprows = None

    def __iter__(self):
        return self.many()

    def one(self) -> T:
        row = self.cursor.fetchone()
        if row is None:
            raise exceptions.NoResultFound()
        if self.cursor.fetchone() is not None:
            raise exceptions.MultipleResultsFound()
        if self.maprows:
            return next(self.maprows([row]))  # type: ignore
        return row

    def first(self) -> T:
        row = self.cursor.fetchone()
        if row and self.maprows:
            return next(self.maprows([row]))  # type: ignore
        return row

    def many(
        self, method: str = "auto", limit_rows: int = 0, limit_mapped: int = 0
    ) -> t.Iterator[T]:
        """
        Return an iterator over the ResultSet.

        :param method: The cursor method used to fetch results.
                       Must be one of 'auto', 'fetchone', 'fetchmany', or 'fetchall'
                       (default: 'auto'). If ``auto`` is selected, ``fetchall``
                       will be used unless a limit is given, in which case
                       ``fetchmany`` will be used.
        :param limit_rows: Maximum number of rows to fetch.
                           This is based on the number of rows returned. If you
                           are using joins to compose these into objects, this
                           may not correspond with the number of objects yielded.
        :param limit_mapped: Maximum number of mapped objects to generate.
        """
        if method == "auto":
            # Shortcut the default case
            if not limit_mapped and not limit_rows:
                if self.maprows:
                    return self.maprows(self.cursor.fetchall())
                else:
                    return iter(self.cursor.fetchall())
            method = "fetchmany"

        row_getter = getattr(self, f"many_rows_{method}")
        if self.maprows:
            if limit_mapped:

                def limited_rowmapper():
                    count = 0
                    rowcount = 0

                    if method == "fetchmany":

                        def _row_getter():
                            while True:
                                if count == 0:
                                    limit = self.cursor.arraysize
                                else:
                                    remaining = limit_mapped - count
                                    limit = int(((remaining + 1) * rowcount) / count)

                                ix = 0
                                for row in row_getter(limit=limit):
                                    yield row
                                    ix += 1
                                if ix == 0:
                                    return

                        rows = _row_getter()
                    else:
                        rows = row_getter()

                    for ix, mapped in enumerate(self.maprows(rows), 1):
                        yield mapped
                        if ix >= limit_mapped:
                            break

                return limited_rowmapper()
            else:
                return self.maprows(row_getter(limit=limit_rows))
        else:
            return row_getter(limit=(limit_rows or limit_mapped))

    def many_rows_fetchone(self, limit: int = 0) -> t.Iterator[T]:
        if limit:
            return islice(iter(self.cursor.fetchone, None), limit)
        else:
            return iter(self.cursor.fetchone, None)

    def many_rows_fetchmany(self, limit: int = 0) -> t.Iterator[T]:
        if limit:
            arraysize = self.cursor.arraysize
            fullbatches, remainder = divmod(limit, arraysize)
            for ix in range(fullbatches):
                yield from self.cursor.fetchmany(arraysize)
            if remainder:
                yield from self.cursor.fetchmany(remainder)
        else:
            for batch in iter(self.cursor.fetchmany, []):
                yield from batch

    def many_rows_fetchall(self, limit: int = 0) -> t.Iterator[T]:
        if limit:
            return iter(self.cursor.fetchall()[:limit])
        else:
            return iter(self.cursor.fetchall())

    def one_or_none(self) -> t.Optional[T]:
        row = self.cursor.fetchone()
        if self.cursor.fetchone() is not None:
            raise exceptions.MultipleResultsFound()
        if row and self.maprows:
            return next(self.maprows([row]))
        return row

    @t.overload
    def scalar(self, default: V) -> t.Union[U, V]:
        ...

    @t.overload
    def scalar(self) -> U:
        ...

    def scalar(self, default=_marker):
        value = next(self.column(), default)
        if value is _marker:
            raise exceptions.NoResultFound()
        return value

    def column(self) -> t.Iterator[T]:
        if self.row_mapper:
            column_slice = self.row_mapper.get_split_points()[0]
            row_mapper = dataclasses.replace(
                self.row_mapper, row_spec=self.row_mapper.row_spec[:1]
            )
            rows = (row[column_slice] for row in iter(self.cursor.fetchone, None))
            return row_mapper.make_row_mapper()(rows)
        first = self.cursor.fetchone()
        if first:
            if isinstance(first, Mapping):
                key = next(iter(first))
            elif isinstance(first, Sequence):
                key = 0
            else:
                raise TypeError(
                    f"Can't find first column for row of type {type(first)}"
                )
            return (
                row[key] for row in chain([first], iter(self.cursor.fetchone, None))
            )
        return iter([])

    def affected(self) -> int:
        return self.cursor.rowcount

    @property
    def rowcount(self) -> int:
        return self.cursor.rowcount


class Query(t.Generic[T, U]):
    name: Optional[str]
    source: Optional[str]
    lineno: Optional[int]
    includes: List[str] = []
    includes_resolved = False
    metadata: Metadata = Metadata()
    statements: list[str]
    row_mapper: Optional[RowMapper] = None

    def __init__(
        self,
        sql: Optional[str] = None,
        source: Optional[str] = None,
        lineno: Optional[int] = None,
        name: Optional[str] = None,
        metadata: Optional[Metadata] = None,
    ):
        self.name = name
        self.result_map = None
        self.src = sql
        self.statements = []
        if sql:
            self._configure_from_string(sql)

        self.metadata = metadata or self.metadata
        self.source = source
        self.lineno = lineno
        self._conn = None

    def __repr__(self):
        return f"<{self.__class__.__name__} from {self.source}:{self.lineno}>"

    @classmethod
    def from_statements(
        cls, metadata: Metadata, statements: Sequence[sqlparse.sql.Statement], **kwargs
    ) -> "Query":
        q = cls(**kwargs)
        q._configure_from_statements(metadata, statements)
        return q

    def _configure_from_string(self, s: str):
        metadata, statements = next(iter(split_statements(s)))
        self._configure_from_statements(metadata, statements)

    def _configure_from_statements(
        self, metadata: Metadata, statements: Sequence[sqlparse.sql.Statement]
    ):
        try:
            returning = parsing.parse_returning_metadata(
                imports=metadata.imports,
                returns=metadata.returns,
                joins=metadata.joins,
                key_columns=metadata.key_columns,
                split_on=metadata.split_on,
            )
        except Exception:
            logger.exception(f"Error parsing {metadata=}")
            raise
        self.statements = [str(s) for s in statements]
        self.metadata = metadata
        if returning:
            self._configure_returning(
                row_spec=returning.row_spec,
                joins=returning.joins,
                key_columns=returning.key_columns,
                split_on=returning.split_on,
            )

    def resolve_includes(self, module: "Module") -> bool:
        new_statements = []
        for stmt in self.statements:
            include_names, replace_includes = compile_includes(stmt)
            try:
                queries = [module.queries[n] for n in include_names]
            except KeyError:
                self.includes_resolved = False
                return False
            for q in queries:
                q.resolve_includes(module)

            new_statements.append(replace_includes(queries))
            self.includes = include_names
        self.statements = new_statements
        self.includes_resolved = True
        return True

    def get_placeholder_info(self) -> list[tuple[str, str]]:
        """
        Return a list of placeholder names in the query in source order
        """
        names = {}
        for sql in self.statements:
            for name, type_hint in get_placeholder_info(sql):
                names.setdefault(name, type_hint)
        return list(names.items())

    def copy(self) -> "Query":
        """
        Return a copy of the query
        """
        cls = self.__class__
        new = cls.__new__(cls)
        new.__dict__ = self.__dict__.copy()
        return new

    def bind(self, conn) -> "Query":
        """
        Return a copy of the query bound to a database connection
        """
        bound = self.copy()
        bound._conn = conn
        return bound

    def returning(
        self,
        row_spec: Union["mapobject", Callable, Sequence[Union["mapobject", Callable]]],
        joins: Union[joinedload, Sequence[joinedload]] = [],
        positional=False,
        key_columns: Optional[list[tuple[str, ...]]] = None,
        split_on=[],
    ) -> "Query":
        """
        Return a copy of the query configured to map and join objects

        :param row_spec:
            One of:
                - a single callable or :class:`mapobject` instance
                - a sequence of callables and :class:`mapobject` instances

            In the case that a single callable or mapobject is provided, the
            values for each row will be passed to the callable as keyword
            arguments, and each row will return a single python object.

            If a sequence of items is provided, the row will be split up into
            multiple objects at the columns indicated by the values of
            ``split_on``, or configured in :attr:`mapobject.split_on`.

        :param joins:
            When multiple python objects are generated per-row, ``joins``
            tells embrace how to construct relations between objects. See
            :func:`joinone` and :func:`joinmany`.

        :param positional:
            If True, pass column values to the items in ``row_spec`` as
            positional parameters rather than keyword args.

        :key_columns:
            The list of primary key columns for each object mapped by ``row_spec``.
            Rows with the same values in these columns will be mapped to the
            same python object.

            If key_columns is not provided, rows will be mapped to the same
            python object if all values match.

            It is an error to use this parameter if :class:`mapobject` is
            used anywhere in ``row_spec``.

        :split_on:
            List of the column names that mark where new objects start
            splitting a row into multiple python objects. If not provided,
            the string ``'id'`` will be used.

            It is an error to use this parameter if :class:`mapobject` is
            used anywhere in ``row_spec``.
        """
        q = self.copy()
        q._configure_returning(
            row_spec=row_spec,
            joins=joins,
            positional=positional,
            key_columns=key_columns,
            split_on=split_on,
        )
        return q

    def _configure_returning(
        self,
        row_spec: Union["mapobject", Callable, Sequence[Union["mapobject", Callable]]],
        joins: Union[joinedload, Sequence[joinedload]] = [],
        positional=False,
        key_columns: Optional[list[tuple[str, ...]]] = None,
        split_on=[],
    ):
        if isinstance(joins, joinedload):
            joins = [joins]

        row_spec = make_rowspec(row_spec, split_on or [], key_columns or [], positional)
        self.row_mapper = RowMapper(row_spec, joins=joins)

    def resultset(
        self,
        conn: Optional[Connection] = None,
        *,
        params: Optional[Mapping] = None,
        default=_marker,
        debug: bool = False,
        _result: Optional[str] = None,
        _get_param_style=get_param_style,
        _resultset=ResultSet,
        _compile_bind_parameters=compile_bind_parameters,
        **kw,
    ) -> ResultSet[T, U]:
        if conn is None:
            conn = self._conn
            if conn is None:
                raise TypeError("Query must be called with a connection argument")

        paramstyle = _get_param_style(conn)
        cursor: Cursor = conn.cursor()  # type: ignore
        if params:
            if kw:
                kw.update(params)
                params = kw
        else:
            params = kw

        prepared = [
            _compile_bind_parameters(paramstyle, s, params) for s in self.statements
        ]
        for sqltext, bind_params in prepared:
            if debug:
                import textwrap

                print(
                    f"Executing \n{textwrap.indent(sqltext, '    ')} "
                    f"with {bind_params!r}",
                    file=sys.stderr,
                )
            try:
                cursor.execute(sqltext, bind_params)
            except BaseException:
                _handle_exception(conn, self.source, 1)

        if self.row_mapper and cursor.description:
            self.row_mapper.set_description(cursor.description)
            row_mapper = self.row_mapper
        else:
            row_mapper = None
        return _resultset(cursor, row_mapper)

    def one(self, conn=None, *, debug=False, **kwargs) -> T:
        return self.resultset(conn, debug=debug, **kwargs).one()

    def one_or_none(self, conn=None, *, debug=False, **kwargs) -> t.Optional[T]:
        return self.resultset(conn, debug=debug, **kwargs).one_or_none()

    @t.overload
    def scalar(self, conn=None, *, default: V, debug=False, **kwargs) -> t.Union[U, V]:
        ...

    @t.overload
    def scalar(self, conn=None, *, debug=False, **kwargs) -> U:
        ...

    def scalar(self, conn=None, *, default=_marker, debug=False, **kwargs):
        return self.resultset(conn, debug=debug, **kwargs).scalar(default=default)

    def first(self, conn=None, *, debug=False, **kwargs) -> t.Optional[T]:
        return self.resultset(conn, debug=debug, **kwargs).first()

    def many(self, conn=None, *, debug=False, **kwargs) -> t.Iterator[T]:
        return self.resultset(conn, debug=debug, **kwargs).many()

    def column(self, conn=None, *, debug=False, **kwargs) -> Iterable[U]:
        return self(conn, debug=debug, **kwargs).column()  # type: ignore

    def cursor(self, conn=None, *, debug=False, **kwargs) -> Cursor:
        return self.resultset(conn, debug=debug, _result="resultset", **kwargs).cursor

    def affected(self, conn=None, *, debug=False, **kwargs) -> int:
        return self.resultset(conn, debug=debug, **kwargs).rowcount

    __call__ = execute = resultset
    rowcount = affected


def _handle_exception(conn, filename, lineno):
    """
    We have an exception of unknown type, probably raised
    from the dbapi module
    """
    exc_type, exc_value, exc_tb = sys.exc_info()
    if exc_type and exc_value:
        classes = [exc_type]
        while classes:
            cls = classes.pop()
            clsname = cls.__name__

            if clsname in exceptions.pep_249_exception_names:
                newexc = exceptions.pep_249_exception_names[clsname]()
                newexc.args = getattr(exc_value, "args", tuple())
                newexc = newexc.with_traceback(exc_tb)
                if filename:
                    newlines = "\n" * (lineno - 1)
                    exec(
                        compile(
                            f"{newlines}raise newexc from exc_value", filename, "exec"
                        ),
                        {
                            "__name__": filename,
                            "__file__": filename,
                            "newexc": newexc,
                            "exc_value": exc_value,
                        },
                        {},
                    )
                else:
                    raise newexc from exc_value
            classes.extend(getattr(cls, "__bases__", []))

        raise exc_value.with_traceback(exc_tb) from exc_value


def joinone(target, attr, source):
    """
    Populate `<target>.<attr>` with
    the item identified by `source`.
    """
    return joinedload(target, attr, source, "1")


def joinmany(target, attr, source):
    """
    Populate `<target>.<attr>` with the list of items identified by `source`.
    """
    return joinedload(target, attr, source, "*")


one_to_many = joinmany
one_to_one = joinone
