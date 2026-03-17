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


class Volume(ValueObject["Volume"]):
    _MIN_VALUE: typing.Final[int] = 1
    _MAX_VALUE: typing.Final[int] = 100

    def __init__(self, value: int) -> None:
        self._value = value

    @staticmethod
    def create(value: int) -> Result["Volume", Error]:
        err: typing.Final = Guard.against_out_of_range(value, Volume._MIN_VALUE, Volume._MAX_VALUE, "volume")
        if err is not None:
            return Result.failure(err)

        return Result.success(Volume(value))

    @staticmethod
    def must_create(value: int) -> "Volume":
        return Volume.create(value).get_value_or_throw()

    @property
    def value(self) -> int:
        return self._value

    def equality_components(self) -> typing.Iterable[object]:
        return [self._value]

    def __repr__(self) -> str:
        return f"Volume(value={self._value})"


class Address(ValueObject["Address"]):
    def __init__(
        self,
        country: str,
        city: str,
        street: str,
        house: str,
        apartment: str,
    ) -> None:
        self._country = country
        self._city = city
        self._street = street
        self._house = house
        self._apartment = apartment

    @staticmethod
    def create(
        country: str,
        city: str,
        street: str,
        house: str,
        apartment: str,
    ) -> Result["Address", Error]:
        err: typing.Final = Guard.combine(
            Guard.against_null_or_empty(country, "country"),
            Guard.against_null_or_empty(city, "city"),
            Guard.against_null_or_empty(street, "street"),
            Guard.against_null_or_empty(house, "house"),
            Guard.against_null_or_empty(apartment, "apartment"),
        )
        if err is not None:
            return Result.failure(err)

        return Result.success(Address(country, city, street, house, apartment))

    @staticmethod
    def must_create(
        country: str,
        city: str,
        street: str,
        house: str,
        apartment: str,
    ) -> "Address":
        return Address.create(country, city, street, house, apartment).get_value_or_throw()

    @property
    def country(self) -> str:
        return self._country

    @property
    def city(self) -> str:
        return self._city

    @property
    def street(self) -> str:
        return self._street

    @property
    def house(self) -> str:
        return self._house

    @property
    def apartment(self) -> str:
        return self._apartment

    def equality_components(self) -> typing.Iterable[object]:
        return [self._country, self._city, self._street, self._house, self._apartment]

    def __repr__(self) -> str:
        return (
            f"Address(country={self._country}, city={self._city}, "
            f"street={self._street}, house={self._house}, "
            f"apartment={self._apartment})"
        )
