import typing

from delivery.core.domain.model.courier.courier import Courier
from delivery.core.domain.model.order.order import Order
from delivery.libs.errs.error import Error
from delivery.libs.errs.guard import Guard
from delivery.libs.errs.result import Result


class OrderDispatchDomainService:
    def dispatch_order(
        self,
        order: Order,
        couriers: list[Courier],
    ) -> Result[Courier, Error]:
        error: typing.Final = Guard.combine(
            Guard.against_null(order, "order"),
            Guard.against_null_or_empty_collection(couriers, "couriers"),
        )
        if error is not None:
            return Result.failure(error)

        suitable_couriers: typing.Final = [
            courier for courier in couriers if courier.can_take_order(order.volume.value)
        ]

        if not suitable_couriers:
            return Result.failure(
                Error.of(
                    "order.dispatch.no.suitable.courier",
                    f"No suitable courier found for order {order.id} with volume {order.volume.value}",
                )
            )

        courier_with_min_time: typing.Final = min(
            suitable_couriers,
            key=lambda courier: courier.calculate_time_to_location(order.location),
        )

        return Result.success(courier_with_min_time)
