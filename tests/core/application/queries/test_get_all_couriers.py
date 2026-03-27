import typing
from unittest.mock import AsyncMock, MagicMock

import pytest

from delivery.core.application.queries.get_all_couriers import (
    CourierDto,
    GetAllCouriersQuery,
    GetAllCouriersQueryHandler,
    GetAllCouriersQueryHandlerImpl,
)
from delivery.core.domain.model.kernel import Location
from tests.test_fixtures import create_test_courier


class TestGetAllCouriersQueryHandler:
    @pytest.fixture
    def mock_session(self) -> MagicMock:
        return MagicMock()

    @pytest.fixture
    def handler(
        self,
        mock_session: MagicMock,
    ) -> GetAllCouriersQueryHandler:
        return GetAllCouriersQueryHandlerImpl(
            session=mock_session,
        )

    @pytest.mark.anyio
    async def test_get_all_couriers_should_return_empty_list(
        self,
        handler: GetAllCouriersQueryHandler,
        mock_session: MagicMock,
    ) -> None:
        query: typing.Final = GetAllCouriersQuery()

        mock_result: typing.Final = MagicMock()
        mock_result.scalars.return_value.unique.return_value.all.return_value = []
        mock_session.execute = AsyncMock(return_value=mock_result)

        result: typing.Final = await handler.handle(query)

        assert result.is_success
        assert result.get_value() == []

    @pytest.mark.anyio
    async def test_get_all_couriers_should_return_couriers(
        self,
        handler: GetAllCouriersQueryHandler,
        mock_session: MagicMock,
    ) -> None:
        query: typing.Final = GetAllCouriersQuery()

        courier1: typing.Final = create_test_courier(name="Courier 1", location=Location.must_create(1, 1))
        courier2: typing.Final = create_test_courier(name="Courier 2", location=Location.must_create(2, 2))

        mock_model1: typing.Final = MagicMock()
        mock_model1.id = courier1.id
        mock_model1.name = courier1.name
        mock_model1.location_x = 1
        mock_model1.location_y = 1

        mock_model2: typing.Final = MagicMock()
        mock_model2.id = courier2.id
        mock_model2.name = courier2.name
        mock_model2.location_x = 2
        mock_model2.location_y = 2

        mock_result: typing.Final = MagicMock()
        mock_result.scalars.return_value.unique.return_value.all.return_value = [mock_model1, mock_model2]
        mock_session.execute = AsyncMock(return_value=mock_result)

        result: typing.Final = await handler.handle(query)

        assert result.is_success
        dto_list: typing.Final = result.get_value()
        assert len(dto_list) == 2
        assert isinstance(dto_list[0], CourierDto)
        assert dto_list[0].id == courier1.id
        assert dto_list[0].name == "Courier 1"
        assert dto_list[0].location_x == 1
        assert dto_list[0].location_y == 1
