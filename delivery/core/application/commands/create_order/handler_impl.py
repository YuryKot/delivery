import random
import typing

from delivery.core.domain.model.kernel import Location
from delivery.core.domain.model.order.order import Order
from delivery.core.ports.courier_repository import CourierRepository
from delivery.core.ports.order_repository import OrderRepository
from delivery.event_publisher import DefaultDomainEventPublisher
from delivery.libs.errs.error import Error
from delivery.libs.errs.result import UnitResult
from .command import CreateOrderCommand
from .handler import CreateOrderCommandHandler


class CreateOrderCommandHandlerImpl(CreateOrderCommandHandler):
    def __init__(
        self,
        order_repository: OrderRepository,
        courier_repository: CourierRepository,
        domain_event_publisher: DefaultDomainEventPublisher,
    ) -> None:
        self._order_repository = order_repository
        self._courier_repository = courier_repository
        self._domain_event_publisher = domain_event_publisher

    async def handle(self, command: CreateOrderCommand) -> UnitResult[Error]:
        random_x: typing.Final = random.randint(1, 10)  # noqa: S311
        random_y: typing.Final = random.randint(1, 10)  # noqa: S311
        location_result: typing.Final = Location.create(random_x, random_y)
        if location_result.is_failure:
            return UnitResult.failure(location_result.get_error())

        order_result: typing.Final = Order.create(command.order_id, location_result.get_value(), command.volume)
        if order_result.is_failure:
            return UnitResult.failure(order_result.get_error())

        order: typing.Final = order_result.get_value()

        await self._order_repository.add(order)

        await self._domain_event_publisher.publish([order])

        return UnitResult.success()
