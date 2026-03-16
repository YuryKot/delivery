import typing

import sqlalchemy
import sqlalchemy.ext.asyncio as sa_async

from delivery.database.models import OrderModel
from delivery.libs.errs.error import Error
from delivery.libs.errs.result import Result
from .dto import IncompleteOrderDto
from .handler import GetAllIncompleteOrdersQueryHandler
from .query import GetAllIncompleteOrdersQuery


class GetAllIncompleteOrdersQueryHandlerImpl(GetAllIncompleteOrdersQueryHandler):
    def __init__(self, session: sa_async.AsyncSession) -> None:
        self._session = session

    async def handle(self, query: GetAllIncompleteOrdersQuery) -> Result[list[IncompleteOrderDto], Error]:  # noqa: ARG002
        stmt: typing.Final = sqlalchemy.select(OrderModel).where(OrderModel.status.in_(["Created", "Assigned"]))

        result: typing.Final = await self._session.execute(stmt)
        order_models: typing.Final = result.scalars().unique().all()

        dto_list: typing.Final[list[IncompleteOrderDto]] = [
            IncompleteOrderDto(
                id=order_model.id,
                location_x=order_model.location_x,
                location_y=order_model.location_y,
            )
            for order_model in order_models
        ]

        return Result.success(dto_list)
