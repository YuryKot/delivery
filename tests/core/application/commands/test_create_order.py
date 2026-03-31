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
from delivery.core.ports.geo_location_client import GeoLocationClient
from delivery.core.ports.unit_of_work import DeliveryUnitOfWork
from delivery.libs.errs.result import Result


class TestCreateOrderCommandHandler:
    @pytest.fixture
    def mock_geo_location_client(self) -> MagicMock:
        return MagicMock(spec=GeoLocationClient)

    @pytest.fixture
    def handler(
        self,
        mock_geo_location_client: MagicMock,
    ) -> CreateOrderCommandHandler:
        return CreateOrderCommandHandlerImpl(
            geo_location_client=mock_geo_location_client,
        )

    @pytest.mark.anyio
    async def test_create_order_should_be_success(
        self,
        handler: CreateOrderCommandHandler,
        mock_geo_location_client: MagicMock,
        monkeypatch: pytest.MonkeyPatch,
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

        mock_uow: typing.Final = MagicMock()
        mock_uow.order.add = AsyncMock()
        mock_uow.domain_event_publisher.publish = AsyncMock()

        mock_start_cm: typing.Final = MagicMock()
        mock_start_cm.__aenter__ = AsyncMock(return_value=mock_uow)
        mock_start_cm.__aexit__ = AsyncMock(return_value=None)

        monkeypatch.setattr(DeliveryUnitOfWork, "start", lambda: mock_start_cm)
        mock_geo_location_client.get_location = AsyncMock(return_value=Result.success(Location.must_create(5, 5)))

        await handler.handle(command)

        mock_uow.order.add.assert_called_once()
        mock_uow.domain_event_publisher.publish.assert_called_once()

        added_order: typing.Final = mock_uow.order.add.call_args[0][0]
        assert added_order.id == order_id
        assert added_order.volume == volume
