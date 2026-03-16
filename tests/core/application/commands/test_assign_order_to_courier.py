import typing
from unittest.mock import AsyncMock, MagicMock

import pytest

from delivery.core.application.commands.assign_order_to_courier import (
    AssignOrderToCourierCommand,
    AssignOrderToCourierCommandHandler,
    AssignOrderToCourierCommandHandlerImpl,
)
from delivery.core.domain.service.order_dispatch_service import OrderDispatchDomainService
from delivery.core.ports.unit_of_work import DeliveryUnitOfWork
from delivery.event_publisher import DefaultDomainEventPublisher
from delivery.libs.errs.result import Result
from tests.test_fixtures import create_test_courier, create_test_order


class TestAssignOrderToCourierCommandHandler:
    @pytest.fixture
    def mock_order_dispatch_service(self) -> MagicMock:
        return MagicMock(spec=OrderDispatchDomainService)

    @pytest.fixture
    def mock_domain_event_publisher(self) -> MagicMock:
        return MagicMock(spec=DefaultDomainEventPublisher)

    @pytest.fixture
    def handler(
        self,
        mock_order_dispatch_service: MagicMock,
        mock_domain_event_publisher: MagicMock,
    ) -> AssignOrderToCourierCommandHandler:
        return AssignOrderToCourierCommandHandlerImpl(
            order_dispatch_service=mock_order_dispatch_service,
            domain_event_publisher=mock_domain_event_publisher,
        )

    @pytest.mark.anyio
    async def test_assign_order_should_return_failure_when_no_free_couriers(
        self,
        handler: AssignOrderToCourierCommandHandler,
        mock_domain_event_publisher: MagicMock,
        monkeypatch: pytest.MonkeyPatch,
    ) -> None:
        command: typing.Final = AssignOrderToCourierCommand()
        order: typing.Final = create_test_order()

        mock_uow: typing.Final = MagicMock()
        mock_uow.order.get_first_by_status_created = AsyncMock(return_value=order)
        mock_uow.courier.get_all_free = AsyncMock(return_value=[])

        mock_start_cm: typing.Final = MagicMock()
        mock_start_cm.__aenter__ = AsyncMock(return_value=mock_uow)
        mock_start_cm.__aexit__ = AsyncMock(return_value=None)

        monkeypatch.setattr(DeliveryUnitOfWork, "start", lambda: mock_start_cm)
        mock_domain_event_publisher.publish = AsyncMock()

        result: typing.Final = await handler.handle(command)

        assert result.is_failure

    @pytest.mark.anyio
    async def test_assign_order_should_assign_to_courier(
        self,
        handler: AssignOrderToCourierCommandHandler,
        mock_order_dispatch_service: MagicMock,
        mock_domain_event_publisher: MagicMock,
        monkeypatch: pytest.MonkeyPatch,
    ) -> None:
        command: typing.Final = AssignOrderToCourierCommand()
        order: typing.Final = create_test_order()
        courier: typing.Final = create_test_courier()

        mock_uow: typing.Final = MagicMock()
        mock_uow.order.get_first_by_status_created = AsyncMock(return_value=order)
        mock_uow.courier.get_all_free = AsyncMock(return_value=[courier])
        mock_uow.courier.update = AsyncMock()
        mock_uow.order.update = AsyncMock()

        mock_start_cm: typing.Final = MagicMock()
        mock_start_cm.__aenter__ = AsyncMock(return_value=mock_uow)
        mock_start_cm.__aexit__ = AsyncMock(return_value=None)

        monkeypatch.setattr(DeliveryUnitOfWork, "start", lambda: mock_start_cm)
        mock_order_dispatch_service.dispatch_order = MagicMock(return_value=Result.success(courier))
        mock_domain_event_publisher.publish = AsyncMock()

        await handler.handle(command)

        mock_order_dispatch_service.dispatch_order.assert_called_once_with(order, [courier])
        mock_uow.order.update.assert_called_once()
        mock_uow.courier.update.assert_called_once()
        mock_domain_event_publisher.publish.assert_called_once()
