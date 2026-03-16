import typing
from unittest.mock import AsyncMock, MagicMock

import pytest
import sqlalchemy.ext.asyncio as sa_async

from delivery.core.application.queries.get_all_incomplete_orders import (
    GetAllIncompleteOrdersQuery,
    GetAllIncompleteOrdersQueryHandler,
    GetAllIncompleteOrdersQueryHandlerImpl,
    IncompleteOrderDto,
)
from delivery.database.models import OrderModel


class TestGetAllIncompleteOrdersQueryHandler:
    @pytest.fixture
    def mock_session(self) -> MagicMock:
        return MagicMock(spec=sa_async.AsyncSession)

    @pytest.fixture
    def handler(
        self,
        mock_session: MagicMock,
    ) -> GetAllIncompleteOrdersQueryHandler:
        return GetAllIncompleteOrdersQueryHandlerImpl(
            session=mock_session,
        )

    @pytest.mark.anyio
    async def test_get_all_incomplete_orders_should_return_empty_list(
        self,
        handler: GetAllIncompleteOrdersQueryHandler,
        mock_session: MagicMock,
    ) -> None:
        query: typing.Final = GetAllIncompleteOrdersQuery()

        mock_result: typing.Final = MagicMock()
        mock_result.scalars().unique().all = MagicMock(return_value=[])
        mock_session.execute = AsyncMock(return_value=mock_result)

        result: typing.Final = await handler.handle(query)

        assert result.is_success
        assert result.get_value() == []

    @pytest.mark.anyio
    async def test_get_all_incomplete_orders_should_return_orders(
        self,
        handler: GetAllIncompleteOrdersQueryHandler,
        mock_session: MagicMock,
    ) -> None:
        # Arrange
        query: typing.Final = GetAllIncompleteOrdersQuery()

        order_model1: typing.Final = MagicMock(spec=OrderModel)
        order_model1.id = "11111111-1111-1111-1111-111111111111"
        order_model1.location_x = 5
        order_model1.location_y = 6
        order_model1.status = "Created"

        order_model2: typing.Final = MagicMock(spec=OrderModel)
        order_model2.id = "22222222-2222-2222-2222-222222222222"
        order_model2.location_x = 7
        order_model2.location_y = 8
        order_model2.status = "Assigned"

        mock_result: typing.Final = MagicMock()
        mock_result.scalars().unique().all = MagicMock(return_value=[order_model1, order_model2])
        mock_session.execute = AsyncMock(return_value=mock_result)

        # Act
        result: typing.Final = await handler.handle(query)

        # Assert
        assert result.is_success
        dto_list: typing.Final = result.get_value()
        assert len(dto_list) == 2
        assert isinstance(dto_list[0], IncompleteOrderDto)
        assert str(dto_list[0].id) == str(order_model1.id)
        assert dto_list[0].location_x == 5
        assert dto_list[0].location_y == 6
