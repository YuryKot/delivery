import typing
import uuid
from collections.abc import Collection
from typing import Protocol

from delivery.libs.errs.error import Error
from delivery.libs.errs.general_errors import GeneralErrors


class Comparable(Protocol):
    def __lt__(self, other: typing.Any) -> bool: ...

    def __le__(self, other: typing.Any) -> bool: ...

    def __gt__(self, other: typing.Any) -> bool: ...

    def __ge__(self, other: typing.Any) -> bool: ...


class Guard:
    _EMPTY_UUID: typing.Final[uuid.UUID] = uuid.UUID("00000000-0000-0000-0000-000000000000")

    @staticmethod
    def combine(*errors: Error | None) -> Error | None:
        for error in errors:
            if error is not None:
                return error
        return None

    @staticmethod
    def against_null_or_empty(value: str | None, param_name: str) -> Error | None:
        if value is None or not value.strip():
            return GeneralErrors.value_is_required(param_name)
        return None

    @staticmethod
    def against_null_or_empty_collection(collection: Collection[typing.Any] | None, param_name: str) -> Error | None:
        """Проверяет, что коллекция не None и не пустая."""
        if collection is None or len(collection) == 0:
            return GeneralErrors.value_is_required(param_name)
        return None

    @staticmethod
    def against_null_or_empty_uuid(value: uuid.UUID | None, param_name: str) -> Error | None:
        if value is None or value == Guard._EMPTY_UUID:
            return GeneralErrors.value_is_required(param_name)
        return None

    @staticmethod
    def against_greater_than(value: Comparable | None, max_value: Comparable, param_name: str) -> Error | None:
        if value is None or value > max_value:
            return GeneralErrors.value_must_be_less_than(param_name, value, max_value)
        return None

    @staticmethod
    def against_greater_or_equal(value: Comparable | None, max_value: Comparable, param_name: str) -> Error | None:
        if value is None or value >= max_value:
            return GeneralErrors.value_must_be_less_or_equal(param_name, value, max_value)
        return None

    @staticmethod
    def against_less_than(value: Comparable | None, min_value: Comparable, param_name: str) -> Error | None:
        if value is None or value < min_value:
            return GeneralErrors.value_must_be_greater_than(param_name, value, min_value)
        return None

    @staticmethod
    def against_less_or_equal(value: Comparable | None, min_value: Comparable, param_name: str) -> Error | None:
        if value is None or value <= min_value:
            return GeneralErrors.value_must_be_greater_or_equal(param_name, value, min_value)
        return None

    @staticmethod
    def against_out_of_range(
        value: Comparable | None,
        min_value: Comparable,
        max_value: Comparable,
        param_name: str,
    ) -> Error | None:
        if value is None or value < min_value or value > max_value:
            return GeneralErrors.value_is_out_of_range(param_name, value, min_value, max_value)
        return None
