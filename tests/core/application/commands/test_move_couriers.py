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
from delivery.core.domain.model.kernel import Location
from delivery.core.ports.unit_of_work import DeliveryUnitOfWork
from delivery.event_publisher import DefaultDomainEventPublisher
from tests.test_fixtures import create_test_order


class TestMoveCouriersCommandHandler:
    @pytest.fixture
    def mock_domain_event_publisher(self) -> MagicMock:
        return MagicMock(spec=DefaultDomainEventPublisher)

    @pytest.fixture
    def handler(
        self,
        mock_domain_event_publisher: MagicMock,
    ) -> MoveCouriersCommandHandler:
        return MoveCouriersCommandHandlerImpl(
            domain_event_publisher=mock_domain_event_publisher,
        )

    @pytest.mark.anyio
    async def test_move_couriers_should_move_couriers_when_not_reached(
        self,
        handler: MoveCouriersCommandHandler,
        mock_domain_event_publisher: MagicMock,
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
        mock_domain_event_publisher.publish = AsyncMock()

        await handler.handle(command)

        mock_uow.order.get_all_assigned.assert_called_once()
        mock_uow.courier.get_by_id.assert_called_once_with(courier_id)
        mock_uow.courier.update.assert_called_once()
        mock_uow.order.update.assert_not_called()  # Заказ не завершён (курьер не достиг)
        mock_domain_event_publisher.publish.assert_called_once()

    @pytest.mark.anyio
    async def test_move_couriers_should_complete_orders_when_reached(
        self,
        handler: MoveCouriersCommandHandler,
        mock_domain_event_publisher: MagicMock,
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
        courier.take_order(order_id, order_volume=1)

        mock_uow: typing.Final = MagicMock()
        mock_uow.order.get_all_assigned = AsyncMock(return_value=[order])
        mock_uow.courier.get_by_id = AsyncMock(return_value=courier)
        mock_uow.courier.update = AsyncMock()
        mock_uow.order.update = AsyncMock()

        mock_start_cm: typing.Final = MagicMock()
        mock_start_cm.__aenter__ = AsyncMock(return_value=mock_uow)
        mock_start_cm.__aexit__ = AsyncMock(return_value=None)

        monkeypatch.setattr(DeliveryUnitOfWork, "start", lambda: mock_start_cm)
        mock_domain_event_publisher.publish = AsyncMock()

        await handler.handle(command)

        mock_uow.order.get_all_assigned.assert_called_once()
        mock_uow.courier.get_by_id.assert_called_once_with(courier_id)
        mock_uow.courier.update.assert_called_once()
        mock_uow.order.update.assert_called_once()
        mock_domain_event_publisher.publish.assert_called_once()
