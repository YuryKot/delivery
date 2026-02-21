import typing
from uuid import UUID, uuid4

from delivery.libs.ddd.entity import BaseEntity
from delivery.libs.errs.error import Error
from delivery.libs.errs.guard import Guard
from delivery.libs.errs.result import Result, UnitResult


class StoragePlace(BaseEntity[UUID]):
    def __init__(
        self,
        id_: UUID,
        name: str,
        total_volume: int,
        order_id: UUID | None = None,
    ) -> None:
        super().__init__(id_)
        self._name = name
        self._total_volume = total_volume
        self._order_id = order_id

    @staticmethod
    def create(
        name: str,
        total_volume: int,
        order_id: UUID | None = None,
    ) -> Result["StoragePlace", Error]:
        err: typing.Final = Guard.combine(
            Guard.against_null_or_empty(name, "name"),
            Guard.against_less_or_equal(total_volume, 0, "total_volume"),
        )
        if err is not None:
            return Result.failure(err)

        storage_id: typing.Final = uuid4()
        return Result.success(StoragePlace(storage_id, name, total_volume, order_id))

    @staticmethod
    def must_create(
        name: str,
        total_volume: int,
        order_id: UUID | None = None,
    ) -> "StoragePlace":
        return StoragePlace.create(name, total_volume, order_id).get_value_or_throw()

    @property
    def name(self) -> str:
        return self._name

    @property
    def total_volume(self) -> int:
        return self._total_volume

    @property
    def order_id(self) -> UUID | None:
        return self._order_id

    def is_occupied(self) -> bool:
        return self._order_id is not None

    def can_store(self, order_volume: int) -> bool:
        return not self.is_occupied() and order_volume <= self._total_volume

    def store(self, order_id: UUID, order_volume: int) -> UnitResult[Error]:
        err: typing.Final = Guard.against_null_or_empty_uuid(order_id, "order_id")
        if err is not None:
            return UnitResult.failure(err)

        if self.is_occupied():
            return UnitResult.failure(
                Error.of(
                    "storage.place.already.occupied",
                    f"Storage place '{self._name}' already contains order {self._order_id}",
                )
            )

        if order_volume > self._total_volume:
            return UnitResult.failure(
                Error.of(
                    "storage.place.volume.exceeded",
                    f"Order volume {order_volume} exceeds storage place volume {self._total_volume}",
                )
            )

        self._order_id = order_id
        return UnitResult.success()

    def clear(self) -> UnitResult[Error]:
        if not self.is_occupied():
            return UnitResult.failure(
                Error.of(
                    "storage.place.already.empty",
                    f"Storage place '{self._name}' is already empty",
                )
            )

        self._order_id = None
        return UnitResult.success()

    def __repr__(self) -> str:
        order_status: typing.Final = f"order_id={self._order_id}" if self._order_id else "empty"
        return f"StoragePlace(id={self.id}, name='{self._name}', total_volume={self._total_volume}, {order_status})"
