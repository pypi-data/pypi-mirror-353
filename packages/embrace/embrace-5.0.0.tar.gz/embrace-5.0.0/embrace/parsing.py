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

import re
import dataclasses
from itertools import count
from functools import partial
from typing import Any
from typing import Dict
from typing import Iterable
from typing import Callable
from typing import List
from typing import Mapping
from typing import Union
from typing import Optional
from typing import Tuple
from typing import Sequence
from typing import Iterator
from typing import TYPE_CHECKING
import typing as t

if TYPE_CHECKING:
    from embrace.query import Query

import sqlparse
import sqlparse.sql

from .mapobject import mapobject
from .mapobject import make_rowspec
from .mapobject import joinedload

BindParams = Union[Tuple, Mapping]
Tokens = List[Tuple]

param_styles = {
    "qmark": (True, lambda name, c: "?"),
    "numeric": (True, lambda name, c: f":{c}"),
    "format": (True, lambda name, c: "%s"),
    "pyformat": (False, lambda name, c: f"%({name})s"),
    "named": (False, lambda name, c: f":{name}"),
}
name_pattern = re.compile(r":name\s+(?P<name>\w+)", re.X)
args_pattern = re.compile(r":args\s+(?P<args>.*)$", re.X)
return_pattern = re.compile(r":returns?\s+(?P<returns>.*)$", re.X)
joins_pattern = re.compile(r":join(?P<joins>(?:one|many)\s+.*)$", re.X)
split_on_pattern = re.compile(r":spliton\s+(?P<split_on>.*)$", re.X)
key_columns_pattern = re.compile(r":keycolumns?\s+(?P<key_columns>.*)$", re.X)
import_pattern = re.compile(r":(?P<imports>(?:import|from)\s+.*)$", re.X)
include_pattern = re.compile(r":include:([a-zA-Z_]\w*)")
param_pattern = re.compile(
    r"""
    # Don't match if:
    # - preceded by backslash (an escape) or ':' (an SQL cast, eg '::INT')
    # - it's an include pattern
    (?<![:\\])
    (?!:include:)
    (?<!:include:)

    # Optional parameter type
    (?:
        :(?P<param_type>
            value|v|value\*|v\*|tuple|t|tuple\*|t\*|identifier|i|raw|r
        )
    )?

    # An identifier
    :(?P<param>[a-zA-Z_]\w*)

    # Optional type hint
    (?::(?P<type_hint>[a-zA-Z\[\]_.|]+))?

    # followed by a non-word char, or end of string
    (?=\W|$)
    """,
    re.X,
)


class ParseError(Exception):
    ...


@dataclasses.dataclass
class Metadata:
    name: Optional[str] = None
    lineno: Optional[int] = None
    args: Optional[str] = None
    returns: Optional[str] = None
    imports: list[str] = dataclasses.field(default_factory=list)
    joins: list[str] = dataclasses.field(default_factory=list)
    split_on: list[str] = dataclasses.field(default_factory=list)
    key_columns: list[str] = dataclasses.field(default_factory=list)

    def update(self, other: "Metadata"):
        defaults = self.__class__().asdict()
        for k, v in other.asdict().items():
            if isinstance(getattr(self, k), list):
                getattr(self, k).extend(v)
            else:
                if v != defaults[k]:
                    setattr(self, k, v)

    def asdict(self):
        return dataclasses.asdict(self)


def parse_comment_metadata(s: str) -> Metadata:
    lines = (re.sub(r"^\s*--", "", line).strip() for line in s.split("\n"))
    patterns = [
        name_pattern,
        args_pattern,
        return_pattern,
        import_pattern,
        joins_pattern,
        split_on_pattern,
        key_columns_pattern,
    ]
    metadata = Metadata()
    for line in lines:
        for p in patterns:
            if mo := p.match(line):
                for k, v in mo.groupdict().items():
                    if v is not None:
                        if isinstance(getattr(metadata, k), list):
                            getattr(metadata, k).append(v)
                        else:
                            setattr(metadata, k, v)

    return metadata


def quote_ident_ansi(s):
    s = str(s)
    if "\x00" in s:
        raise ValueError(
            "Quoted identifiers can contain any character, "
            "except the character with code zero"
        )
    return f'''"{s.replace('"', '""')}"'''


def compile_includes(
    statement: str,
) -> Tuple[List[str], Callable[[Sequence["Query"]], str]]:
    """
    Parse a statement str, looking for ':include:<name>' patterns. Return the
    list of include names found, and a function that will accept the named
    queries in order and return a modified statement string.
    """

    # Will be [<stmt>, <include_name>, <stmt>, <include_name>, … <stmt>]
    splits = include_pattern.split(statement)

    # List of matched include names
    names = splits[1::2]

    def strip_semicolon(stmt: str) -> str:
        return stmt.rstrip().rstrip(";")

    def replace_includes(includes: Sequence["Query"]) -> str:
        iterincludes = iter(includes)
        return "".join(
            s
            if ix % 2 == 0
            else ";".join(map(strip_semicolon, next(iterincludes).statements))
            for ix, s in enumerate(splits)
        )

    return names, replace_includes


def compile_bind_parameters(
    target_style: str, sql: str, bind_parameters: Mapping
) -> Tuple[str, BindParams]:
    """
    :param target_style: A DBAPI paramstyle value (eg 'qmark', 'format', etc)
    :param sql: An SQL str
    :bind_parameters: A dict of bind parameters for the query

    :return: tuple of `(sql, bind_parameters)`. ``sql`` will be rewritten with
             the target paramstyle; ``bind_parameters`` will be a tuple or
             dict as required.
    :raises: TypeError, if the bind_parameters do not match the query
    """

    is_positional, param_gen = param_styles[target_style]

    if target_style[-6:] == "format":
        sql = sql.replace("%", "%%")
    params: Union[list, dict[str, Any]]
    if is_positional:
        params = []
    else:
        params = {}

    transformed_sql = param_pattern.sub(
        partial(
            replace_placeholder,
            params,
            param_gen,
            count(1),
            bind_parameters,
        ),
        sql,
    )
    if is_positional:
        return transformed_sql, tuple(params)
    else:
        return transformed_sql, params  # type: ignore


def get_placeholder_info(sql: str) -> Iterator[tuple[str, str]]:
    """
    Generate tuples of ``(<name>, <optional type hint>)``
    for all placeholders present in ``sql``
    """
    for match in param_pattern.finditer(sql):
        gd = match.groupdict()
        yield gd["param"], gd["type_hint"] or "None"


def split_statements(
    sql: str,
) -> Iterable[tuple[Metadata, list[sqlparse.sql.Statement]]]:
    """
    Split an sql string into multiple queries and parse any metadata
    found in comments
    """
    statements = sqlparse.parse(sql)
    positions = []
    offset = 0
    for s in statements:
        offset = sql.index(str(s), offset)
        positions.append(offset)

    statements = ((pos, s) for pos, s in zip(positions, statements) if str(s).strip())
    current: tuple[Optional[Metadata], list[sqlparse.sql.Statement]] = (None, [])

    for pos, statement in statements:
        metadata, tokens = parse_tokens(statement)
        metadata.lineno = sql[:pos].count("\n") + 1
        statement.tokens[:] = tokens

        if starts_new_statement(metadata):
            if current[0] is not None:
                yield current
            current = metadata, [statement]

        else:
            if current[0] is None:
                current = (metadata, [statement])
            else:
                current[0].update(metadata)
                current[1].append(statement)

    if current[0] is not None:
        yield current


def replace_placeholder(
    params: Union[Dict[str, Any], List[Any]],
    param_gen,
    placeholder_counter,
    bind_parameters,
    match,
):
    group = match.groupdict().get
    pt = group("param_type")
    p = group("param")
    if pt in {None, "value", "v"}:
        if isinstance(params, list):
            params.append(bind_parameters[p])
        else:
            params[p] = bind_parameters[p]
        return param_gen(p, next(placeholder_counter))  # type: ignore
    elif pt in {"raw", "r"}:
        return str(bind_parameters[p])
    elif pt in {"identifier", "i"}:
        return quote_ident_ansi(bind_parameters[p])
    elif pt in {"value*", "v*", "tuple", "t"}:
        placeholder = make_sequence_placeholder(
            params, param_gen, placeholder_counter, list(bind_parameters[p])
        )
        if pt in {"tuple", "t"}:
            return f"({placeholder})"
        return placeholder
    elif pt in {"tuple*", "t*"}:
        return ", ".join(
            f"({make_sequence_placeholder(params, param_gen, placeholder_counter, list(items))})"
            for items in bind_parameters[p]
        )
    else:
        raise ValueError(f"Unsupported param_type {pt}")


def make_sequence_placeholder(
    params: Union[List[Any], Dict[str, Any]],
    param_gen: Callable[[str, int], str],
    placeholder_counter: Iterator[int],
    items: List,
) -> str:
    """
    Return a placeholder for a sequence of parameters, in the format::

        ?, ?, ?, ...

    Or::

        :_1, :_2, :_3, ...

    Modify ``params`` in place to include the placeholders.
    """
    numbers = [next(placeholder_counter) for ix in range(len(items))]
    names = [f"_{n}" for n in numbers]
    if isinstance(params, list):
        params.extend(items)
    else:
        params.update(zip(names, items))
    return ", ".join(param_gen(name, c) for name, c in zip(names, numbers))


def starts_new_statement(metadata: Metadata) -> bool:
    return bool(metadata.name)


def parse_tokens(statement: sqlparse.sql.Statement) -> tuple[Metadata, Tokens]:
    """
    Parse out any metadata from an sqlparse statement
    Return a Metadata object and a new list of tokens with metadata removed
    """
    new_tokens = []
    metadata: Metadata = Metadata()
    for token in statement.tokens:
        if isinstance(token, sqlparse.sql.Comment) or (
            token.ttype and token.ttype[0] == "Comment"
        ):
            metadata.update(parse_comment_metadata(str(token)))
        else:
            new_tokens.append(token)
    return metadata, new_tokens


def parse_type_hints(imports: Sequence[str], type_hints: Sequence[str]) -> list[t.Any]:
    imports_str = "\n".join(imports)
    code = (
        f"{imports_str}\n"
        f"type_hints = [{', '.join(type_hints)}]"
    )
    _code = compile(code, "<string>", "exec")
    ns = {}
    try:
        exec(_code, ns)
    except NameError as e:
        raise NameError(
            f"{e.args[0]} (do you need to add `-- :import {e.name}`?)", name=e.name
        ) from e
    return ns["type_hints"]


@dataclasses.dataclass
class ParsedReturning:
    row_spec: list[mapobject] = dataclasses.field(default_factory=list)
    imports: list[str] = dataclasses.field(default_factory=list)
    joins: list[joinedload] = dataclasses.field(default_factory=list)
    key_columns: list[tuple[str, ...]] = dataclasses.field(default_factory=list)
    split_on: list[str] = dataclasses.field(default_factory=list)

    def __bool__(self):
        return bool(self.row_spec)


def parse_returning_metadata(
    imports: list[str] = [],
    returns: t.Optional[str] = None,
    joins: list[str] = [],
    key_columns: list[str] = [],
    split_on: list[str] = [],
) -> ParsedReturning:
    """
    Parse the query returning metadata into a ParsedReturning object,
    resolving imported symbols into live objects
    """
    result = ParsedReturning()
    imports.append("from embrace import mapobject")
    imports_str = "\n".join(imports)
    code = (
        f"{imports_str}\n"
        f'returns = {returns if returns and returns.strip() else "None"}'
    )
    ns = {}
    _code = compile(code, "<string>", "exec")
    try:
        exec(_code, ns)
    except NameError as e:
        raise NameError(
            f"{e.args[0]} (do you need to add `-- :import {e.name}`?)", name=e.name
        ) from e
    rs = ns["returns"]
    rs_origin = t.get_origin(rs)
    if rs is None:
        result.row_spec = []
    elif rs_origin is tuple:
        rs_args = t.get_args(rs)
        if rs_args == (Ellipsis,):
            result.row_spec = make_rowspec(
                tuple, split_on=[], key_columns=[], positional=False
            )
        elif Ellipsis in rs_args:
            raise ParseError(
                f"Invalid return annotation {returns}: tuples must be completely specified."
            )
        else:
            result.row_spec = make_rowspec(
                t.get_args(rs), split_on=[], key_columns=[], positional=False
            )
    elif rs_origin is None:
        result.row_spec = make_rowspec(
            rs, split_on=[], key_columns=[], positional=False
        )
    else:
        raise ParseError(
            f"Invalid return annotation {returns}: unsupported typing origin {rs_origin}"
        )

    result.joins = parse_joins(ns, joins)
    result.key_columns = [tuple(s.strip() for s in k.split(",")) for k in key_columns]
    result.split_on = split_on

    return result


def parse_joins(
    ns: dict[str, Any],
    joins: list[str],
    cardinality_pattern=re.compile(r"^(one|many)\s*(.*)$"),
) -> list[joinedload]:
    result: list[joinedload] = []
    for s in joins:
        if mo := cardinality_pattern.match(s):
            cardinality = mo.group(1)
            s = mo.group(2).strip()
        else:
            cardinality = "one"
            s = s.strip()
        lhs, rhs = re.split(r"\s*=\s*", s)
        try:
            lhs, lhs_attr = lhs.rsplit(".", 1)
        except ValueError:
            raise ParseError(
                f"{lhs!r} should be a dotted path in join expression {s!r}"
            )
        lhs_ob = load_join_symbol(ns, s, lhs)
        rhs_ob = load_join_symbol(ns, s, rhs)
        result.append(
            joinedload(
                lhs_ob,
                lhs_attr,
                rhs_ob,
                "1" if cardinality == "one" else "*",
            )
        )

    return result


def load_join_symbol(ns: dict[str, t.Any], joinexpr: str, dottedpath: str) -> t.Any:
    """
    Load a symbol from dict `ns` addressed by a dotted path
    """
    names = dottedpath.split(".")
    ob = None
    for name in names:
        if ob is None:
            next_ob = ns.get(name, name)
            if next_ob is name:
                if len(names) == 1:
                    return name
                raise ParseError(
                    f"name {name!r} is not defined in join expression {joinexpr!r}. "
                    f"Do you need to add ':import {name}'?"
                )
        else:
            try:
                next_ob = getattr(ob, name)
            except AttributeError:
                raise ParseError(
                    f"{type(ob)} object has no attribute {name!r} "
                    f"in join expression {joinexpr!r}"
                )
        ob = next_ob
    if ob is None:
        raise ParseError(f"Bad join expression {joinexpr!r}")
    return ob
