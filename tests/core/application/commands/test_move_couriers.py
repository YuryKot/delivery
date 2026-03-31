import typing
from unittest.mock import AsyncMock, MagicMock
from uuid import uuid4

import pytest

from delivery.core.application.commands.move_couriers import (
    MoveCouriersCommand,
    MoveCouriersCommandHandler,
    MoveCouriersCommandHandlerImpl,
)
from delivery.core.domain.model.courier.courier import Courier
from delivery.core.domain.model.kernel import Location, Volume
from delivery.core.ports.order_events_producer import OrderEventsProducer
from delivery.core.ports.unit_of_work import DeliveryUnitOfWork
from tests.test_fixtures import create_test_order


class TestMoveCouriersCommandHandler:
    @pytest.fixture
    def mock_order_events_producer(self) -> MagicMock:
        return MagicMock(spec=OrderEventsProducer)

    @pytest.fixture
    def handler(
        self,
        mock_order_events_producer: MagicMock,
    ) -> MoveCouriersCommandHandler:
        return MoveCouriersCommandHandlerImpl(
            order_events_producer=mock_order_events_producer,
        )

    @pytest.mark.anyio
    async def test_move_couriers_should_move_couriers_when_not_reached(
        self,
        handler: MoveCouriersCommandHandler,
        mock_order_events_producer: MagicMock,
        monkeypatch: pytest.MonkeyPatch,
    ) -> None:
        command: typing.Final = MoveCouriersCommand()

        courier_id: typing.Final = uuid4()
        order_location: typing.Final = Location.must_create(10, 10)
        order: typing.Final = create_test_order(location=order_location, courier_id=courier_id)

        courier: typing.Final = Courier.must_create(name="Test", speed=1, location=Location.must_create(1, 1))

        mock_uow: typing.Final = MagicMock()
        mock_uow.order.get_all_assigned = AsyncMock(return_value=[order])
        mock_uow.courier.get_by_id = AsyncMock(return_value=courier)
        mock_uow.courier.update = AsyncMock()
        mock_uow.order.update = AsyncMock()

        mock_start_cm: typing.Final = MagicMock()
        mock_start_cm.__aenter__ = AsyncMock(return_value=mock_uow)
        mock_start_cm.__aexit__ = AsyncMock(return_value=None)

        monkeypatch.setattr(DeliveryUnitOfWork, "start", lambda: mock_start_cm)
        mock_order_events_producer.publish = AsyncMock()

        await handler.handle(command)

        mock_uow.order.get_all_assigned.assert_called_once()
        mock_uow.courier.get_by_id.assert_called_once_with(courier_id)
        mock_uow.courier.update.assert_called_once()
        mock_uow.order.update.assert_not_called()
        mock_order_events_producer.publish.assert_not_called()

    @pytest.mark.anyio
    async def test_move_couriers_should_complete_orders_when_reached(
        self,
        handler: MoveCouriersCommandHandler,
        mock_order_events_producer: MagicMock,
        monkeypatch: pytest.MonkeyPatch,
    ) -> None:
        command: typing.Final = MoveCouriersCommand()

        location: typing.Final = Location.must_create(5, 5)
        courier_id: typing.Final = uuid4()
        order_id: typing.Final = uuid4()
        order: typing.Final = create_test_order(
            order_id=order_id,
            location=location,
            courier_id=courier_id,
        )

        courier: typing.Final = Courier.must_create(name="Test", speed=10, location=location)
        courier.take_order(order_id, Volume.must_create(1))

        mock_uow: typing.Final = MagicMock()
        mock_uow.order.get_all_assigned = AsyncMock(return_value=[order])
        mock_uow.courier.get_by_id = AsyncMock(return_value=courier)
        mock_uow.courier.update = AsyncMock()
        mock_uow.order.update = AsyncMock()

        mock_start_cm: typing.Final = MagicMock()
        mock_start_cm.__aenter__ = AsyncMock(return_value=mock_uow)
        mock_start_cm.__aexit__ = AsyncMock(return_value=None)

        monkeypatch.setattr(DeliveryUnitOfWork, "start", lambda: mock_start_cm)
        mock_order_events_producer.publish = AsyncMock()

        await handler.handle(command)

        mock_uow.order.get_all_assigned.assert_called_once()
        mock_uow.courier.get_by_id.assert_called_once_with(courier_id)
        mock_uow.courier.update.assert_called_once()
        mock_uow.order.update.assert_called_once()
        mock_order_events_producer.publish.assert_called_once()
