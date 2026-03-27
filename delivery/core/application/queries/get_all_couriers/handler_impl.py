import typing

import sqlalchemy
import sqlalchemy.ext.asyncio as sa_async

from delivery.database.models import CourierModel
from delivery.libs.errs.error import Error
from delivery.libs.errs.result import Result
from .dto import CourierDto
from .handler import GetAllCouriersQueryHandler
from .query import GetAllCouriersQuery


class GetAllCouriersQueryHandlerImpl(GetAllCouriersQueryHandler):
    def __init__(self, session: sa_async.AsyncSession) -> None:
        self._session = session

    async def handle(self, query: GetAllCouriersQuery) -> Result[list[CourierDto], Error]:  # noqa: ARG002
        stmt: typing.Final = sqlalchemy.select(CourierModel)

        result: typing.Final = await self._session.execute(stmt)
        courier_models: typing.Final = result.scalars().unique().all()

        dto_list: typing.Final[list[CourierDto]] = [
            CourierDto(
                id=courier_model.id,
                name=courier_model.name,
                location_x=courier_model.location_x,
                location_y=courier_model.location_y,
            )
            for courier_model in courier_models
        ]

        return Result.success(dto_list)
