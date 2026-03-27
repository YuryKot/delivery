import typing
from unittest.mock import AsyncMock, MagicMock
from uuid import uuid4

import pytest

from delivery.adapters.input.http.controllers.create_courier_controller import create_courier
from delivery.libs.errs.error import Error
from delivery.libs.errs.result import Result


class TestCreateCourierController:
    @pytest.fixture
    def mock_handler(self) -> MagicMock:
        handler: typing.Final = MagicMock()
        handler.handle = AsyncMock()
        return handler

    @pytest.mark.anyio
    async def test_create_courier_success(
        self,
        mock_handler: MagicMock,
    ) -> None:
        courier_id: typing.Final = uuid4()
        request_data: typing.Final = {"name": "Иван"}

        mock_handler.handle.return_value = Result.success(courier_id)

        response: typing.Final = await create_courier(
            request=MagicMock(**request_data),
            handler=mock_handler,
        )

        assert response.status_code == 201
        mock_handler.handle.assert_called_once()

    @pytest.mark.anyio
    async def test_create_courier_conflict(
        self,
        mock_handler: MagicMock,
    ) -> None:
        request_data: typing.Final = {"name": "Иван"}

        mock_handler.handle.return_value = Result.failure(Error.of("courier.already.exists", "Courier already exists"))

        response: typing.Final = await create_courier(
            request=MagicMock(**request_data),
            handler=mock_handler,
        )

        assert response.status_code == 409
        mock_handler.handle.assert_called_once()
