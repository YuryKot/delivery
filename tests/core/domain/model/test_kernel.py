import typing

import pytest

from delivery.core.domain.model.kernel import Location
from delivery.libs.errs.error import DomainInvariantError


class TestLocationCreation:
    @pytest.mark.parametrize(
        ("x", "y", "expected_x", "expected_y"),
        [
            (1, 1, 1, 1),
            (10, 10, 10, 10),
            (5, 7, 5, 7),
            (1, 10, 1, 10),
            (10, 1, 10, 1),
        ],
        ids=[
            "min_coordinates",
            "max_coordinates",
            "middle_coordinates",
            "x_min_y_max",
            "x_max_y_min",
        ],
    )
    def test_create_valid_location(self, x: int, y: int, expected_x: int, expected_y: int) -> None:
        result: typing.Final = Location.create(x, y)

        assert result.is_success
        location: typing.Final = result.get_value()
        assert location.x == expected_x
        assert location.y == expected_y

    @pytest.mark.parametrize(
        ("x", "y", "error_description"),
        [
            (0, 5, "X меньше минимума"),
            (11, 5, "X больше максимума"),
            (5, 0, "Y меньше минимума"),
            (5, 11, "Y больше максимума"),
            (0, 0, "Обе координаты меньше минимума"),  # noqa: RUF001
            (11, 11, "Обе координаты больше максимума"),  # noqa: RUF001
            (0, 11, "X меньше минимума, Y больше максимума"),
            (-1, 5, "X отрицательный"),
            (5, -1, "Y отрицательный"),
        ],
        ids=[
            "x_less_than_min",
            "x_greater_than_max",
            "y_less_than_min",
            "y_greater_than_max",
            "both_less_than_min",
            "both_greater_than_max",
            "x_min_y_max_violation",
            "x_negative",
            "y_negative",
        ],
    )
    def test_create_invalid_location(self, x: int, y: int, error_description: str) -> None:
        result: typing.Final = Location.create(x, y)

        assert result.is_failure, error_description
        error: typing.Final = result.get_error()
        assert "out.of.range" in error.code

    @pytest.mark.parametrize(
        ("x", "y"),
        [
            (1, 1),
            (5, 5),
            (10, 10),
            (3, 7),
        ],
    )
    def test_must_create_valid_location(self, x: int, y: int) -> None:
        location: typing.Final = Location.must_create(x, y)

        assert location.x == x
        assert location.y == y

    @pytest.mark.parametrize(
        ("x", "y"),
        [
            (0, 5),
            (11, 5),
            (5, 0),
            (5, 11),
            (-1, -1),
        ],
    )
    def test_must_create_invalid_location_raises_exception(self, x: int, y: int) -> None:
        with pytest.raises(DomainInvariantError) as exc_info:
            Location.must_create(x, y)

        assert "out.of.range" in exc_info.value.error.code


class TestLocationEquality:
    @pytest.mark.parametrize(
        ("x1", "y1", "x2", "y2", "should_be_equal"),
        [
            (5, 5, 5, 5, True),
            (1, 1, 1, 1, True),
            (10, 10, 10, 10, True),
            (5, 5, 6, 5, False),
            (5, 5, 5, 6, False),
            (5, 5, 6, 6, False),
            (1, 10, 10, 1, False),
        ],
        ids=[
            "same_coordinates",
            "same_min",
            "same_max",
            "different_x",
            "different_y",
            "both_different",
            "inverted",
        ],
    )
    def test_location_equality(self, x1: int, y1: int, x2: int, y2: int, should_be_equal: bool) -> None:
        location1: typing.Final = Location.must_create(x1, y1)
        location2: typing.Final = Location.must_create(x2, y2)

        if should_be_equal:
            assert location1 == location2
            assert location2 == location1
            assert hash(location1) == hash(location2)
        else:
            assert location1 != location2
            assert location2 != location1


class TestLocationDistance:
    """Тесты расчета расстояния между Location."""

    @pytest.mark.parametrize(
        ("x1", "y1", "x2", "y2", "expected_distance"),
        [
            (5, 5, 5, 5, 0),
            (1, 1, 1, 1, 0),
            (10, 10, 10, 10, 0),
            (1, 5, 5, 5, 4),
            (5, 1, 5, 5, 4),
            (1, 1, 5, 5, 8),
            (1, 1, 10, 10, 18),
            (3, 7, 8, 2, 10),
            (2, 3, 7, 9, 11),
            (10, 1, 1, 10, 18),
        ],
        ids=[
            "same_location",
            "same_location_min",
            "same_location_max",
            "horizontal_only",
            "vertical_only",
            "diagonal_simple",
            "max_corners",
            "complex_case_1",
            "complex_case_2",
            "diagonal_inverse",
        ],
    )
    def test_distance_calculation(self, x1: int, y1: int, x2: int, y2: int, expected_distance: int) -> None:
        location1: typing.Final = Location.must_create(x1, y1)
        location2: typing.Final = Location.must_create(x2, y2)

        distance: typing.Final = location1.distance_to(location2)

        assert distance == expected_distance
