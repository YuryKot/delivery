import typing
from datetime import datetime
from uuid import UUID

import sqlalchemy
import sqlalchemy.ext.asyncio as sa_async
from advanced_alchemy.repository import SQLAlchemyAsyncRepository

from delivery.core.ports.outbox_repository import OutboxRepository
from delivery.database.models import OutboxMessageModel


class _OutboxAlchemyRepository(SQLAlchemyAsyncRepository[OutboxMessageModel]):  # type: ignore[type-var]
    model_type = OutboxMessageModel


class OutboxRepositoryImpl(OutboxRepository):
    def __init__(self, session: sa_async.AsyncSession) -> None:
        self._repo: typing.Final = _OutboxAlchemyRepository(session=session)

    async def add(  # noqa: PLR0913
        self,
        event_id: UUID,
        event_type: str,
        aggregate_id: UUID,
        aggregate_type: str,
        payload: str,
        occurred_on_utc: datetime,
    ) -> None:
        model: typing.Final = OutboxMessageModel(
            id=event_id,
            event_type=event_type,
            aggregate_id=aggregate_id,
            aggregate_type=aggregate_type,
            payload=payload,
            occurred_on_utc=occurred_on_utc,
            processed_on_utc=None,
        )
        await self._repo.add(model, auto_commit=False)

    async def find_unprocessed_messages(self) -> list[OutboxMessageModel]:
        result: typing.Final = await self._repo.session.execute(
            sqlalchemy.select(OutboxMessageModel).where(OutboxMessageModel.processed_on_utc.is_(None))
        )
        return list(result.scalars().all())

    async def mark_as_processed(self, event_id: UUID) -> None:
        model: typing.Final = await self._repo.get_one_or_none(id=event_id)
        if model is not None:
            model.processed_on_utc = datetime.now(tz=datetime.now().astimezone().tzinfo)
            await self._repo.session.commit()
