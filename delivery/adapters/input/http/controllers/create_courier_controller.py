import typing

from fastapi import APIRouter, Depends, status
from fastapi.responses import JSONResponse

from delivery.adapters.input.http.models.courier import CreateCourierResponse, NewCourier
from delivery.adapters.input.http.models.error import Error as HttpError
from delivery.core.application.commands.create_courier import (
    CreateCourierCommand,
    CreateCourierCommandHandler,
)
from delivery.libs.errs.error import Error


router = APIRouter()


@router.post(
    "/couriers",
    response_model=CreateCourierResponse,
    status_code=status.HTTP_201_CREATED,
    responses={
        400: {"model": HttpError, "description": "Некорректные параметры запроса"},
        409: {"model": HttpError, "description": "Конфликт при создании курьера"},
        500: {"model": HttpError, "description": "Внутренняя ошибка сервиса"},
    },
)
async def create_courier(
    request: NewCourier,
    handler: typing.Annotated[CreateCourierCommandHandler, Depends()],
) -> JSONResponse:
    command: typing.Final = CreateCourierCommand(
        name=request.name,
        speed=10,
    )

    result: typing.Final = await handler.handle(command)

    if result.is_failure:
        error: typing.Final = result.get_error()
        http_status: typing.Final[int] = _map_error_to_status(error)
        return JSONResponse(
            status_code=http_status,
            content={"code": http_status, "message": error.message},
        )

    courier_id: typing.Final = result.get_value()
    return JSONResponse(
        status_code=status.HTTP_201_CREATED,
        content={"courierId": str(courier_id)},
    )


def _map_error_to_status(error: Error) -> int:
    code: typing.Final[str] = error.code.lower()
    if "null" in code or "empty" in code or "required" in code or "range" in code:
        return 400
    if "conflict" in code or "already" in code or "exists" in code:
        return 409
    return 500
