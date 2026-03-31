import typing

from delivery.core.domain.service.order_dispatch_service import OrderDispatchDomainService
from delivery.core.ports.unit_of_work import DeliveryUnitOfWork
from delivery.libs.errs.error import Error
from delivery.libs.errs.result import UnitResult
from .command import AssignOrderToCourierCommand
from .handler import AssignOrderToCourierCommandHandler


if typing.TYPE_CHECKING:
    from uuid import UUID


class AssignOrderToCourierCommandHandlerImpl(AssignOrderToCourierCommandHandler):
    def __init__(
        self,
        order_dispatch_service: OrderDispatchDomainService,
    ) -> None:
        self._order_dispatch_service = order_dispatch_service

    async def handle(self, command: AssignOrderToCourierCommand) -> UnitResult[Error]:  # noqa: ARG002
        async with DeliveryUnitOfWork.start() as uow:
            order: typing.Final = await uow.order.get_first_by_status_created()
            if order is None:
                return UnitResult.success()

            free_couriers: typing.Final = await uow.courier.get_all_free()
            if not free_couriers:
                return UnitResult.failure(
                    Error.of(
                        "dispatch.no.free.couriers",
                        "No free couriers available for order assignment",
                    )
                )

            dispatch_result: typing.Final = self._order_dispatch_service.dispatch_order(order, free_couriers)
            if dispatch_result.is_failure:
                return UnitResult.failure(dispatch_result.get_error())

            best_courier: typing.Final = dispatch_result.get_value()

            take_result: typing.Final = best_courier.take_order(typing.cast("UUID", order.id), order.volume)
            if take_result.is_failure:
                return UnitResult.failure(take_result.get_error())

            assign_result: typing.Final = order.assign(typing.cast("UUID", best_courier.id))
            if assign_result.is_failure:
                return UnitResult.failure(assign_result.get_error())

            await uow.order.update(order)
            await uow.courier.update(best_courier)

            await uow.domain_event_publisher.publish([order])

        return UnitResult.success()
