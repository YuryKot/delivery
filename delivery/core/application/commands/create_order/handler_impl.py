import typing

from delivery.core.domain.model.order.order import Order
from delivery.core.ports.geo_location_client import GeoLocationClient
from delivery.core.ports.unit_of_work import DeliveryUnitOfWork
from delivery.libs.errs.error import Error
from delivery.libs.errs.result import UnitResult
from .command import CreateOrderCommand
from .handler import CreateOrderCommandHandler


class CreateOrderCommandHandlerImpl(CreateOrderCommandHandler):
    def __init__(
        self,
        geo_location_client: GeoLocationClient,
    ) -> None:
        self._geo_location_client = geo_location_client

    async def handle(self, command: CreateOrderCommand) -> UnitResult[Error]:
        location_result: typing.Final = await self._geo_location_client.get_location(command.address.street)
        if location_result.is_failure:
            return UnitResult.failure(location_result.get_error())

        order_result: typing.Final = Order.create(command.order_id, location_result.get_value(), command.volume)
        if order_result.is_failure:
            return UnitResult.failure(order_result.get_error())

        order: typing.Final = order_result.get_value()

        async with DeliveryUnitOfWork.start() as uow:
            await uow.order.add(order)
            await uow.domain_event_publisher.publish([order])

        return UnitResult.success()
