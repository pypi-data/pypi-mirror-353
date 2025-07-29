import collections.abc
import typing as t
import inspect
from embrace.module import Module
from embrace.codegen import generate_module_source


def test_it_generates_type_signature():
    m = Module()
    m.add_query("foo", "-- :many\n-- :returns tuple[int, int]\nSELECT 1,2")
    s = generate_module_source(m)
    assert ") -> _C.Iterable[tuple[int, int]]" in s


def test_it_generates_type_with_mapobject():
    m = Module()
    m.add_query(
        "foo",
        "-- :one\n-- :from types import SimpleNamespace\n-- :returns mapobject(SimpleNamespace)\nSELECT 1,2",
    )
    s = generate_module_source(m)
    assert ") -> _0.SimpleNamespace" in s


def test_it_generates_type_with_mapobject_dataclass():
    # It is not possible to generate a full type signature as the dataclass is
    # generated dynamically after the cursor.description is populated
    m = Module()
    m.add_query(
        "foo",
        """-- :one\n-- :import typing, dataclasses\n-- :returns mapobject.dataclass([('owner', typing.Any), ('images', list[str])])""",
    )
    s = generate_module_source(m)
    assert ") -> _T.Any" in s


def test_it_adds_query_arguments():
    m = Module()
    m.add_query("foo", "SELECT :a, :b FROM :c")
    s = generate_module_source(m)
    assert "conn: _T.Optional[_ET.Connection], a: _T.Any, b: _T.Any, c: _T.Any" in s


def test_it_adds_query_arguments_with_type_hints():
    m = Module()
    m.add_query(
        "foo", "-- :import decimal\nSELECT :a:int, :b:decimal.Decimal FROM :c:str"
    )
    s = generate_module_source(m)
    assert "conn: _T.Optional[_ET.Connection], a: int, b: _0.Decimal, c: str" in s


def test_it_type_checks():
    m = Module()
    m.add_query("foo", "-- :returns tuple[int, str]\nSELECT 1, 'a'")
    s = generate_module_source(m)
    ns = {}
    exec(s, ns)
    query = ns["foo"]
    import inspect

    assert (
        inspect.signature(query.first).return_annotation == t.Optional[tuple[int, str]]
    )
    assert (
        inspect.signature(query.many).return_annotation
        == collections.abc.Iterable[tuple[int, str]]
    )
