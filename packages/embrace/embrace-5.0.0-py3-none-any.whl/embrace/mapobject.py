from collections.abc import Sequence
from collections import namedtuple
from functools import partial
from itertools import zip_longest
from pickle import dumps
from pickle import HIGHEST_PROTOCOL
import typing as t
import dataclasses

from .types import CursorDescription

T = t.TypeVar("T")


class NullObjectType:
    pass


NullObject = NullObjectType()
joinedload = namedtuple("joinedload", "target attr source cardinality")
column_indexes = namedtuple(
    "column_indexes", "target_idx target_attr source_idx cardinality join_as_dict"
)


@dataclasses.dataclass(frozen=True, eq=True)
class mapobject:
    mapped: t.Callable
    key: dataclasses.InitVar[t.Union[str, Sequence[str]]] = tuple()
    split: str = "id"
    positional: bool = False
    column_count: t.Optional[int] = None
    join_as_dict: bool = False
    key_columns: Sequence[str] = tuple()
    label: t.Any = None

    @staticmethod
    def passthrough_mapped(x: T) -> T:
        return x

    def __post_init__(self, key):
        if not self.key_columns:
            if isinstance(key, str):
                object.__setattr__(self, "key_columns", (key,))
            else:
                object.__setattr__(self, "key_columns", (tuple(key)))
        if self.label is None:
            object.__setattr__(self, "label", self.mapped)
        if self.mapped in {bytes, bool, int, float, str}:
            object.__setattr__(self, "positional", True)
            object.__setattr__(self, "positional", True)
            object.__setattr__(self, "column_count", 1)
        elif self.mapped is dict:
            object.__setattr__(self, "join_as_dict", True)

    @classmethod
    def dict(cls, mapped=dict, *args, **kwargs):
        kwargs["join_as_dict"] = True
        return cls(mapped, *args, **kwargs)

    @classmethod
    def passthrough(cls, mapped="ignore", *args, **kwargs):
        kwargs["column_count"] = 1
        kwargs["positional"] = True
        return cls(cls.passthrough_mapped, **kwargs)

    @classmethod
    def namedtuple(cls, *args, **kwargs):
        return cls(mapped=dynamicnamedtuple(), **kwargs)

    @classmethod
    def dataclass(
        cls,
        fields: Sequence[
            t.Union[
                str,
                tuple[str, t.Union[str, type]],
                tuple[str, t.Union[str, type], dataclasses.Field],
            ]
        ] = [],
        **kwargs: t.Any,
    ):
        """
        Return a mapper that stores values in a dataclass.

        By default field names are be inferred from the returned column names,
        and have a type of ``typing.Any``.

        :param fields:
            Additional fields to be appended after fields loaded from the
            database. This should be in the same format as expected by the
            stdlib :func:`dataclasses.make_dataclass` function.

            If a field has the same name as one of the returned
            columns, it will be used instead of autogenerating a field.

            If a field tuple does not contain a :class:`dataclasses.Field` item,
            the value ``dataclasses.field(default=None)`` will be used.
            Additional fields are not populated during data loading so
            must have a default or default_factory specified.

        :param kwargs:
            Keyword arguments corresponding to :class:`mapobject` fields will be
            passed through to the constructor (eg ``split``, ``label``, etc).
            Other arguments will be taken as additional field names, and
            specified as either a simple name-type mapping::

                mapobject.dataclass(foo=list[str]|None)

            or as a tuple of ``(type, Field)``::

                mapobject.dataclass(
                    foo=(list[str], dataclasses.field(default_factory=list))
                )
        """
        mapobject_fields = {f.name for f in dataclasses.fields(cls)}
        field_dict = {item[0]: item for item in fields}
        field_dict.update(
            (name, (name,) + (item if isinstance(item, tuple) else (item,)))
            for name, item in kwargs.items()
            if name not in mapobject_fields
        )
        mapobject_kwargs = {k: v for k, v in kwargs.items() if k in mapobject_fields}

        return cls(mapped=dynamicdataclass(field_dict), **mapobject_kwargs)


class dynamicnamedtuple:

    nt = None

    def __call__(self, **kwargs):
        nt = self.nt
        if nt is None:
            nt = self.nt = namedtuple(  # type: ignore
                f"mapobject_namedtuple_{id(self)}", tuple(kwargs)
            )
        return self.nt(**kwargs)  # type: ignore


class dynamicdataclass:

    datacls = None

    def __init__(self, field_dict):
        self.field_dict = field_dict

    def __call__(self, **kwargs):

        datacls = self.datacls
        if datacls is None:
            dbfields = [self.field_dict.pop(k, k) for k in kwargs]
            additionalfields = []
            for item in self.field_dict.values():
                if isinstance(item, str):
                    item = (item,)
                if len(item) < 3:
                    item = item + (dataclasses.field(default=None),)
                additionalfields.append(item)
            datacls = self.datacls = dataclasses.make_dataclass(
                f"mapobject_dataclass_{id(self)}",
                dbfields + additionalfields,
            )
        return datacls(**kwargs)


def make_rowspec(
    row_spec: t.Union[
        "mapobject", t.Callable, Sequence[t.Union["mapobject", t.Callable]]
    ],
    split_on: Sequence[str],
    key_columns: Sequence[tuple[str, ...]],
    positional: bool,
) -> list["mapobject"]:
    """
    Standardize a row_spec into a standardized sequence of mapobjects.
    :param row_spec:
        The row_spec as provided to Query.returning.
        This could be a single mapobject (eg ``mapobject.dict()``),
        a callable (eg ``dict``), or a sequence mixing the two styles.
    :param split_on:
        A sequence of column names at which to split mapped objects
    :param key_columns:
        A sequence of column name tuples uniquely identifying a
        mapped object.
    """
    if not isinstance(row_spec, Sequence):
        row_spec = (row_spec,)

    if split_on and any(isinstance(i, mapobject) for i in row_spec):
        raise TypeError("Cannot combine mapobject with split_on")

    result = []
    for ix, item in enumerate(row_spec):
        if not isinstance(item, mapobject):
            item = mapobject(
                mapped=item,
                positional=positional,
                split=(split_on[ix - 1] if 0 < ix < len(split_on) - 1 else "id"),
                key_columns=(key_columns[ix] if ix < len(key_columns) else []),
            )

        result.append(item)
    return result


@dataclasses.dataclass
class RowMapper:
    """
    Model the properties required to map a query's output (cursor description +
    row tuples) to the configured return type
    """

    row_spec: list[mapobject] = dataclasses.field(default_factory=list)
    imports: list[str] = dataclasses.field(default_factory=list)
    joins: t.Sequence[joinedload] = dataclasses.field(default_factory=list)
    key_columns: list[tuple[str, ...]] = dataclasses.field(default_factory=list)
    split_on: list[str] = dataclasses.field(default_factory=list)

    split_points: list[slice] = dataclasses.field(default_factory=list)
    is_multi: bool = False
    column_names: t.Optional[list[str]] = None
    mapped_column_names: t.Optional[list[tuple[str, ...]]] = None

    def __post_init__(self):
        self.is_multi = len(self.row_spec) > 1

    def set_description(self, description: CursorDescription):
        self.column_names = [d[0] for d in description]
        if self.is_multi:
            sp = self.get_split_points()
            self.split_points = sp
            self.mapped_column_names = [tuple(self.column_names[s]) for s in sp]
        else:
            self.mapped_column_names = [tuple(self.column_names)]

    def make_row_mapper(self) -> t.Callable[
        [t.Iterable[tuple]], t.Iterable[t.Any]
    ]:
        maker: t.Optional[t.Callable] = None
        grouper: t.Optional[t.Callable] = None
        if self.column_names is None:
            raise AssertionError("set_description must be called first")

        if self.joins:
            if not self.is_multi:
                raise TypeError(
                    "joins may only be set when there are multiple return types"
                )
            grouper = partial(
                group_by_and_join, self.mapped_column_names, self.row_spec, self.joins
            )

        else:
            maker = make_object_maker(self.mapped_column_names, self.row_spec)

        return partial(self._maprows, grouper, maker)

    def get_split_points(self) -> list[slice]:
        pos = 0
        result = []
        if self.column_names is None:
            raise ValueError(f"{self}.column_names has not been set")

        for curr_mo, next_mo in zip_longest(self.row_spec, self.row_spec[1:]):
            if curr_mo.column_count:
                pos_ = pos + curr_mo.column_count
            elif next_mo:
                try:
                    pos_ = self.column_names.index(next_mo.split, pos + 1)
                except ValueError as e:
                    raise ValueError(
                        f"split_on column {next_mo.split!r} for {next_mo} not found: "
                        f" (columns remaining are {self.column_names[pos + 1:]})"
                    ) from e
            else:
                pos_ = len(self.column_names)
            result.append(slice(pos, pos_))
            pos = pos_
        return result

    def _maprows(self, grouper, maker, rows) -> t.Iterable[t.Any]:
        if not self.is_multi:
            object_rows = rows
        else:
            object_rows = ([row[s] for s in self.split_points] for row in rows)
        if self.is_multi:
            if grouper:
                return grouper(object_rows)
            else:
                return (tuple(map(maker, r)) for r in object_rows)
        else:
            return map(maker, object_rows)


def group_by_and_join(
    mapped_column_names: list[tuple[str, ...]],
    row_spec: list[mapobject],
    join_spec: Sequence[joinedload],
    object_rows: t.Iterable[list[tuple]],
    key_columns: t.Optional[list[tuple[str]]] = None,
    _marker=object(),
):
    make_object = make_object_maker(mapped_column_names, row_spec)
    indexed_joins = translate_to_column_indexes(row_spec, join_spec)
    join_source_columns = {c.source_idx for c in indexed_joins}

    last = [_marker] * len(row_spec)

    # Mapping of <column group index>: <currently loaded object>
    cur: dict[int, t.Any] = {}

    # List of column group indexes without backlinks: these are the top-level
    # objects we want to return
    return_columns = [n for n in range(len(row_spec)) if n not in join_source_columns]
    single_column = return_columns[0] if len(return_columns) == 1 else None
    items = None

    multi_join_targets = [c.target_idx for c in indexed_joins if c.cardinality == "*"]
    seen: set[tuple[int, int]] = set()
    for irow, items in enumerate(object_rows):
        # When all columns change, emit a new object row (or single item)
        if irow > 0 and all(items[ix] != last[ix] for ix in multi_join_targets):
            if single_column is not None:
                yield cur[0]
            else:
                yield tuple(cur[ix] for ix in return_columns)
            seen.clear()

        # Create objects from column data
        for column_index, item in enumerate(items):
            if column_index in join_source_columns:
                if all(v is None for v in item):
                    cur[column_index] = make_object(NullObject)
                    continue
            ob = make_object(item)
            cur[column_index] = ob

        # Populate joins
        for t_idx, attr, s_idx, cardinality, join_as_dict in indexed_joins:
            ob = cur[s_idx]
            ob_key = (s_idx, id(ob))
            if ob_key in seen:
                continue

            dest = cur[t_idx]
            if dest is None:
                continue
            if cardinality == "*":
                if join_as_dict:
                    if attr in dest:
                        attrib = dest[attr]
                    else:
                        attrib = _marker
                else:
                    attrib = getattr(dest, attr, _marker)
                if attrib is _marker:
                    attrib = []
                    if join_as_dict:
                        dest[attr] = attrib
                    else:
                        setattr(dest, attr, attrib)
                if ob is not None:
                    attrib.append(ob)  # type: ignore
            else:
                if join_as_dict:
                    dest[attr] = ob
                else:
                    setattr(dest, attr, ob)
            seen.add(ob_key)

        last = items

    if items:
        if single_column is not None:
            yield cur[single_column]
        else:
            rv: list[t.Any] = []
            append = rv.append
            for ix in return_columns:
                if ix in cur:
                    append(cur[ix])
                else:
                    append(make_object(items[ix]))
            yield tuple(rv)


def translate_to_column_indexes(
    row_spec: list[mapobject], join_spec: Sequence[joinedload]
) -> list[column_indexes]:
    """
    :return: a list of tuples, one per join
    """
    row_spec_indexes = {c.label: ix for ix, c in enumerate(row_spec)}

    def map_column(col: t.Any) -> int:
        if isinstance(col, int):
            return col
        return row_spec_indexes[col]

    result = []
    for j in join_spec:
        t_col = map_column(j.target)
        s_col = map_column(j.source)
        if t_col >= len(row_spec):
            raise ValueError(
                f"Target index {t_col} in join {j} exceeds number of mapped objects"
            )
        if s_col >= len(row_spec):
            raise ValueError(
                f"Source index {s_col} in join {j} exceeds number of mapped objects"
            )
        result.append(
            column_indexes(
                t_col, j.attr, s_col, j.cardinality, row_spec[t_col].join_as_dict
            )
        )
    return result


def make_object_maker(
    mapped_column_names: list[tuple[str, ...]],
    row_spec: list[t.Any],
) -> t.Callable[[t.Union[NullObjectType, tuple]], t.Any]:
    """
    Return a function that constructs the target type from a group of columns.

    The returned function will cache objects (the same input returns the
    same object) so that object identity may be relied on within the scope of a
    single query.
    """

    key_column_positions: list[list[int]] = []
    row_spec_cols = list(zip(row_spec, mapped_column_names))
    for mo, item_column_names in row_spec_cols:
        key_column_positions.append([])
        for c in mo.key_columns:
            try:
                key_column_positions[-1].append(item_column_names.index(c))
            except ValueError as e:
                import pprint

                mapped_columns_dump = {m.mapped: c for m, c in row_spec_cols}
                raise ValueError(
                    f"{c!r} specified in key_columns does not exist "
                    f"in the returned columns for {mo.mapped!r}. \n"
                    f"Mapped columns are: \n{pprint.pformat(mapped_columns_dump)}"
                ) from e

    def _object_maker():
        object_cache: dict[t.Any, t.Any] = {}
        ob = None
        itemcount = len(row_spec)

        # When loading multiple objects, ensure that proximate items loaded
        # with identical values map to the same object. This makes it possible
        # for joined loads to do the right thing, even if key_columns is not
        # set.
        row_cache: dict[t.Union[Sequence[t.Any], tuple[int, t.Any]], t.Any] = {}
        use_row_cache = len(row_spec) > 1
        mapping_items: list[tuple[t.Any, t.Any, bool, t.Optional[bool]]] = [
            (m.mapped, m.key_columns, m.positional, None) for m in row_spec
        ]

        i = -1
        rows_since_cache_flush = 0
        cache_hit_this_row = False
        cache_as_pickle_cols = {ix: False for ix in range(itemcount)}
        pickle = partial(dumps, protocol=HIGHEST_PROTOCOL)

        while True:
            data = yield ob
            i = (i + 1) % itemcount
            cache_as_pickle = cache_as_pickle_cols[i]

            # Clear the row_cache once we find a full row with no cache hits.
            if i == 0 and row_cache and not cache_hit_this_row:
                cache_hit_this_row = False
                if rows_since_cache_flush < 2:
                    rows_since_cache_flush += 1
                else:
                    row_cache.clear()
                    rows_since_cache_flush = 0

            if data is NullObject:
                ob = None
                continue

            mapped, key_columns, positional, passthrough = mapping_items[i]
            if passthrough is None:
                passthrough = (
                    len(data) == 1
                    and isinstance(mapped, type)
                    and isinstance(data[0], mapped)
                )
                mapping_items[i] = (mapped, key_columns, positional, passthrough)
            if passthrough:
                ob = data[0]
            elif key_columns:
                key = (i, tuple(data[x] for x in key_column_positions[i]))
                if key in object_cache:
                    cache_hit_this_row = True
                    ob = object_cache[key]
                else:
                    ob = object_cache[key] = (
                        mapped(*data)
                        if positional
                        else mapped(**dict(zip(mapped_column_names[i], data)))
                    )
            elif use_row_cache:
                cache_key = pickle((i, data)) if cache_as_pickle else (i, data)
                try:
                    cache_hit = cache_key in row_cache
                except TypeError:
                    if cache_as_pickle:
                        raise
                    # data may contain unhashable types (eg postgresql ARRAY
                    # types), in which case a TypeError is thrown. Work around
                    # this by allowing keys for this column to be pickled.
                    cache_as_pickle_cols[i] = cache_as_pickle = True
                    cache_key = pickle(cache_key)
                    cache_hit = cache_key in row_cache

                if cache_hit:
                    cache_hit_this_row = True
                    ob = row_cache[cache_key]
                else:
                    ob = (
                        mapped(*data)
                        if positional
                        else mapped(**dict(zip(mapped_column_names[i], data)))
                    )
                    row_cache[cache_key] = ob
            else:
                ob = (
                    mapped(*data)
                    if positional
                    else mapped(**dict(zip(mapped_column_names[i], data)))
                )

    func = _object_maker()
    next(func)
    return func.send
