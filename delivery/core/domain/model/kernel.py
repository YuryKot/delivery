import typing

from delivery.libs.ddd.value_object import ValueObject
from delivery.libs.errs.error import Error
from delivery.libs.errs.guard import Guard
from delivery.libs.errs.result import Result


class Location(ValueObject["Location"]):
    _MIN_COORDINATE: typing.Final[int] = 1
    _MAX_COORDINATE: typing.Final[int] = 10

    def __init__(self, x: int, y: int) -> None:
        self._x = x
        self._y = y

    @staticmethod
    def create(x: int, y: int) -> Result["Location", Error]:
        err: typing.Final = Guard.combine(
            Guard.against_out_of_range(x, Location._MIN_COORDINATE, Location._MAX_COORDINATE, "x"),
            Guard.against_out_of_range(y, Location._MIN_COORDINATE, Location._MAX_COORDINATE, "y"),
        )
        if err is not None:
            return Result.failure(err)

        return Result.success(Location(x, y))

    @staticmethod
    def must_create(x: int, y: int) -> "Location":
        return Location.create(x, y).get_value_or_throw()

    @property
    def x(self) -> int:
        return self._x

    @property
    def y(self) -> int:
        return self._y

    def distance_to(self, other: "Location") -> int:
        return abs(self._x - other.x) + abs(self._y - other.y)

    def equality_components(self) -> typing.Iterable[object]:
        return [self._x, self._y]

    def __repr__(self) -> str:
        return f"Location(x={self._x}, y={self._y})"
