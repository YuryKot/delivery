import typing

from delivery.libs.errs.error import Error


class GeneralErrors:
    @staticmethod
    def not_found(name: str, id_: typing.Any) -> Error:  # noqa: ANN401
        if not name or not name.strip():
            msg: typing.Final = "Name must not be null or empty"
            raise ValueError(msg)

        return Error.of("record.not.found", f"Record not found. Name: {name}, id: {id_}")

    @staticmethod
    def value_is_invalid(name: str, value: typing.Any) -> Error:  # noqa: ANN401
        if not name or not name.strip():
            msg: typing.Final = "Name must not be null or empty"
            raise ValueError(msg)

        return Error.of("value.is.invalid", f"Value '{value}' is invalid for {name}")

    @staticmethod
    def value_is_required(name: str) -> Error:
        if not name or not name.strip():
            msg: typing.Final = "Name must not be null or empty"
            raise ValueError(msg)

        return Error.of("value.is.required", f"Value is required for {name}")

    @staticmethod
    def invalid_length(name: str) -> Error:
        if not name or not name.strip():
            msg: typing.Final = "Name must not be null or empty"
            raise ValueError(msg)

        return Error.of("invalid.string.length", f"Invalid {name} length")

    @staticmethod
    def collection_is_too_small(min_size: int, current: int) -> Error:
        return Error.of(
            "collection.is.too.small",
            f"The collection must contain {min_size} items or more. It contains {current} items.",
        )

    @staticmethod
    def collection_is_too_large(max_size: int, current: int) -> Error:
        return Error.of(
            "collection.is.too.large",
            f"The collection must contain {max_size} items or fewer. It contains {current} items.",
        )

    @staticmethod
    def value_is_out_of_range(name: str, value: typing.Any, min_value: typing.Any, max_value: typing.Any) -> Error:  # noqa: ANN401
        if not name or not name.strip():
            msg: typing.Final = "Name must not be null or empty"
            raise ValueError(msg)

        message: typing.Final = (
            f"Value {value} for {name} is out of range. Min value is {min_value}, max value is {max_value}."
        )

        return Error.of("value.is.out.of.range", message)

    @staticmethod
    def value_must_be_greater_than(name: str, value: typing.Any, min_value: typing.Any) -> Error:  # noqa: ANN401
        if not name or not name.strip():
            msg: typing.Final = "Name must not be null or empty"
            raise ValueError(msg)

        return Error.of(
            "value.must.be.greater.than",
            f"The value of {name} ({value}) must be greater than {min_value}.",
        )

    @staticmethod
    def value_must_be_greater_or_equal(name: str, value: typing.Any, min_value: typing.Any) -> Error:  # noqa: ANN401
        if not name or not name.strip():
            msg: typing.Final = "Name must not be null or empty"
            raise ValueError(msg)

        return Error.of(
            "value.must.be.greater.or.equal",
            f"The value of {name} ({value}) must be greater than or equal to {min_value}.",
        )

    @staticmethod
    def value_must_be_less_than(name: str, value: typing.Any, max_value: typing.Any) -> Error:  # noqa: ANN401
        if not name or not name.strip():
            msg: typing.Final = "Name must not be null or empty"
            raise ValueError(msg)

        return Error.of(
            "value.must.be.less.than",
            f"The value of {name} ({value}) must be less than {max_value}.",
        )

    @staticmethod
    def value_must_be_less_or_equal(name: str, value: typing.Any, max_value: typing.Any) -> Error:  # noqa: ANN401
        if not name or not name.strip():
            msg: typing.Final = "Name must not be null or empty"
            raise ValueError(msg)

        return Error.of(
            "value.must.be.less.or.equal",
            f"The value of {name} ({value}) must be less than or equal to {max_value}.",
        )
