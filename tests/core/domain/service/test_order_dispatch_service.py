import typing
import uuid

import pytest

from delivery.core.domain.model.courier.courier import Courier
from delivery.core.domain.model.kernel import Location
from delivery.core.domain.model.order.order import Order
from delivery.core.domain.service import OrderDispatchDomainService


class TestOrderDispatchDomainService:
    @pytest.fixture
    def dispatch_service(self) -> OrderDispatchDomainService:
        return OrderDispatchDomainService()

    @staticmethod
    def _create_courier(
        name: str,
        speed: int,
        location: Location,
    ) -> Courier:
        return Courier.must_create(
            name=name,
            speed=speed,
            location=location,
        )

    @staticmethod
    def _create_order(location: Location, volume: int) -> Order:
        order_id: typing.Final = uuid.uuid4()
        return Order.must_create(
            id_=order_id,
            location=location,
            volume=volume,
        )

    def test_dispatch_with_null_order_raises_error(
        self,
        dispatch_service: OrderDispatchDomainService,
    ) -> None:
        result: typing.Final = dispatch_service.dispatch_order(
            None,  # type: ignore[arg-type]
            [],
        )

        assert result.is_failure
        assert result.get_error().code == "value.is.required"

    def test_dispatch_with_null_couriers_raises_error(
        self,
        dispatch_service: OrderDispatchDomainService,
    ) -> None:
        order: typing.Final = self._create_order(
            location=Location.must_create(5, 5),
            volume=5,
        )

        result: typing.Final = dispatch_service.dispatch_order(
            order,
            None,  # type: ignore[arg-type]
        )

        assert result.is_failure
        assert result.get_error().code == "value.is.required"

    def test_dispatch_with_empty_couriers_list_raises_error(
        self,
        dispatch_service: OrderDispatchDomainService,
    ) -> None:
        order: typing.Final = self._create_order(
            location=Location.must_create(5, 5),
            volume=5,
        )

        result: typing.Final = dispatch_service.dispatch_order(order, [])

        assert result.is_failure
        assert result.get_error().code == "value.is.required"

    def test_dispatch_with_single_courier(
        self,
        dispatch_service: OrderDispatchDomainService,
    ) -> None:
        courier_location: typing.Final = Location.must_create(1, 1)
        order_location: typing.Final = Location.must_create(5, 5)

        courier: typing.Final = self._create_courier(
            name="Courier 1",
            speed=10,
            location=courier_location,
        )

        order: typing.Final = self._create_order(
            location=order_location,
            volume=5,
        )

        result: typing.Final = dispatch_service.dispatch_order(order, [courier])

        assert result.is_success
        assert result.get_value().id == courier.id

    def test_dispatch_selects_fastest_courier(
        self,
        dispatch_service: OrderDispatchDomainService,
    ) -> None:
        order_location: typing.Final = Location.must_create(10, 10)

        far_courier: typing.Final = self._create_courier(
            name="Fast Courier",
            speed=20,
            location=Location.must_create(1, 1),
        )

        near_courier: typing.Final = self._create_courier(
            name="Slow Courier",
            speed=2,
            location=Location.must_create(8, 8),
        )

        order: typing.Final = self._create_order(
            location=order_location,
            volume=5,
        )

        result: typing.Final = dispatch_service.dispatch_order(order, [far_courier, near_courier])

        assert result.is_success
        assert result.get_value().id == far_courier.id

    def test_dispatch_filters_by_storage_capacity(
        self,
        dispatch_service: OrderDispatchDomainService,
    ) -> None:
        order_location: typing.Final = Location.must_create(5, 5)

        small_courier: typing.Final = self._create_courier(
            name="Small Courier",
            speed=10,
            location=Location.must_create(1, 1),
        )
        occupied_order_id: typing.Final = uuid.uuid4()
        take_result: typing.Final = small_courier.take_order(occupied_order_id, order_volume=10)
        assert take_result.is_success

        large_courier: typing.Final = self._create_courier(
            name="Large Courier",
            speed=5,
            location=Location.must_create(1, 1),
        )

        order: typing.Final = self._create_order(
            location=order_location,
            volume=8,
        )

        result: typing.Final = dispatch_service.dispatch_order(order, [small_courier, large_courier])

        assert result.is_success
        assert result.get_value().id == large_courier.id

    def test_dispatch_no_suitable_courier(
        self,
        dispatch_service: OrderDispatchDomainService,
    ) -> None:
        order_location: typing.Final = Location.must_create(5, 5)

        courier1: typing.Final = self._create_courier(
            name="Courier 1",
            speed=10,
            location=Location.must_create(1, 1),
        )
        occupied_order_id_1: typing.Final = uuid.uuid4()
        take_result1: typing.Final = courier1.take_order(occupied_order_id_1, order_volume=10)
        assert take_result1.is_success

        courier2: typing.Final = self._create_courier(
            name="Courier 2",
            speed=10,
            location=Location.must_create(1, 1),
        )
        occupied_order_id_2: typing.Final = uuid.uuid4()
        take_result2: typing.Final = courier2.take_order(occupied_order_id_2, order_volume=10)
        assert take_result2.is_success

        order: typing.Final = self._create_order(
            location=order_location,
            volume=15,
        )

        result: typing.Final = dispatch_service.dispatch_order(order, [courier1, courier2])

        assert result.is_failure
        error: typing.Final = result.get_error()
        assert error.code == "order.dispatch.no.suitable.courier"

    def test_dispatch_with_empty_couriers_list(
        self,
        dispatch_service: OrderDispatchDomainService,
    ) -> None:
        order: typing.Final = self._create_order(
            location=Location.must_create(5, 5),
            volume=5,
        )

        result: typing.Final = dispatch_service.dispatch_order(order, [])

        assert result.is_failure
        assert result.get_error().code == "value.is.required"

    def test_dispatch_ignores_courier_without_storage(
        self,
        dispatch_service: OrderDispatchDomainService,
    ) -> None:
        order_location: typing.Final = Location.must_create(5, 5)

        busy_courier: typing.Final = self._create_courier(
            name="Busy Courier",
            speed=10,
            location=Location.must_create(1, 1),
        )

        occupied_order_id: typing.Final = uuid.uuid4()
        take_result: typing.Final = busy_courier.take_order(occupied_order_id, order_volume=5)
        assert take_result.is_success

        free_courier: typing.Final = self._create_courier(
            name="Free Courier",
            speed=10,
            location=Location.must_create(1, 1),
        )

        order: typing.Final = self._create_order(
            location=order_location,
            volume=5,
        )

        result: typing.Final = dispatch_service.dispatch_order(order, [busy_courier, free_courier])

        assert result.is_success
        assert result.get_value().id == free_courier.id
