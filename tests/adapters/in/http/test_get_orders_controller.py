import typing
from unittest.mock import AsyncMock, MagicMock
from uuid import uuid4

import pytest

from delivery.adapters.input.http.controllers.get_orders_controller import get_active_orders
from delivery.core.application.queries.get_all_incomplete_orders.dto import IncompleteOrderDto
from delivery.libs.errs.error import Error
from delivery.libs.errs.result import Result


class TestGetOrdersController:
    @pytest.fixture
    def mock_handler(self) -> MagicMock:
        handler: typing.Final = MagicMock()
        handler.handle = AsyncMock()
        return handler

    @pytest.mark.anyio
    async def test_get_active_orders_success(
        self,
        mock_handler: MagicMock,
    ) -> None:
        orders_dto: typing.Final = [
            IncompleteOrderDto(
                id=uuid4(),
                location_x=5,
                location_y=5,
            ),
            IncompleteOrderDto(
                id=uuid4(),
                location_x=10,
                location_y=10,
            ),
        ]

        mock_handler.handle.return_value = Result.success(orders_dto)

        result: typing.Final = await get_active_orders(handler=mock_handler)

        assert isinstance(result, list)
        assert len(result) == 2
        mock_handler.handle.assert_called_once()

    @pytest.mark.anyio
    async def test_get_active_orders_handler_failure(
        self,
        mock_handler: MagicMock,
    ) -> None:

        mock_handler.handle.return_value = Result.failure(Error.of("db.error", "Database connection failed"))

        with pytest.raises(Exception, match="db.error"):
            await get_active_orders(handler=mock_handler)

        mock_handler.handle.assert_called_once()
