import typing
from unittest.mock import AsyncMock, MagicMock

import pytest

from delivery.core.application.commands.create_courier import (
    CreateCourierCommand,
    CreateCourierCommandHandler,
    CreateCourierCommandHandlerImpl,
)
from delivery.core.ports.courier_repository import CourierRepository
from delivery.event_publisher import DefaultDomainEventPublisher


class TestCreateCourierCommandHandler:
    @pytest.fixture
    def mock_courier_repository(self) -> MagicMock:
        return MagicMock(spec=CourierRepository)

    @pytest.fixture
    def mock_domain_event_publisher(self) -> MagicMock:
        return MagicMock(spec=DefaultDomainEventPublisher)

    @pytest.fixture
    def handler(
        self,
        mock_courier_repository: MagicMock,
        mock_domain_event_publisher: MagicMock,
    ) -> CreateCourierCommandHandler:
        return CreateCourierCommandHandlerImpl(
            courier_repository=mock_courier_repository,
            domain_event_publisher=mock_domain_event_publisher,
        )

    @pytest.mark.anyio
    async def test_create_courier_should_be_success(
        self,
        handler: CreateCourierCommandHandler,
        mock_courier_repository: MagicMock,
        mock_domain_event_publisher: MagicMock,
    ) -> None:
        command: typing.Final = CreateCourierCommand(name="Test Courier", speed=10)

        mock_courier_repository.add = AsyncMock()
        mock_domain_event_publisher.publish = AsyncMock()

        result: typing.Final = await handler.handle(command)

        assert result.is_success
        mock_courier_repository.add.assert_called_once()
        mock_domain_event_publisher.publish.assert_called_once()

        added_courier: typing.Final = mock_courier_repository.add.call_args[0][0]
        assert added_courier.name == "Test Courier"
        assert added_courier.speed == 10
        assert result.get_value() == added_courier.id
