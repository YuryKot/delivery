import typing
from uuid import uuid4

import pytest

from delivery.core.domain.model.courier.courier import Courier
from delivery.core.domain.model.kernel import Location
from delivery.libs.errs.error import DomainInvariantError


class TestCourierCreation:
    @pytest.mark.parametrize(
        ("name", "speed", "x", "y"),
        [
            ("Иван", 1, 1, 1),
            ("Петр", 2, 5, 5),
            ("Мария", 3, 10, 10),
            ("Courier", 10, 1, 10),
        ],
        ids=[
            "min_speed",
            "medium_speed",
            "high_speed",
            "max_speed",
        ],
    )
    def test_create_valid_courier(self, name: str, speed: int, x: int, y: int) -> None:
        location: typing.Final = Location.must_create(x, y)

        result: typing.Final = Courier.create(name, speed, location)

        assert result.is_success
        courier: typing.Final = result.get_value()
        assert courier.id is not None
        assert courier.name == name
        assert courier.speed == speed
        assert courier.location == location
        assert len(courier.storage_places) == 1
        assert courier.storage_places[0].name == "Сумка"
        assert courier.storage_places[0].total_volume == 10

    @pytest.mark.parametrize(
        ("name", "speed", "error_code_fragment"),
        [
            ("", 1, "value.is.required"),
            ("Иван", 0, "must.be.greater.or.equal"),
            ("Петр", -1, "must.be.greater.or.equal"),
        ],
        ids=[
            "empty_name",
            "zero_speed",
            "negative_speed",
        ],
    )
    def test_create_invalid_courier(self, name: str, speed: int, error_code_fragment: str) -> None:
        location: typing.Final = Location.must_create(5, 5)

        result: typing.Final = Courier.create(name, speed, location)

        assert result.is_failure
        error: typing.Final = result.get_error()
        assert error_code_fragment in error.code

    def test_create_with_none_location(self) -> None:
        result: typing.Final = Courier.create("Иван", 2, None)  # type: ignore[arg-type]

        assert result.is_failure
        error: typing.Final = result.get_error()
        assert "value.is.required" in error.code

    def test_must_create_valid_courier(self) -> None:
        location: typing.Final = Location.must_create(5, 5)

        courier: typing.Final = Courier.must_create("Иван", 2, location)

        assert courier.id is not None
        assert courier.name == "Иван"
        assert courier.speed == 2

    def test_must_create_invalid_courier_raises_exception(self) -> None:
        location: typing.Final = Location.must_create(5, 5)

        with pytest.raises(DomainInvariantError):
            Courier.must_create("", 2, location)


class TestCourierAddStoragePlace:
    def test_add_storage_place_success(self) -> None:
        location: typing.Final = Location.must_create(5, 5)
        courier: typing.Final = Courier.must_create("Иван", 2, location)

        result: typing.Final = courier.add_storage_place("Рюкзак", 50)

        assert result.is_success
        assert len(courier.storage_places) == 2
        assert courier.storage_places[1].name == "Рюкзак"
        assert courier.storage_places[1].total_volume == 50

    def test_add_multiple_storage_places(self) -> None:
        location: typing.Final = Location.must_create(5, 5)
        courier: typing.Final = Courier.must_create("Иван", 2, location)

        courier.add_storage_place("Рюкзак", 50)
        courier.add_storage_place("Багажник", 100)

        assert len(courier.storage_places) == 3

    def test_add_invalid_storage_place(self) -> None:
        location: typing.Final = Location.must_create(5, 5)
        courier: typing.Final = Courier.must_create("Иван", 2, location)

        result: typing.Final = courier.add_storage_place("", 50)

        assert result.is_failure
        error: typing.Final = result.get_error()
        assert "value.is.required" in error.code


class TestCourierCanTakeOrder:
    @pytest.mark.parametrize(
        ("order_volume", "can_take"),
        [
            (1, True),
            (5, True),
            (10, True),
            (11, False),
            (100, False),
        ],
        ids=[
            "small_order",
            "medium_order",
            "exact_volume",
            "slightly_exceeds",
            "large_order",
        ],
    )
    def test_can_take_order_default_storage(self, order_volume: int, can_take: bool) -> None:
        location: typing.Final = Location.must_create(5, 5)
        courier: typing.Final = Courier.must_create("Иван", 2, location)

        assert courier.can_take_order(order_volume) == can_take

    def test_can_take_order_with_additional_storage(self) -> None:
        location: typing.Final = Location.must_create(5, 5)
        courier: typing.Final = Courier.must_create("Иван", 2, location)
        courier.add_storage_place("Рюкзак", 50)

        assert courier.can_take_order(30)
        assert courier.can_take_order(50)
        assert not courier.can_take_order(51)

    def test_cannot_take_order_when_all_occupied(self) -> None:
        location: typing.Final = Location.must_create(5, 5)
        courier: typing.Final = Courier.must_create("Иван", 2, location)
        order_id: typing.Final = uuid4()

        courier.take_order(order_id, 10)

        assert not courier.can_take_order(5)
        assert not courier.can_take_order(10)


class TestCourierTakeOrder:
    def test_take_order_success(self) -> None:
        location: typing.Final = Location.must_create(5, 5)
        courier: typing.Final = Courier.must_create("Иван", 2, location)
        order_id: typing.Final = uuid4()

        result: typing.Final = courier.take_order(order_id, 8)

        assert result.is_success
        assert courier.storage_places[0].order_id == order_id
        assert courier.storage_places[0].is_occupied()

    def test_take_order_chooses_smallest_suitable(self) -> None:
        location: typing.Final = Location.must_create(5, 5)
        courier: typing.Final = Courier.must_create("Иван", 2, location)
        courier.add_storage_place("Рюкзак", 30)
        courier.add_storage_place("Багажник", 100)
        order_id: typing.Final = uuid4()

        result: typing.Final = courier.take_order(order_id, 8)

        assert result.is_success
        assert courier.storage_places[0].order_id == order_id
        assert courier.storage_places[1].order_id is None
        assert courier.storage_places[2].order_id is None

    def test_take_order_uses_larger_when_small_occupied(self) -> None:
        location: typing.Final = Location.must_create(5, 5)
        courier: typing.Final = Courier.must_create("Иван", 2, location)
        courier.add_storage_place("Багажник", 100)
        first_order: typing.Final = uuid4()
        second_order: typing.Final = uuid4()

        courier.take_order(first_order, 10)
        result: typing.Final = courier.take_order(second_order, 50)

        assert result.is_success
        assert courier.storage_places[0].order_id == first_order
        assert courier.storage_places[1].order_id == second_order

    def test_take_order_no_available_storage(self) -> None:
        location: typing.Final = Location.must_create(5, 5)
        courier: typing.Final = Courier.must_create("Иван", 2, location)
        order_id: typing.Final = uuid4()

        result: typing.Final = courier.take_order(order_id, 100)

        assert result.is_failure
        error: typing.Final = result.get_error()
        assert "courier.no.available.storage" in error.code

    def test_take_order_all_occupied(self) -> None:
        location: typing.Final = Location.must_create(5, 5)
        courier: typing.Final = Courier.must_create("Иван", 2, location)
        first_order: typing.Final = uuid4()
        second_order: typing.Final = uuid4()

        courier.take_order(first_order, 10)
        result: typing.Final = courier.take_order(second_order, 5)

        assert result.is_failure
        error: typing.Final = result.get_error()
        assert "courier.no.available.storage" in error.code

    @pytest.mark.parametrize(
        ("order_volume", "error_code_fragment"),
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
    def test_take_order_invalid_volume(self, order_volume: int, error_code_fragment: str) -> None:
        location: typing.Final = Location.must_create(5, 5)
        courier: typing.Final = Courier.must_create("[ИМЯ_3336]", 2, location)
        order_id: typing.Final = uuid4()

        result: typing.Final = courier.take_order(order_id, order_volume)

        assert result.is_failure
        error: typing.Final = result.get_error()
        assert error_code_fragment in error.code


class TestCourierCompleteOrder:
    def test_complete_order_success(self) -> None:
        location: typing.Final = Location.must_create(5, 5)
        courier: typing.Final = Courier.must_create("Иван", 2, location)
        order_id: typing.Final = uuid4()

        courier.take_order(order_id, 8)
        result: typing.Final = courier.complete_order(order_id)

        assert result.is_success
        assert not courier.storage_places[0].is_occupied()
        assert courier.storage_places[0].order_id is None

    def test_complete_order_not_found(self) -> None:
        location: typing.Final = Location.must_create(5, 5)
        courier: typing.Final = Courier.must_create("Иван", 2, location)
        order_id: typing.Final = uuid4()

        result: typing.Final = courier.complete_order(order_id)

        assert result.is_failure
        error: typing.Final = result.get_error()
        assert "courier.order.not.found" in error.code

    def test_complete_order_from_multiple_storage(self) -> None:
        location: typing.Final = Location.must_create(5, 5)
        courier: typing.Final = Courier.must_create("Иван", 2, location)
        courier.add_storage_place("Рюкзак", 50)
        courier.add_storage_place("Багажник", 100)
        order1: typing.Final = uuid4()
        order2: typing.Final = uuid4()

        courier.take_order(order1, 10)
        courier.take_order(order2, 30)

        result: typing.Final = courier.complete_order(order1)

        assert result.is_success
        assert not courier.storage_places[0].is_occupied()
        assert courier.storage_places[1].is_occupied()


class TestCourierCalculateTimeToLocation:
    @pytest.mark.parametrize(
        ("courier_x", "courier_y", "target_x", "target_y", "speed", "expected_time"),
        [
            (1, 1, 5, 5, 2, 4),
            (1, 1, 1, 1, 2, 0),
            (1, 1, 3, 3, 1, 4),
            (1, 1, 10, 10, 3, 6),
            (5, 5, 1, 1, 2, 4),
            (1, 1, 2, 1, 1, 1),
            (1, 1, 1, 3, 1, 2),
        ],
        ids=[
            "example_from_spec",
            "same_location",
            "slow_courier",
            "fast_courier",
            "reverse_direction",
            "horizontal_move",
            "vertical_move",
        ],
    )
    def test_calculate_time_to_location(
        self,
        courier_x: int,
        courier_y: int,
        target_x: int,
        target_y: int,
        speed: int,
        expected_time: int,
    ) -> None:
        courier_location: typing.Final = Location.must_create(courier_x, courier_y)
        target_location: typing.Final = Location.must_create(target_x, target_y)
        courier: typing.Final = Courier.must_create("Иван", speed, courier_location)

        time: typing.Final = courier.calculate_time_to_location(target_location)

        assert time == expected_time


class TestCourierMove:
    def test_move_towards_target(self) -> None:
        location: typing.Final = Location.must_create(1, 1)
        target: typing.Final = Location.must_create(5, 5)
        courier: typing.Final = Courier.must_create("Иван", 2, location)

        result: typing.Final = courier.move(target)

        assert result.is_success
        assert courier.location.x == 3
        assert courier.location.y == 1

    def test_move_with_high_speed(self) -> None:
        location: typing.Final = Location.must_create(1, 1)
        target: typing.Final = Location.must_create(5, 5)
        courier: typing.Final = Courier.must_create("Иван", 10, location)

        result: typing.Final = courier.move(target)

        assert result.is_success
        assert courier.location.x == 5
        assert courier.location.y == 5

    def test_move_already_at_target(self) -> None:
        location: typing.Final = Location.must_create(5, 5)
        target: typing.Final = Location.must_create(5, 5)
        courier: typing.Final = Courier.must_create("Иван", 2, location)

        result: typing.Final = courier.move(target)

        assert result.is_success
        assert courier.location.x == 5
        assert courier.location.y == 5

    def test_move_with_none_target(self) -> None:
        location: typing.Final = Location.must_create(5, 5)
        courier: typing.Final = Courier.must_create("Иван", 2, location)

        result: typing.Final = courier.move(None)  # type: ignore[arg-type]

        assert result.is_failure
        error: typing.Final = result.get_error()
        assert "value.is.required" in error.code

    def test_move_out_of_bounds(self) -> None:
        location: typing.Final = Location.must_create(10, 10)
        target: typing.Final = Location.must_create(1, 1)
        courier: typing.Final = Courier.must_create("Иван", 5, location)

        result: typing.Final = courier.move(target)

        assert result.is_success
        assert courier.location.x == 5
        assert courier.location.y == 10


class TestCourierWorkflow:
    def test_full_courier_workflow(self) -> None:
        location: typing.Final = Location.must_create(1, 1)
        courier: typing.Final = Courier.must_create("Иван", 2, location)

        courier.add_storage_place("Рюкзак", 50)
        assert len(courier.storage_places) == 2

        order_id: typing.Final = uuid4()
        assert courier.can_take_order(30)

        take_result: typing.Final = courier.take_order(order_id, 30)
        assert take_result.is_success
        assert not courier.can_take_order(30)

        target: typing.Final = Location.must_create(5, 5)
        time: typing.Final = courier.calculate_time_to_location(target)
        assert time == 4

        for _ in range(time):
            move_result = courier.move(target)
            assert move_result.is_success

        assert courier.location == target

        complete_result: typing.Final = courier.complete_order(order_id)
        assert complete_result.is_success
        assert courier.can_take_order(30)
