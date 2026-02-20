import fastapi
from fastapi.responses import JSONResponse
from starlette import status

from delivery.libs.errs import DomainInvariantException


async def domain_invariant_exception_handler(request: fastapi.Request, exc: DomainInvariantException) -> JSONResponse:
    return JSONResponse(
        status_code=status.HTTP_400_BAD_REQUEST,
        content={"error": {"code": exc.error.code, "message": exc.error.message}},
    )


async def general_exception_handler(request: fastapi.Request, exc: Exception) -> JSONResponse:
    return JSONResponse(
        status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
        content={"error": {"code": "internal.server.error", "message": "Internal server error"}},
    )


def register_exception_handlers(app: fastapi.FastAPI) -> None:
    app.add_exception_handler(DomainInvariantException, domain_invariant_exception_handler)  # type: ignore[arg-type]
    app.add_exception_handler(Exception, general_exception_handler)
