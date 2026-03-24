import typing
from unittest.mock import AsyncMock, MagicMock
from uuid import uuid4

import pytest

from delivery.adapters.input.http.controllers.create_order_controller import create_order
from delivery.libs.errs.error import Error
from delivery.libs.errs.result import UnitResult


class TestCreateOrderController:
    @pytest.fixture
    def mock_handler(self) -> MagicMock:
        handler: typing.Final = MagicMock()
        handler.handle = AsyncMock()
        return handler

    @pytest.mark.anyio
    async def test_create_order_success(
        self,
        mock_handler: MagicMock,
    ) -> None:
        order_id: typing.Final = uuid4()
        request_data: typing.Final = {
            "order_id": str(order_id),
            "country": "Россия",
            "city": "Москва",
            "street": "Тверская",
            "house": "1",
            "apartment": "1",
            "volume": 10,
        }

        mock_handler.handle.return_value = UnitResult.success()

        response: typing.Final = await create_order(
            request=MagicMock(**request_data),
            handler=mock_handler,
        )

        assert response.status_code == 201  # type: ignore[attr-defined]
        mock_handler.handle.assert_called_once()

    @pytest.mark.anyio
    async def test_create_order_conflict(
        self,
        mock_handler: MagicMock,
    ) -> None:
        order_id: typing.Final = uuid4()
        request_data: typing.Final = {
            "order_id": str(order_id),
            "country": "Россия",
            "city": "Москва",
            "street": "Тверская",
            "house": "1",
            "apartment": "1",
            "volume": 10,
        }

        mock_handler.handle.return_value = UnitResult.failure(Error.of("order.already.exists", "Order already exists"))

        response: typing.Final = await create_order(
            request=MagicMock(**request_data),
            handler=mock_handler,
        )

        assert response.status_code == 409  # type: ignore[attr-defined]
        mock_handler.handle.assert_called_once()
