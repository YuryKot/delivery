import typing

from delivery.core.domain.model.courier.courier import Courier
from delivery.core.domain.model.order.order import Order
from delivery.core.ports.unit_of_work import DeliveryUnitOfWork
from delivery.libs.errs.error import Error
from delivery.libs.errs.result import UnitResult
from .command import MoveCouriersCommand
from .handler import MoveCouriersCommandHandler


if typing.TYPE_CHECKING:
    from uuid import UUID


class MoveCouriersCommandHandlerImpl(MoveCouriersCommandHandler):
    async def handle(self, command: MoveCouriersCommand) -> UnitResult[Error]:  # noqa: C901, ARG002
        async with DeliveryUnitOfWork.start() as uow:
            assigned_orders: typing.Final = await uow.order.get_all_assigned()
            if not assigned_orders:
                return UnitResult.success()

            modified_aggregates: typing.Final[list[Order | Courier]] = []
            for order in assigned_orders:
                if order.courier_id is None:
                    continue

                courier = await uow.courier.get_by_id(order.courier_id)
                if courier is None:
                    continue

                move_result = courier.move(order.location)
                if move_result.is_failure:
                    return UnitResult.failure(move_result.get_error())

                if courier.location == order.location:
                    complete_result = order.complete()
                    if complete_result.is_failure:
                        return UnitResult.failure(complete_result.get_error())

                    clear_result = courier.complete_order(typing.cast("UUID", order.id))
                    if clear_result.is_failure:
                        return UnitResult.failure(clear_result.get_error())

                    modified_aggregates.append(order)

                modified_aggregates.append(courier)

            for aggregate in modified_aggregates:
                if isinstance(aggregate, Order):
                    await uow.order.update(aggregate)
                elif isinstance(aggregate, Courier):
                    await uow.courier.update(aggregate)

            await uow.domain_event_publisher.publish(modified_aggregates)

        return UnitResult.success()
