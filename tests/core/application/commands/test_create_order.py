import typing
from unittest.mock import AsyncMock, MagicMock
from uuid import uuid4

import pytest

from delivery.core.application.commands.create_order import (
    CreateOrderCommand,
    CreateOrderCommandHandler,
    CreateOrderCommandHandlerImpl,
)
from delivery.core.domain.model.kernel import Address, Location, Volume
from delivery.core.ports.courier_repository import CourierRepository
from delivery.core.ports.order_repository import OrderRepository
from delivery.event_publisher import DefaultDomainEventPublisher


class TestCreateOrderCommandHandler:
    @pytest.fixture
    def mock_order_repository(self) -> MagicMock:
        return MagicMock(spec=OrderRepository)

    @pytest.fixture
    def mock_courier_repository(self) -> MagicMock:
        return MagicMock(spec=CourierRepository)

    @pytest.fixture
    def mock_domain_event_publisher(self) -> MagicMock:
        return MagicMock(spec=DefaultDomainEventPublisher)

    @pytest.fixture
    def handler(
        self,
        mock_order_repository: MagicMock,
        mock_courier_repository: MagicMock,
        mock_domain_event_publisher: MagicMock,
    ) -> CreateOrderCommandHandler:
        return CreateOrderCommandHandlerImpl(
            order_repository=mock_order_repository,
            courier_repository=mock_courier_repository,
            domain_event_publisher=mock_domain_event_publisher,
        )

    @pytest.mark.anyio
    async def test_create_order_should_be_success(
        self,
        handler: CreateOrderCommandHandler,
        mock_order_repository: MagicMock,
        mock_courier_repository: MagicMock,
        mock_domain_event_publisher: MagicMock,
    ) -> None:
        order_id: typing.Final = uuid4()
        address: typing.Final = Address.must_create(
            country="Россия",
            city="Москва",
            street="Тверская",
            house="1",
            apartment="1",
        )
        volume: typing.Final = Volume.must_create(5)
        command: typing.Final = CreateOrderCommand(
            order_id=order_id,
            address=address,
            volume=volume,
        )

        mock_order_repository.add = AsyncMock()
        mock_courier_repository.get_random_location = AsyncMock(return_value=Location.must_create(5, 5))
        mock_domain_event_publisher.publish = AsyncMock()

        await handler.handle(command)

        mock_order_repository.add.assert_called_once()
        mock_domain_event_publisher.publish.assert_called_once()

        added_order: typing.Final = mock_order_repository.add.call_args[0][0]
        assert added_order.id == order_id
        assert added_order.volume == volume
