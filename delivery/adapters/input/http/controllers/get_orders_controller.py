import typing

from fastapi import APIRouter, Depends, status
from that_depends import Provide

from delivery.adapters.input.http.mappers.order_mapper import OrderMapper
from delivery.adapters.input.http.models.error import Error as HttpError
from delivery.adapters.input.http.models.order import Order
from delivery.core.application.queries.get_all_incomplete_orders import (
    GetAllIncompleteOrdersQuery,
    GetAllIncompleteOrdersQueryHandler,
)
from delivery.ioc import IOCContainer


router = APIRouter()


@router.get(
    "/orders/active",
    status_code=status.HTTP_200_OK,
    responses={
        "default": {"model": HttpError, "description": "Ошибка"},
    },
)
async def get_active_orders(
    handler: typing.Annotated[
        GetAllIncompleteOrdersQueryHandler,
        Depends(Provide[IOCContainer.get_all_incomplete_orders_handler]),
    ],
) -> list[Order]:
    query: typing.Final = GetAllIncompleteOrdersQuery()

    result: typing.Final = await handler.handle(query)

    if result.is_failure:
        error: typing.Final = result.get_error()
        raise Exception(f"Error: {error.code} - {error.message}")  # noqa: TRY002

    orders: typing.Final[list[Order]] = [OrderMapper.to_http(order_dto) for order_dto in result.get_value()]

    return orders
