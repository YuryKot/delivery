import typing

import grpc  # type: ignore[import-untyped]
import structlog

from delivery.core.domain.model.kernel import Location
from delivery.core.ports.geo_location_client import GeoLocationClient
from delivery.libs.errs.error import Error
from delivery.libs.errs.result import Result
from . import geo_pb2, geo_pb2_grpc


logger = structlog.get_logger(__name__)


class GeoClientImpl(GeoLocationClient):
    def __init__(
        self,
        host: str,
        port: int,
        timeout: float = 5.0,
    ) -> None:
        self._channel = grpc.insecure_channel(f"{host}:{port}")
        self._stub = geo_pb2_grpc.GeoStub(self._channel)
        self._timeout = timeout

    async def get_location(self, street: str) -> Result[Location, Error]:
        try:
            request: typing.Final = geo_pb2.GetGeolocationRequest(street=street)  # type: ignore[attr-defined]
            response: typing.Final = self._stub.GetGeolocation(request, timeout=self._timeout)

            location_result: typing.Final = Location.create(response.location.x, response.location.y)
            if location_result.is_failure:
                error: typing.Final = location_result.get_error()
                logger.error(
                    "Invalid location from Geo service",
                    street=street,
                    error_code=error.code,
                    error_message=error.message,
                )
                return location_result

            logger.info(
                "Successfully received location from Geo service",
                street=street,
                x=response.location.x,
                y=response.location.y,
            )
            return Result.success(location_result.get_value())

        except grpc.RpcError as e:
            logger.exception(
                "gRPC error while getting location",
                street=street,
                error_code=e.code(),
                error_details=e.details(),
            )
            return Result.failure(Error.of("geo.service.rpc.error", f"gRPC error: {e.code()} - {e.details()}"))

        except Exception as e:
            logger.exception("Unexpected error while getting location", street=street)
            return Result.failure(Error.of("geo.service.unexpected.error", f"Unexpected error: {e!s}"))
