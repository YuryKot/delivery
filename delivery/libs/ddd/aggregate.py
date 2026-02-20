import typing
from abc import ABC, abstractmethod

from delivery.libs.ddd.entity import BaseEntity, Comparable
from delivery.libs.ddd.events import DomainEvent


TId = typing.TypeVar("TId", bound=Comparable)


class AggregateRoot[TId](ABC):
    @abstractmethod
    def get_id(self) -> TId | None: ...

    @abstractmethod
    def get_domain_events(self) -> list[DomainEvent]: ...

    @abstractmethod
    def clear_domain_events(self) -> None: ...


class Aggregate[TId: Comparable](BaseEntity[TId], AggregateRoot[TId]):
    def __init__(self, id_: TId | None = None) -> None:
        super().__init__(id_)
        self._domain_events: list[DomainEvent] = []

    def get_id(self) -> TId | None:
        return self.id

    def get_domain_events(self) -> list[DomainEvent]:
        return self._domain_events.copy()

    def clear_domain_events(self) -> None:
        self._domain_events.clear()

    def raise_domain_event(self, domain_event: DomainEvent) -> None:
        self._domain_events.append(domain_event)
