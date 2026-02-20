import typing
import uuid
from abc import ABC, abstractmethod
from datetime import UTC, datetime


if typing.TYPE_CHECKING:
    from delivery.libs.ddd.aggregate import Aggregate


class DomainEvent(ABC):
    def __init__(self, source: object | None = None) -> None:
        self.event_id: uuid.UUID = uuid.uuid4()
        self.occurred_on_utc: datetime = datetime.now(UTC)
        self._source: object | None = source


class DomainEventPublisher(ABC):
    @abstractmethod
    async def publish(self, aggregates: typing.Iterable["Aggregate[typing.Any]"]) -> None: ...
