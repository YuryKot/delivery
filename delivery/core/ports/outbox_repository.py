from abc import ABC, abstractmethod
from datetime import datetime
from uuid import UUID

from delivery.database.models import OutboxMessageModel


class OutboxRepository(ABC):
    @abstractmethod
    async def add(  # noqa: PLR0913
        self,
        event_id: UUID,
        event_type: str,
        aggregate_id: UUID,
        aggregate_type: str,
        payload: str,
        occurred_on_utc: datetime,
    ) -> None: ...

    @abstractmethod
    async def find_unprocessed_messages(self) -> list[OutboxMessageModel]: ...

    @abstractmethod
    async def mark_as_processed(self, event_id: UUID) -> None: ...
