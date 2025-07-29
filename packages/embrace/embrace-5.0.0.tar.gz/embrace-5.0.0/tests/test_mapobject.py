from embrace.mapobject import mapobject
from embrace.mapobject import RowMapper
from embrace.mapobject import group_by_and_join
from embrace.mapobject import make_rowspec


class TestRowMapper:

    def test_get_split_points_by_split(self):
        rm = RowMapper([mapobject(tuple), mapobject(tuple, split="c")])
        rm.set_description(["a", "b", "c", "d"])  # type: ignore
        assert rm.get_split_points() == [slice(0, 2), slice(2, 4)]

    def test_get_split_points_by_count(self):
        rm = RowMapper([mapobject(tuple, column_count=3), mapobject(tuple)])
        rm.set_description(["a", "b", "c", "d"])  # type: ignore
        assert rm.get_split_points() == [slice(0, 3), slice(3, 4)]
