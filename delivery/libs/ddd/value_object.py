import typing
from abc import ABC, abstractmethod
from decimal import Decimal
from typing import Protocol


class Comparable(Protocol):
    def __lt__(self, other: typing.Any) -> bool: ...  # noqa: ANN401

    def __le__(self, other: typing.Any) -> bool: ...  # noqa: ANN401

    def __gt__(self, other: typing.Any) -> bool: ...  # noqa: ANN401

    def __ge__(self, other: typing.Any) -> bool: ...  # noqa: ANN401


class ValueObject[T](ABC):
    @abstractmethod
    def equality_components(self) -> typing.Iterable[object]: ...

    @staticmethod
    def _safe_compare(a: object, b: object) -> int:  # noqa: PLR0911
        if a is b:
            return 0
        if a is None:
            return -1
        if b is None:
            return 1

        if isinstance(a, Decimal) and isinstance(b, Decimal):
            if a < b:
                return -1
            if a > b:
                return 1
            return 0

        if not (hasattr(a, "__lt__") and hasattr(b, "__lt__")):
            msg: typing.Final = "Fields must be Comparable"
            raise TypeError(msg)

        a_comp: typing.Final = typing.cast("Comparable", a)
        b_comp: typing.Final = typing.cast("Comparable", b)

        if a_comp < b_comp:
            return -1
        if a_comp > b_comp:
            return 1
        return 0

    def __eq__(self, other: object) -> bool:
        if self is other:
            return True
        if other is None or type(self) is not type(other):
            return False

        other_vo: typing.Final = typing.cast("ValueObject[typing.Any]", other)
        this_components: typing.Final = list(self.equality_components())
        that_components: typing.Final = list(other_vo.equality_components())

        if len(this_components) != len(that_components):
            return False

        return all(a == b for a, b in zip(this_components, that_components, strict=True))

    def __hash__(self) -> int:
        return hash(tuple(self.equality_components()))

    def __lt__(self, other: T) -> bool:
        if not isinstance(other, type(self)):
            return NotImplemented

        this_components: typing.Final = list(self.equality_components())
        other_components: typing.Final = list(other.equality_components())

        for a, b in zip(this_components, other_components, strict=False):
            result = self._safe_compare(a, b)
            if result != 0:
                return result < 0

        return len(this_components) < len(other_components)

    def __le__(self, other: T) -> bool:
        return self == other or self < other

    def __gt__(self, other: T) -> bool:
        if not isinstance(other, type(self)):
            return NotImplemented
        is_equal: typing.Final = self == other
        is_less: typing.Final = self.__lt__(other)  # type: ignore[operator]
        return not (is_equal or is_less)

    def __ge__(self, other: T) -> bool:
        return not self.__lt__(other)

    def __str__(self) -> str:
        components: typing.Final = list(self.equality_components())
        components_str: typing.Final = ", ".join(str(c) for c in components)
        return f"{type(self).__name__}[{components_str}]"
