import typing

from delivery.core.ports.courier_repository import CourierRepository
from delivery.libs.errs.error import Error
from delivery.libs.errs.result import Result
from .dto import CourierDto
from .handler import GetAllCouriersQueryHandler
from .query import GetAllCouriersQuery


if typing.TYPE_CHECKING:
    from uuid import UUID


class GetAllCouriersQueryHandlerImpl(GetAllCouriersQueryHandler):
    def __init__(self, courier_repository: CourierRepository) -> None:
        self._courier_repository = courier_repository

    async def handle(self, query: GetAllCouriersQuery) -> Result[list[CourierDto], Error]:  # noqa: ARG002
        couriers: typing.Final = await self._courier_repository.get_all_free()

        dto_list: typing.Final[list[CourierDto]] = [
            CourierDto(
                id=typing.cast("UUID", courier.id),
                name=courier.name,
                location_x=courier.location.x,
                location_y=courier.location.y,
            )
            for courier in couriers
        ]

        return Result.success(dto_list)
