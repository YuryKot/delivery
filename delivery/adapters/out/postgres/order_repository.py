import typing
from uuid import UUID

import sqlalchemy.ext.asyncio as sa_async
from advanced_alchemy.filters import CollectionFilter, LimitOffset
from advanced_alchemy.repository import SQLAlchemyAsyncRepository

from delivery.adapters.out.postgres.order_mapper import to_domain, to_model
from delivery.core.domain.model.order.order import Order
from delivery.core.domain.model.order.order_status import OrderStatus
from delivery.core.ports.order_repository import OrderRepository
from delivery.database.models import OrderModel


class _OrderAlchemyRepository(SQLAlchemyAsyncRepository[OrderModel]):  # type: ignore[type-var]
    model_type = OrderModel


class OrderRepositoryImpl(OrderRepository):
    def __init__(self, session: sa_async.AsyncSession) -> None:
        self._repo: typing.Final = _OrderAlchemyRepository(session=session)

    async def add(self, order: Order) -> None:
        await self._repo.add(to_model(order), auto_commit=True)

    async def update(self, order: Order) -> None:
        await self._repo.update(to_model(order), auto_commit=True)

    async def get_by_id(self, order_id: UUID) -> Order | None:
        model: typing.Final = await self._repo.get_one_or_none(id=order_id)
        if model is None:
            return None
        return to_domain(model)

    async def get_first_by_status_created(self) -> Order | None:
        results: typing.Final = await self._repo.list(
            CollectionFilter(field_name="status", values=[OrderStatus.CREATED.value]),
            LimitOffset(limit=1, offset=0),
        )
        if not results:
            return None
        return to_domain(results[0])

    async def get_all_assigned(self) -> list[Order]:
        results: typing.Final = await self._repo.list(
            CollectionFilter(field_name="status", values=[OrderStatus.ASSIGNED.value]),
        )
        return [to_domain(model) for model in results]
