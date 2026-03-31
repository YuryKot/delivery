import typing
from unittest.mock import AsyncMock, MagicMock

import pytest

from delivery.core.application.commands.create_courier import (
    CreateCourierCommand,
    CreateCourierCommandHandler,
    CreateCourierCommandHandlerImpl,
)
from delivery.core.ports.unit_of_work import DeliveryUnitOfWork


class TestCreateCourierCommandHandler:
    @pytest.fixture
    def handler(
        self,
    ) -> CreateCourierCommandHandler:
        return CreateCourierCommandHandlerImpl()

    @pytest.mark.anyio
    async def test_create_courier_should_be_success(
        self,
        handler: CreateCourierCommandHandler,
        monkeypatch: pytest.MonkeyPatch,
    ) -> None:
        command: typing.Final = CreateCourierCommand(name="Test Courier", speed=10)

        mock_uow: typing.Final = MagicMock()
        mock_uow.courier.add = AsyncMock()
        mock_uow.domain_event_publisher.publish = AsyncMock()

        mock_start_cm: typing.Final = MagicMock()
        mock_start_cm.__aenter__ = AsyncMock(return_value=mock_uow)
        mock_start_cm.__aexit__ = AsyncMock(return_value=None)

        monkeypatch.setattr(DeliveryUnitOfWork, "start", lambda: mock_start_cm)

        result: typing.Final = await handler.handle(command)

        assert result.is_success
        mock_uow.courier.add.assert_called_once()
        mock_uow.domain_event_publisher.publish.assert_called_once()
