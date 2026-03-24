import typing
from unittest.mock import AsyncMock, MagicMock
from uuid import UUID

import pytest

from delivery.adapters.input.http.controllers.get_couriers_controller import get_couriers
from delivery.core.application.queries.get_all_couriers.dto import CourierDto
from delivery.libs.errs.error import Error
from delivery.libs.errs.result import Result


class TestGetCouriersController:
    @pytest.fixture
    def mock_handler(self) -> MagicMock:
        handler: typing.Final = MagicMock()
        handler.handle = AsyncMock()
        return handler

    @pytest.mark.anyio
    async def test_get_couriers_success(
        self,
        mock_handler: MagicMock,
    ) -> None:
        couriers_dto: typing.Final = [
            CourierDto(
                id=UUID("00000000-0000-0000-0000-000000000001"),
                name="Иван",
                location_x=5,
                location_y=5,
            ),
            CourierDto(
                id=UUID("00000000-0000-0000-0000-000000000002"),
                name="Петр",
                location_x=10,
                location_y=10,
            ),
        ]

        mock_handler.handle.return_value = Result.success(couriers_dto)

        result: typing.Final = await get_couriers(handler=mock_handler)

        assert isinstance(result, list)
        assert len(result) == 2
        mock_handler.handle.assert_called_once()

    @pytest.mark.anyio
    async def test_get_couriers_handler_failure(
        self,
        mock_handler: MagicMock,
    ) -> None:

        mock_handler.handle.return_value = Result.failure(Error.of("db.error", "Database connection failed"))

        with pytest.raises(Exception, match="db.error"):
            await get_couriers(handler=mock_handler)

        mock_handler.handle.assert_called_once()
