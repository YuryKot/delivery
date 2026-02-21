import typing


class Error:
    _SEPARATOR: typing.Final[str] = "||"

    def __init__(self, code: str, message: str) -> None:
        if not code:
            msg = "Code must not be empty"
            raise ValueError(msg)
        if not message:
            msg = "Message must not be empty"
            raise ValueError(msg)

        self._code = code
        self._message = message

    @staticmethod
    def of(code: str, message: str) -> "Error":
        return Error(code, message)

    @property
    def code(self) -> str:
        return self._code

    @property
    def message(self) -> str:
        return self._message

    def serialize(self) -> str:
        return f"{self._code}{self._SEPARATOR}{self._message}"

    @staticmethod
    def deserialize(serialized: str) -> "Error":
        if serialized == "A non-empty request body is required.":
            from delivery.libs.errs.general_errors import GeneralErrors  # noqa: PLC0415

            return GeneralErrors.value_is_required("serialized")

        parts: typing.Final = serialized.split("||")

        if len(parts) < 2:  # noqa: PLR2004
            msg: typing.Final = f"Invalid error serialization: '{serialized}'"
            raise ValueError(msg)

        return Error(parts[0], parts[1])

    @staticmethod
    def throw_if(error: "Error | None") -> None:
        if error is not None:
            raise DomainInvariantError(error)

    def __eq__(self, other: object) -> bool:
        if not isinstance(other, Error):
            return False
        return self._code == other._code and self._message == other._message

    def __hash__(self) -> int:
        return hash((self._code, self._message))

    def __str__(self) -> str:
        return f"Error{{code='{self._code}', message='{self._message}'}}"


class DomainInvariantError(Exception):
    def __init__(self, error: Error) -> None:
        super().__init__(f"Domain invariant violated: {error.message}")
        self.error = error
