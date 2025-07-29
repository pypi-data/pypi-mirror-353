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

import pathlib
from itertools import count
from typing import overload
from typing import Iterable
from typing import Mapping
from typing import Tuple
from typing import Union

import wrapt

from .query import Query
from .types import Connection
from .exceptions import InvalidStatement
from .parsing import split_statements

SQL_FILE_GLOB = "**/*.sql"


class Module:
    _conn = None
    queries: dict = {}
    _query_mtimes: dict[pathlib.Path, float] = {}
    directories: list[pathlib.Path]

    def __init__(self, *paths: Union[str, pathlib.Path], auto_reload=False):
        self.queries = {}
        self.directories = []
        self.auto_reload = auto_reload
        for p in paths:
            self.load_dir(p)

    def __getattr__(self, name):
        if self.auto_reload:
            self.ensure_up_to_date(name)
            try:
                query = reloadable_query_proxy(self, name)
            except KeyError:
                raise AttributeError(name)
        else:
            try:
                query = self.queries[name]
            except KeyError:
                import difflib

                matches = difflib.get_close_matches(name, list(self.queries), n=1)
                raise AttributeError(
                    f"{self!r} has no attribute {name!r}"
                    + (f" Did you mean {matches[0]!r}?" if matches else "")
                )
        if not query.includes_resolved:
            query.resolve_includes(self)
        return query

    def __enter__(self):
        return self

    def __exit__(self, type, value, traceback):
        return

    def __iter__(self):
        return iter(self.queries.values())

    def __repr__(self):
        return f"<{self.__class__.__module__}.{self.__class__.__qualname__} {':'.join(map(str, self.directories))}>"

    def clear(self):
        self.queries.clear()

    def add_query(self, name, query: Union[Query, str]):
        if isinstance(query, str):
            return self.add_query(name, Query(query))
        if name in self.queries:
            raise InvalidStatement(
                f"Can't add query {name!r} in {query.source}: "
                f"{self!r} already has an attribute named {name!r} "
                f"(loaded from {getattr(self, name).source})"
            )

        if self._conn:
            query = query.bind(self._conn)
        query.name = name
        self.queries[name] = query
        if query.source:
            path = pathlib.Path(query.source)
            if path.exists():
                self._query_mtimes[path] = path.stat().st_mtime

    def add_queries(self, qs: Union[Iterable[Tuple[str, Query]], Mapping[str, Query]]):
        if isinstance(qs, Mapping):
            qs = qs.items()
        for name, query in qs:
            self.add_query(name, query)

    def load_dir(self, path: Union[str, pathlib.Path]):
        path = pathlib.Path(path)
        if path not in self.directories:
            self.directories.append(path)
        for p in path.glob(SQL_FILE_GLOB):
            self.load_file(p)

        return self

    def load_file(self, path: pathlib.Path):
        queries = list(load_queries(path))
        for query in queries:
            self.add_query(query.name, query)

    def ensure_up_to_date(self, query_name: str) -> bool:
        """
        Ensure that the named query is up to date, reloading from disk if
        required.

        Returns ``True`` if the query was reloaded
        """
        try:
            query = self.queries[query_name]
        except KeyError:
            self.clear()
            for path in self.directories:
                self.load_dir(path)
            return True
        includes_reloaded = False
        for included in query.includes:
            if self.ensure_up_to_date(included):
                includes_reloaded = True
        path = pathlib.Path(query.source)
        try:
            last_mtime = self._query_mtimes[path]
        except KeyError:
            last_mtime = 0.0

        if not path.exists():
            mtime = 0.0
        else:
            mtime = path.stat().st_mtime

        if mtime != last_mtime:
            for item in list(self.queries):
                if self.queries[item].source == query.source:
                    del self.queries[item]

            if path.exists():
                self.load_file(path)
                self._query_mtimes[path] = mtime
            return True
        if includes_reloaded:
            query.resolve_includes(self)
            return True
        return False

    def query(self, sql: str) -> Query:
        """
        Return a new, unnamed query.
        This convenience method is intended to facilitate ad-hoc
        queries, for example::

            >>> mod = embrace.module.Module()
            >>> result = mod.query("SELECT * FROM mytable").one(conn)

        It differs from instantiating ``embrace.query.Query``
        directly in that:
        - ``:include:`` markers will be resolved,
        - if the module has a connection bound,
          it will be bound to the returned query
        """
        query = Query(sql, source="<string>")
        if self._conn:
            query = query.bind(self._conn)
        query.resolve_includes(self)
        return query

    @overload
    def _run_query(self, result_type: str, sql: str, *args, **kwargs):
        ...

    @overload
    def _run_query(self, result_type: str, conn: Connection, sql: str, *args, **kwargs):
        ...

    def _run_query(self, result_type, *args, **kwargs):
        if isinstance(args[0], str):
            conn = self._conn
            sql, *args = args
        else:
            conn, sql, *args = args
        query = self.query(sql)
        return getattr(query, result_type)(conn, *args, **kwargs)

    def resultset(self, *args, **kwargs):
        return self._run_query("resultset", *args, **kwargs)

    def execute(self, *args, **kwargs):
        return self._run_query("execute", *args, **kwargs)

    def one(self, *args, **kwargs):
        return self._run_query("one", *args, **kwargs)

    def one_or_none(self, *args, **kwargs):
        return self._run_query("one_or_none", *args, **kwargs)

    def first(self, *args, **kwargs):
        return self._run_query("first", *args, **kwargs)

    def many(self, *args, **kwargs):
        return self._run_query("many", *args, **kwargs)

    def scalar(self, *args, **kwargs):
        return self._run_query("scalar", *args, **kwargs)

    def affected(self, *args, **kwargs):
        return self._run_query("affected", *args, **kwargs)

    def column(self, *args, **kwargs):
        return self._run_query("column", *args, **kwargs)

    def cursor(self, *args, **kwargs):
        return self._run_query("cursor", *args, **kwargs)

    def bind(self, conn) -> "Module":
        """
        Return a copy of the module bound to a database connection
        """
        cls = self.__class__
        bound = cls.__new__(cls)
        bound.__dict__ = {
            "_conn": conn,
            "auto_reload": self.auto_reload,
            "directories": self.directories,
            "_query_mtimes": self._query_mtimes,
            "queries": {name: q.bind(conn) for name, q in self.queries.items()},
        }
        return bound

    def transaction(self, conn) -> "Transaction":
        return Transaction(self, conn)

    def savepoint(self, conn) -> "Savepoint":
        return Savepoint(self, conn)


class Transaction:
    def __init__(self, module, conn):
        self.conn = conn
        self.module = module.bind(conn)

    def __enter__(self):
        return self.module

    def __exit__(self, type, value, traceback):
        if type:
            self.conn.rollback()
        else:
            self.conn.commit()

    def commit(self):
        self.conn.commit()

    def rollback(self):
        self.conn.rollback()


class Savepoint:
    _seq = count()

    def __init__(self, module, conn):
        self.conn = conn
        self.module = module.bind(conn)
        self.savepoint = f"sp_{next(self._seq)}"
        self._cursor = None

    def __enter__(self):
        self._cursor = self.conn.cursor()
        self._cursor.execute(f"SAVEPOINT {self.savepoint}")
        return self.module

    def __exit__(self, type, value, traceback):
        if self._cursor is not None:
            if type:
                self._cursor.execute(f"ROLLBACK TO SAVEPOINT {self.savepoint}")
            else:
                self._cursor.execute(f"RELEASE SAVEPOINT {self.savepoint}")
            self._cursor.close()


def load_queries(path: pathlib.Path) -> Iterable[Query]:
    with path.open("r", encoding="UTF-8") as f:
        sql = f.read()
        for ix, (metadata, statements) in enumerate(split_statements(sql)):
            if not metadata.name:
                if ix == 0:
                    metadata.name = path.stem
                else:
                    raise InvalidStatement(
                        f"{path!s}, line {metadata.lineno}: no name specified (eg `-- :name my_query_name`)"
                    )
            yield Query.from_statements(
                metadata,
                statements,
                source=str(path),
                lineno=metadata.lineno,
                name=metadata.name,
            )


def reloadable_query_proxy(module, name):
    def get_query():
        return module.queries[name]

    class ReloadableQueryProxy(wrapt.ObjectProxy):
        def __call__(self, *args, **kwargs):
            module.ensure_up_to_date(name)
            self.__wrapped__ = get_query()
            return self.__wrapped__(*args, **kwargs)

        def bind(self, conn):
            return reloadable_query_proxy(module, name)

    return ReloadableQueryProxy(get_query())
