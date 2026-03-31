from abc import ABC, abstractmethod

from delivery.libs.ddd.events import DomainEvent


class OrderEventsProducer(ABC):
    @abstractmethod
    async def publish(self, events: list[DomainEvent]) -> None: ...
