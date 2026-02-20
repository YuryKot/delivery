import typing
from abc import ABC
from typing import Protocol


class Comparable(Protocol):
    def __lt__(self, other: typing.Any) -> bool: ...

    def __le__(self, other: typing.Any) -> bool: ...

    def __gt__(self, other: typing.Any) -> bool: ...

    def __ge__(self, other: typing.Any) -> bool: ...


TId = typing.TypeVar("TId", bound=Comparable)


class BaseEntity[TId: Comparable](ABC):
    def __init__(self, id_: TId | None = None) -> None:
        self.id: TId | None = id_

    def is_transient(self) -> bool:
        return self.id is None or self.id == self._default_value()

    def _default_value(self) -> TId | None:
        return None

    def __eq__(self, other: object) -> bool:
        if other is None:
            return False

        if self is other:
            return True

        if not isinstance(other, BaseEntity):
            return False

        if type(self) is not type(other):
            return False

        if self.is_transient() or other.is_transient():
            return False

        return self.id == other.id

    def __hash__(self) -> int:
        class_name: typing.Final = type(self).__name__
        id_str: typing.Final = str(self.id) if self.id is not None else ""
        return hash(class_name + id_str)

    def __lt__(self, other: typing.Self) -> bool:
        if other is None:
            return False

        if self is other:
            return False

        if self.id is None or other.id is None:
            return False

        return self.id < other.id

    def __le__(self, other: typing.Self) -> bool:
        return self < other or self == other

    def __gt__(self, other: typing.Self) -> bool:
        return not self <= other

    def __ge__(self, other: typing.Self) -> bool:
        return not self < other
