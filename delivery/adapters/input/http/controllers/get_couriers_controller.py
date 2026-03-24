import typing

from fastapi import APIRouter, Depends, status
from that_depends import Provide

from delivery.adapters.input.http.mappers.courier_mapper import CourierMapper
from delivery.adapters.input.http.models.courier import Courier
from delivery.adapters.input.http.models.error import Error as HttpError
from delivery.core.application.queries.get_all_couriers import (
    GetAllCouriersQuery,
    GetAllCouriersQueryHandler,
)
from delivery.ioc import IOCContainer


router = APIRouter()


@router.get(
    "/couriers",
    status_code=status.HTTP_200_OK,
    responses={
        "default": {"model": HttpError, "description": "Ошибка"},
    },
)
async def get_couriers(
    handler: typing.Annotated[
        GetAllCouriersQueryHandler,
        Depends(Provide[IOCContainer.get_all_couriers_handler]),
    ],
) -> list[Courier]:
    query: typing.Final = GetAllCouriersQuery()

    result: typing.Final = await handler.handle(query)

    if result.is_failure:
        error: typing.Final = result.get_error()
        raise Exception(f"Error: {error.code} - {error.message}")  # noqa: TRY002

    couriers: typing.Final[list[Courier]] = [CourierMapper.to_http(courier_dto) for courier_dto in result.get_value()]

    return couriers
