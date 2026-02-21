import typing
from uuid import uuid4

import pytest

from delivery.core.domain.model.kernel import Location
from delivery.core.domain.model.order.order import Order
from delivery.core.domain.model.order.order_status import OrderStatus


class TestOrderCreation:
    @pytest.mark.parametrize(
        "volume",
        [
            1,
            10,
            100,
            500,
        ],
        ids=[
            "min_volume",
            "small_volume",
            "medium_volume",
            "large_volume",
        ],
    )
    def test_create_valid_order(self, volume: int) -> None:
        order_id: typing.Final = uuid4()
        location: typing.Final = Location.must_create(5, 5)

        result: typing.Final = Order.create(order_id, location, volume)

        assert result.is_success
        order: typing.Final = result.get_value()
        assert order.id == order_id
        assert order.location == location
        assert order.volume == volume
        assert order.status == OrderStatus.CREATED
        assert order.courier_id is None

    @pytest.mark.parametrize(
        ("volume", "error_code_fragment"),
        [
            (0, "must.be.greater.or.equal"),
            (-1, "must.be.greater.or.equal"),
            (-100, "must.be.greater.or.equal"),
        ],
        ids=[
            "zero_volume",
            "negative_volume",
            "large_negative_volume",
        ],
    )
    def test_create_invalid_volume(self, volume: int, error_code_fragment: str) -> None:
        order_id: typing.Final = uuid4()
        location: typing.Final = Location.must_create(5, 5)

        result: typing.Final = Order.create(order_id, location, volume)

        assert result.is_failure
        error: typing.Final = result.get_error()
        assert error_code_fragment in error.code

    def test_create_with_none_location(self) -> None:
        order_id: typing.Final = uuid4()

        result: typing.Final = Order.create(order_id, None, 100)  # type: ignore[arg-type]

        assert result.is_failure
        error: typing.Final = result.get_error()
        assert "value.is.required" in error.code


class TestOrderAssign:
    def test_assign_success(self) -> None:
        order_id: typing.Final = uuid4()
        location: typing.Final = Location.must_create(5, 5)
        order: typing.Final = Order.must_create(order_id, location, 100)
        courier_id: typing.Final = uuid4()

        result: typing.Final = order.assign(courier_id)

        assert result.is_success
        assert order.status == OrderStatus.ASSIGNED
        assert order.courier_id == courier_id

    def test_assign_already_assigned(self) -> None:
        order_id: typing.Final = uuid4()
        location: typing.Final = Location.must_create(5, 5)
        order: typing.Final = Order.must_create(order_id, location, 100)
        first_courier: typing.Final = uuid4()
        second_courier: typing.Final = uuid4()

        order.assign(first_courier)
        result: typing.Final = order.assign(second_courier)

        assert result.is_failure
        error: typing.Final = result.get_error()
        assert "order.already.assigned" in error.code
        assert order.courier_id == first_courier

    def test_assign_completed_order(self) -> None:
        order_id: typing.Final = uuid4()
        location: typing.Final = Location.must_create(5, 5)
        order: typing.Final = Order.must_create(order_id, location, 100)
        courier_id: typing.Final = uuid4()

        order.assign(courier_id)
        order.complete()

        new_courier: typing.Final = uuid4()
        result: typing.Final = order.assign(new_courier)

        assert result.is_failure
        error: typing.Final = result.get_error()
        assert "order.already.assigned" in error.code


class TestOrderComplete:
    def test_complete_assigned_order(self) -> None:
        order_id: typing.Final = uuid4()
        location: typing.Final = Location.must_create(5, 5)
        order: typing.Final = Order.must_create(order_id, location, 100)
        courier_id: typing.Final = uuid4()

        order.assign(courier_id)
        result: typing.Final = order.complete()

        assert result.is_success
        assert order.status == OrderStatus.COMPLETED

    def test_complete_not_assigned_order(self) -> None:
        order_id: typing.Final = uuid4()
        location: typing.Final = Location.must_create(5, 5)
        order: typing.Final = Order.must_create(order_id, location, 100)

        result: typing.Final = order.complete()

        assert result.is_failure
        error: typing.Final = result.get_error()
        assert "order.not.assigned" in error.code
        assert order.status == OrderStatus.CREATED

    def test_complete_already_completed_order(self) -> None:
        order_id: typing.Final = uuid4()
        location: typing.Final = Location.must_create(5, 5)
        order: typing.Final = Order.must_create(order_id, location, 100)
        courier_id: typing.Final = uuid4()

        order.assign(courier_id)
        order.complete()
        result: typing.Final = order.complete()

        assert result.is_failure
        error: typing.Final = result.get_error()
        assert "order.not.assigned" in error.code


class TestOrderWorkflow:
    def test_full_order_lifecycle(self) -> None:
        order_id: typing.Final = uuid4()
        location: typing.Final = Location.must_create(5, 5)
        order: typing.Final = Order.must_create(order_id, location, 100)

        assert order.status == OrderStatus.CREATED
        assert order.courier_id is None

        courier_id: typing.Final = uuid4()
        assign_result: typing.Final = order.assign(courier_id)
        assert assign_result.is_success
        assert order.status == OrderStatus.ASSIGNED
        assert order.courier_id == courier_id

        complete_result: typing.Final = order.complete()
        assert complete_result.is_success
        assert order.status == OrderStatus.COMPLETED
        assert order.courier_id == courier_id
