import typing
from uuid import UUID

from delivery.core.domain.model.courier.courier import Courier
from delivery.core.domain.model.kernel import Location
from delivery.core.ports.unit_of_work import DeliveryUnitOfWork
from delivery.libs.errs.error import Error
from delivery.libs.errs.result import Result
from .command import CreateCourierCommand
from .handler import CreateCourierCommandHandler


class CreateCourierCommandHandlerImpl(CreateCourierCommandHandler):
    async def handle(self, command: CreateCourierCommand) -> Result[UUID, Error]:
        location_result: typing.Final = Location.create(1, 1)
        if location_result.is_failure:
            return Result.failure(location_result.get_error())

        courier_result: typing.Final = Courier.create(command.name, command.speed, location_result.get_value())
        if courier_result.is_failure:
            return Result.failure(courier_result.get_error())

        courier: typing.Final = courier_result.get_value()

        async with DeliveryUnitOfWork.start() as uow:
            await uow.courier.add(courier)
            await uow.domain_event_publisher.publish([courier])

        courier_id: typing.Final = typing.cast("UUID", courier.id)
        return Result.success(courier_id)
