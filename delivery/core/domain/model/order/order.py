import typing
from uuid import UUID

from delivery.core.domain.model.kernel import Location
from delivery.core.domain.model.order.order_status import OrderStatus
from delivery.libs.ddd.aggregate import Aggregate
from delivery.libs.errs.error import Error
from delivery.libs.errs.guard import Guard
from delivery.libs.errs.result import Result, UnitResult


class Order(Aggregate[UUID]):
    def __init__(
        self,
        id_: UUID,
        location: Location,
        volume: int,
        status: OrderStatus,
        courier_id: UUID | None = None,
    ) -> None:
        super().__init__(id_)
        self._location = location
        self._volume = volume
        self._status = status
        self._courier_id = courier_id

    @staticmethod
    def create(
        id_: UUID,
        location: Location,
        volume: int,
    ) -> Result["Order", Error]:
        if location is None:
            return Result.failure(Error.of("value.is.required", "location is required"))

        err: typing.Final = Guard.combine(
            Guard.against_null_or_empty_uuid(id_, "id"),
            Guard.against_less_or_equal(volume, 0, "volume"),
        )
        if err is not None:
            return Result.failure(err)

        order: typing.Final = Order(
            id_=id_,
            location=location,
            volume=volume,
            status=OrderStatus.CREATED,
            courier_id=None,
        )
        return Result.success(order)

    @staticmethod
    def must_create(
        id_: UUID,
        location: Location,
        volume: int,
    ) -> "Order":
        return Order.create(id_, location, volume).get_value_or_throw()

    @property
    def location(self) -> Location:
        return self._location

    @property
    def volume(self) -> int:
        return self._volume

    @property
    def status(self) -> OrderStatus:
        return self._status

    @property
    def courier_id(self) -> UUID | None:
        return self._courier_id

    def assign(self, courier_id: UUID) -> UnitResult[Error]:
        err: typing.Final = Guard.against_null_or_empty_uuid(courier_id, "courier_id")
        if err is not None:
            return UnitResult.failure(err)

        if self._status != OrderStatus.CREATED:
            return UnitResult.failure(
                Error.of(
                    "order.already.assigned",
                    f"Order {self.id} is already in status {self._status.value}",
                )
            )

        if not self._status.can_transition_to(OrderStatus.ASSIGNED):
            return UnitResult.failure(
                Error.of(
                    "order.invalid.status.transition",
                    f"Cannot transition from {self._status.value} to {OrderStatus.ASSIGNED.value}",
                )
            )

        self._courier_id = courier_id
        self._status = OrderStatus.ASSIGNED
        return UnitResult.success()

    def complete(self) -> UnitResult[Error]:
        if self._status != OrderStatus.ASSIGNED:
            return UnitResult.failure(
                Error.of(
                    "order.not.assigned",
                    f"Cannot complete order {self.id} in status {self._status.value}. Order must be assigned first.",
                )
            )

        if not self._status.can_transition_to(OrderStatus.COMPLETED):
            return UnitResult.failure(
                Error.of(
                    "order.invalid.status.transition",
                    f"Cannot transition from {self._status.value} to {OrderStatus.COMPLETED.value}",
                )
            )

        self._status = OrderStatus.COMPLETED
        return UnitResult.success()

    def __repr__(self) -> str:
        courier_info: typing.Final = f"courier_id={self._courier_id}" if self._courier_id else "unassigned"
        return (
            f"Order(id={self.id}, location={self._location}, "
            f"volume={self._volume}, status={self._status.value}, {courier_info})"
        )
