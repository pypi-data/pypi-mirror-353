from collections.abc import Sequence, Mapping
import typing as t

Parameters = t.Union[Sequence[t.Any], Mapping[str, t.Any]]
Row = Sequence[t.Any]

CursorDescription = Sequence[
    #: name, type_code, display_size, internal_size, precision, scale, null_ok
    tuple[
        str,
        object,
        t.Optional[int],
        t.Optional[int],
        t.Optional[int],
        t.Optional[int],
        t.Optional[bool],
    ]
]


class Connection(t.Protocol):
    #: Optional extension
    messages: list[tuple[type, Exception]]

    #: Optional extension
    autocommit: bool

    #: Optional extension
    errorhandler: t.Optional[
        t.Callable[["Connection", "Cursor", t.Type[Exception], Exception], t.NoReturn]
    ]

    def close(self) -> None:
        ...

    def commit(self) -> None:
        ...

    def rollback(self) -> None:
        ...

    def cursor(self) -> None:
        ...


class Cursor(t.Protocol):
    description: t.Optional[CursorDescription]
    rowcount: int
    arraysize: int

    #: Optional extension
    rownumber: t.Optional[int]

    #: Optional extension
    connection: Connection

    #: Optional extension
    messages: list[tuple[type, Exception]]

    #: Optional extension
    lastrowid: t.Any

    #: Optional extension
    errorhandler: t.Optional[
        t.Callable[["Connection", "Cursor", t.Type[Exception], Exception], t.NoReturn]
    ]

    def callproc(
        self, procname: str, parameters: t.Optional[Sequence[t.Any]] = None
    ) -> None:
        "Optional extension"

    def close(self) -> None:
        ...

    def execute(
        self, operation: str, parameters: t.Optional[Parameters] = None
    ) -> None:
        ...

    def executemany(
        self, operation: str, seq_of_parameters: Sequence[Parameters]
    ) -> None:
        ...

    def fetchone(self) -> Row:
        ...

    def fetchmany(self, size: int = 1) -> Sequence[Row]:
        ...

    def fetchall(self) -> Sequence[Row]:
        ...

    def nextset(self) -> None:
        "Optional extension"

    def setinputsizes(self, sizes) -> None:
        ...

    def setoutputsize(self, size: int, column: t.Optional[int]) -> None:
        ...

    def scroll(self, value: int, mode: str = "relative") -> None:
        "Optional extension"

    def next(self) -> Row:
        "Optional extension"
        ...

    def __iter__(self) -> t.Iterator[Sequence[t.Any]]:
        "Optional extension"
        ...
