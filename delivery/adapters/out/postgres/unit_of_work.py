import sqlalchemy.ext.asyncio as sa_async

from delivery.core.ports.unit_of_work import UnitOfWork


class UnitOfWorkImpl(UnitOfWork):
    def __init__(self, session: sa_async.AsyncSession) -> None:
        self._session = session

    async def commit(self) -> None:
        await self._session.commit()

    async def rollback(self) -> None:
        await self._session.rollback()
