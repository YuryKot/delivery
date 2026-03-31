import typing
import uuid
from abc import ABC, abstractmethod
from datetime import UTC, datetime

from pydantic import BaseModel


if typing.TYPE_CHECKING:
    from delivery.libs.ddd.aggregate import Aggregate


class DomainEvent(BaseModel):
    event_id: uuid.UUID
    occurred_on_utc: datetime

    model_config = {"arbitrary_types_allowed": True}

    def __init__(self, **kwargs: typing.Any) -> None:
        super().__init__(
            event_id=kwargs.pop("event_id", uuid.uuid4()),
            occurred_on_utc=kwargs.pop("occurred_on_utc", datetime.now(UTC)),
            **kwargs,
        )


class DomainEventPublisher(ABC):
    @abstractmethod
    async def publish(self, aggregates: typing.Iterable["Aggregate[typing.Any]"]) -> None: ...
