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

import pytest
from embrace.parsing import parse_comment_metadata
from embrace.parsing import parse_returning_metadata
from embrace.parsing import Metadata
from embrace.parsing import compile_bind_parameters


def test_parse_comment_metadata():
    def test(comment, expected):
        assert parse_comment_metadata(comment) == expected

    test("--", Metadata())
    test("-- :name foo", Metadata(name="foo"))


def test_compile_bind_parameters():
    def test(qstyle, sql, bindparams, expected_sql, expected_params):
        compiled, params = compile_bind_parameters(qstyle, sql, bindparams)
        assert compiled == expected_sql
        assert params == expected_params

    # It replaces a positional param
    test("qmark", ":a", {"a": 1}, "?", (1,))

    with pytest.raises(KeyError):
        # raise exception if a named param is not supplied
        test("qmark", ":a", {}, ":a", ())

    # it ignores SQL casts
    test("qmark", "::int", {"int": 1}, "::int", ())

    # …and backslashes
    test("qmark", "\\:int", {"int": 1}, "\\:int", ())

    # it quotes ansi identifiers
    test("qmark", ":identifier:a", {"a": 1}, '"1"', ())

    # it escapes ansi identifiers
    test(
        "qmark",
        ":identifier:a",
        {"a": 'this is a "param"'},
        '"this is a ""param"""',
        (),
    )

    # passes through raw params
    test("qmark", ":raw:a", {"a": 1}, "1", ())

    # it compiles to numeric paramstyle
    test("numeric", ":a :b :b :a", {"b": 2, "a": 1}, ":1 :2 :3 :4", (1, 2, 2, 1))

    # it compiles to named paramstyle
    test(
        "named",
        ":a :b :b :a",
        {"b": 2, "a": 1},
        ":a :b :b :a",
        {"a": 1, "b": 2},
    )

    # it compiles mixed param types
    test("named", ":a :i:b", {"b": 2, "a": 1}, ':a "2"', {"a": 1})

    # it compiles values
    test("named", ":value:a", {"a": 1}, ":a", {"a": 1})

    # it compiles value lists
    test("named", ":v*:a", {"a": ["x", "y"]}, ":_1, :_2", {"_1": "x", "_2": "y"})
    test("qmark", ":v*:a", {"a": ["x", "y"]}, "?, ?", ("x", "y"))

    # it compiles tuples
    test("qmark", ":t:a", {"a": ("x", "y")}, "(?, ?)", ("x", "y"))

    # it compiles tuple-lists
    test(
        "qmark",
        ":t*:a",
        {"a": [("x", "y"), (1, 2)]},
        "(?, ?), (?, ?)",
        ("x", "y", 1, 2),
    )

    test(
        "named",
        ":tuple*:a",
        {"a": [("x", "y"), (1, 2)]},
        "(:_1, :_2), (:_3, :_4)",
        {"_1": "x", "_2": "y", "_3": 1, "_4": 2},
    )

    # it escapes percent signs
    test("format", ":a % :b", {"a": 3, "b": 2}, "%s %% %s", (3, 2))
    test(
        "pyformat",
        ":a % :b",
        {"a": 3, "b": 2},
        "%(a)s %% %(b)s",
        {"a": 3, "b": 2},
    )


class TestParseMetadata:

    def test_it_parses_returns(self):
        from embrace.mapobject import mapobject

        assert parse_returning_metadata(returns="tuple[str, int]").row_spec == [mapobject(str), mapobject(int)]

        assert parse_returning_metadata(returns="mapobject.dict(label='d')").row_spec == [mapobject(dict, label='d', join_as_dict=True)]

    def test_it_parses_joins(self):
        from embrace.mapobject import joinedload

        assert parse_returning_metadata(joins=["one Foo.x = Bar"]).joins == [joinedload("Foo", "x", "Bar", "1")]

    def test_it_parses_joins_with_import(self):
        from embrace.mapobject import joinedload
        import datetime

        assert parse_returning_metadata(
            imports=["import datetime"],
            joins=["one datetime.date.year = x"]
        ).joins == [joinedload(datetime.date, "year", "x", "1")]
