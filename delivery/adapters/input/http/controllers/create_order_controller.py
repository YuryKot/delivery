import typing

from fastapi import APIRouter, Depends, status
from fastapi.responses import JSONResponse

from delivery.adapters.input.http.models.error import Error as HttpError
from delivery.adapters.input.http.models.order import CreateOrderRequest, CreateOrderResponse
from delivery.core.application.commands.create_order import (
    CreateOrderCommand,
    CreateOrderCommandHandler,
)
from delivery.core.domain.model.kernel import Address, Volume
from delivery.libs.errs.error import Error


router = APIRouter()


@router.post(
    "/orders",
    response_model=CreateOrderResponse,
    status_code=status.HTTP_201_CREATED,
    responses={
        400: {"model": HttpError, "description": "Некорректные параметры запроса"},
        409: {"model": HttpError, "description": "Конфликт при создании заказа"},
        500: {"model": HttpError, "description": "Внутренняя ошибка сервиса"},
    },
)
async def create_order(
    request: CreateOrderRequest,
    handler: typing.Annotated[CreateOrderCommandHandler, Depends()],
) -> JSONResponse:
    address: typing.Final = Address.must_create(
        country=request.country,
        city=request.city,
        street=request.street,
        house=request.house,
        apartment=request.apartment,
    )
    volume: typing.Final = Volume.must_create(request.volume)

    command: typing.Final = CreateOrderCommand(
        order_id=request.order_id,
        address=address,
        volume=volume,
    )

    result: typing.Final = await handler.handle(command)

    if result.is_failure:
        error: typing.Final = result.get_error()
        http_status: typing.Final[int] = _map_error_to_status(error)
        return JSONResponse(
            status_code=http_status,
            content={"code": http_status, "message": error.message},
        )

    return JSONResponse(
        status_code=status.HTTP_201_CREATED,
        content={"orderId": str(request.order_id)},
    )


def _map_error_to_status(error: Error) -> int:
    code: typing.Final[str] = error.code.lower()
    if "null" in code or "empty" in code or "required" in code or "range" in code:
        return 400
    if "conflict" in code or "already" in code or "exists" in code:
        return 409
    return 500
