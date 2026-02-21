import typing
from collections.abc import Callable

from delivery.libs.errs.error import DomainInvariantError, Error


T = typing.TypeVar("T")
U = typing.TypeVar("U")
E = typing.TypeVar("E", bound=Error)
F = typing.TypeVar("F", bound=Error)


class Result[T, E: Error]:
    def __init__(self, value: T | None, error: E | None, is_success: bool) -> None:
        self._value = value
        self._error = error
        self._is_success = is_success

    @staticmethod
    def success(value: T) -> "Result[T, E]":
        if value is None:
            msg: typing.Final = "Value must not be None for success"
            raise ValueError(msg)
        return Result(value, None, True)

    @staticmethod
    def success_empty() -> "Result[None, E]":
        return Result(None, None, True)

    @staticmethod
    def failure(error: E) -> "Result[T, E]":
        if error is None:
            msg: typing.Final = "Error must not be None for failure"
            raise ValueError(msg)
        return Result(None, error, False)

    @property
    def is_success(self) -> bool:
        return self._is_success

    @property
    def is_failure(self) -> bool:
        return not self._is_success

    def get_value(self) -> T:
        if not self._is_success:
            msg: typing.Final = "Cannot get value from failure"
            raise ValueError(msg)
        return typing.cast("T", self._value)

    def get_error(self) -> E:
        if self._is_success:
            msg: typing.Final = "Cannot get error from success"
            raise ValueError(msg)
        return typing.cast("E", self._error)

    def map(self, mapper: Callable[[T], U]) -> "Result[U, E]":
        if self._is_success:
            return Result.success(mapper(typing.cast("T", self._value)))
        return Result.failure(typing.cast("E", self._error))

    def flat_map(self, mapper: Callable[[T], "Result[U, E]"]) -> "Result[U, E]":
        if self._is_success:
            return mapper(typing.cast("T", self._value))
        return Result.failure(typing.cast("E", self._error))

    def on_success(self, handler: Callable[[T], None]) -> "Result[T, E]":
        if self._is_success:
            handler(typing.cast("T", self._value))
        return self

    def on_failure(self, handler: Callable[[E], None]) -> "Result[T, E]":
        if self.is_failure:
            handler(typing.cast("E", self._error))
        return self

    def fold(self, on_success: Callable[[T], U], on_failure: Callable[[E], U]) -> U:
        if self._is_success:
            return on_success(typing.cast("T", self._value))
        return on_failure(typing.cast("E", self._error))

    def map_error(self, mapper: Callable[[E], F]) -> "Result[T, F]":
        if self._is_success:
            return Result.success(typing.cast("T", self._value))
        return Result.failure(mapper(typing.cast("E", self._error)))

    def get_value_or_throw(self) -> T:
        if self._is_success:
            return typing.cast("T", self._value)
        raise DomainInvariantError(typing.cast("E", self._error))

    def __str__(self) -> str:
        if self._is_success:
            return f"Success({self._value})"
        return f"Failure({self._error})"


class UnitResult[E: Error]:
    def __init__(self, is_success: bool, error: E | None) -> None:
        self._is_success = is_success
        self._error = error

    @staticmethod
    def success() -> "UnitResult[E]":
        return UnitResult(True, None)

    @staticmethod
    def failure(error: E) -> "UnitResult[E]":
        if error is None:
            msg: typing.Final = "Error must not be None on failure"
            raise ValueError(msg)
        return UnitResult(False, error)

    @property
    def is_success(self) -> bool:
        return self._is_success

    @property
    def is_failure(self) -> bool:
        return not self._is_success

    def get_error(self) -> E:
        if self._is_success:
            msg: typing.Final = "Cannot get error from success"
            raise ValueError(msg)
        return typing.cast("E", self._error)

    def on_success(self, handler: Callable[[], None]) -> "UnitResult[E]":
        if self._is_success:
            handler()
        return self

    def on_failure(self, handler: Callable[[E], None]) -> "UnitResult[E]":
        if self.is_failure:
            handler(typing.cast("E", self._error))
        return self

    def fold(self, on_success: Callable[[], U], on_failure: Callable[[E], U]) -> U:
        if self._is_success:
            return on_success()
        return on_failure(typing.cast("E", self._error))

    def merge(self, other: "UnitResult[E]") -> "UnitResult[E]":
        if self.is_failure:
            return self
        if other.is_failure:
            return other
        return UnitResult.success()

    @staticmethod
    def from_result(result: Result[None, E]) -> "UnitResult[E]":
        if result.is_success:
            return UnitResult.success()
        return UnitResult.failure(result.get_error())

    def to_result(self) -> Result[None, E]:
        if self.is_failure:
            return Result.failure(typing.cast("E", self._error))
        return Result.success_empty()

    def get_or_else_throw(self, exception_mapper: Callable[[E], Exception] | None = None) -> None:
        if self._is_success:
            return

        if exception_mapper is not None:
            raise exception_mapper(typing.cast("E", self._error))

        raise DomainInvariantError(typing.cast("E", self._error))

    def __str__(self) -> str:
        if self._is_success:
            return "Success"
        return f"Failure({self._error})"
