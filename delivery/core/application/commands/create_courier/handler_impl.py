import typing
from uuid import UUID

from delivery.core.domain.model.courier.courier import Courier
from delivery.core.domain.model.kernel import Location
from delivery.core.ports.courier_repository import CourierRepository
from delivery.event_publisher import DefaultDomainEventPublisher
from delivery.libs.errs.error import Error
from delivery.libs.errs.result import Result
from .command import CreateCourierCommand
from .handler import CreateCourierCommandHandler


class CreateCourierCommandHandlerImpl(CreateCourierCommandHandler):
    def __init__(
        self,
        courier_repository: CourierRepository,
        domain_event_publisher: DefaultDomainEventPublisher,
    ) -> None:
        self._courier_repository = courier_repository
        self._domain_event_publisher = domain_event_publisher

    async def handle(self, command: CreateCourierCommand) -> Result[UUID, Error]:
        location_result: typing.Final = Location.create(1, 1)
        if location_result.is_failure:
            return Result.failure(location_result.get_error())

        courier_result: typing.Final = Courier.create(command.name, command.speed, location_result.get_value())
        if courier_result.is_failure:
            return Result.failure(courier_result.get_error())

        courier: typing.Final = courier_result.get_value()

        await self._courier_repository.add(courier)

        await self._domain_event_publisher.publish([courier])

        return Result.success(courier.id)
