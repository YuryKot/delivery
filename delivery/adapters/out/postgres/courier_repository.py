import typing
from uuid import UUID

import sqlalchemy
import sqlalchemy.ext.asyncio as sa_async
from advanced_alchemy.repository import SQLAlchemyAsyncRepository

from delivery.adapters.out.postgres.courier_mapper import to_domain, to_model
from delivery.core.domain.model.courier.courier import Courier
from delivery.core.ports.courier_repository import CourierRepository
from delivery.database.models import CourierModel, StoragePlaceModel


class _CourierAlchemyRepository(SQLAlchemyAsyncRepository[CourierModel]):  # type: ignore[type-var]
    model_type = CourierModel


class CourierRepositoryImpl(CourierRepository):
    def __init__(self, session: sa_async.AsyncSession) -> None:
        self._session: typing.Final = session
        self._repo: typing.Final = _CourierAlchemyRepository(session=session)

    async def add(self, courier: Courier) -> None:
        await self._repo.add(to_model(courier), auto_commit=False)

    async def update(self, courier: Courier) -> None:
        await self._session.merge(to_model(courier))

    async def get_by_id(self, courier_id: UUID) -> Courier | None:
        model: typing.Final = await self._repo.get_one_or_none(id=courier_id)
        if model is None:
            return None
        return to_domain(model)

    async def get_all_free(self) -> list[Courier]:
        # Get all courier IDs that have at least one storage place with an order
        occupied_courier_ids_subquery: typing.Final = (
            sqlalchemy.select(StoragePlaceModel.courier_id).where(StoragePlaceModel.order_id.is_not(None)).distinct()
        )
        stmt: typing.Final = sqlalchemy.select(CourierModel).where(~CourierModel.id.in_(occupied_courier_ids_subquery))
        result: typing.Final = await self._session.execute(stmt)
        models: typing.Final = result.scalars().unique().all()
        return [to_domain(m) for m in models]
