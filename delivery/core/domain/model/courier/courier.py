import typing
from uuid import UUID, uuid4

from delivery.core.domain.model.courier.storage_place import StoragePlace
from delivery.core.domain.model.kernel import Location
from delivery.libs.ddd.aggregate import Aggregate
from delivery.libs.errs.error import Error
from delivery.libs.errs.guard import Guard
from delivery.libs.errs.result import Result, UnitResult


class Courier(Aggregate[UUID]):
    _DEFAULT_STORAGE_NAME: typing.Final[str] = "Сумка"
    _DEFAULT_STORAGE_VOLUME: typing.Final[int] = 10

    def __init__(
        self,
        id_: UUID,
        name: str,
        speed: int,
        location: Location,
        storage_places: list[StoragePlace],
    ) -> None:
        super().__init__(id_)
        self._name = name
        self._speed = speed
        self._location = location
        self._storage_places = storage_places

    @staticmethod
    def create(
        name: str,
        speed: int,
        location: Location,
    ) -> Result["Courier", Error]:
        if location is None:
            return Result.failure(Error.of("value.is.required", "location is required"))

        err: typing.Final = Guard.combine(
            Guard.against_null_or_empty(name, "name"),
            Guard.against_less_or_equal(speed, 0, "speed"),
        )
        if err is not None:
            return Result.failure(err)

        default_storage: typing.Final = StoragePlace.must_create(
            Courier._DEFAULT_STORAGE_NAME,
            Courier._DEFAULT_STORAGE_VOLUME,
        )

        courier_id: typing.Final = uuid4()
        courier: typing.Final = Courier(
            id_=courier_id,
            name=name,
            speed=speed,
            location=location,
            storage_places=[default_storage],
        )
        return Result.success(courier)

    @staticmethod
    def must_create(
        name: str,
        speed: int,
        location: Location,
    ) -> "Courier":
        return Courier.create(name, speed, location).get_value_or_throw()

    @property
    def name(self) -> str:
        return self._name

    @property
    def speed(self) -> int:
        return self._speed

    @property
    def location(self) -> Location:
        return self._location

    @property
    def storage_places(self) -> list[StoragePlace]:
        return self._storage_places.copy()

    def add_storage_place(self, name: str, volume: int) -> UnitResult[Error]:
        storage_result: typing.Final = StoragePlace.create(name, volume)
        if storage_result.is_failure:
            return UnitResult.failure(storage_result.get_error())

        self._storage_places.append(storage_result.get_value())
        return UnitResult.success()

    def can_take_order(self, order_volume: int) -> bool:
        return any(place.can_store(order_volume) for place in self._storage_places)

    def take_order(self, order_id: UUID, order_volume: int) -> UnitResult[Error]:
        err: typing.Final = Guard.combine(
            Guard.against_null_or_empty_uuid(order_id, "order_id"),
            Guard.against_less_or_equal(order_volume, 0, "order_volume"),
        )
        if err is not None:
            return UnitResult.failure(err)

        suitable_places: typing.Final = [place for place in self._storage_places if place.can_store(order_volume)]

        if not suitable_places:
            return UnitResult.failure(
                Error.of(
                    "courier.no.available.storage",
                    f"Courier {self._name} has no available storage for order volume {order_volume}",
                )
            )

        best_place: typing.Final = min(suitable_places, key=lambda p: p.total_volume)

        store_result: typing.Final = best_place.store(order_id, order_volume)
        if store_result.is_failure:
            return store_result

        return UnitResult.success()

    def complete_order(self, order_id: UUID) -> UnitResult[Error]:
        err: typing.Final = Guard.against_null_or_empty_uuid(order_id, "order_id")
        if err is not None:
            return UnitResult.failure(err)

        for place in self._storage_places:
            if place.order_id == order_id:
                clear_result = place.clear()
                if clear_result.is_failure:
                    return clear_result
                return UnitResult.success()

        return UnitResult.failure(
            Error.of(
                "courier.order.not.found",
                f"Order {order_id} not found in courier {self._name} storage",
            )
        )

    def calculate_time_to_location(self, target: Location) -> int:
        distance: typing.Final = self._location.distance_to(target)
        steps: typing.Final = (distance + self._speed - 1) // self._speed
        return steps

    def move(self, target: Location) -> UnitResult[Error]:
        if target is None:
            return UnitResult.failure(Error.of("value.is.required", "target is required"))

        dif_x: typing.Final = target.x - self._location.x
        dif_y: typing.Final = target.y - self._location.y
        cruising_range: int = self._speed

        move_x: typing.Final = max(-cruising_range, min(dif_x, cruising_range))
        cruising_range -= abs(move_x)

        move_y: typing.Final = max(-cruising_range, min(dif_y, cruising_range))

        new_location_result: typing.Final = Location.create(
            self._location.x + move_x,
            self._location.y + move_y,
        )

        if new_location_result.is_failure:
            return UnitResult.failure(new_location_result.get_error())

        self._location = new_location_result.get_value()
        return UnitResult.success()

    def __repr__(self) -> str:
        occupied_count: typing.Final = sum(1 for p in self._storage_places if p.is_occupied())
        return (
            f"Courier(id={self.id}, name='{self._name}', speed={self._speed}, "
            f"location={self._location}, storage_places={len(self._storage_places)}, "
            f"occupied={occupied_count})"
        )
