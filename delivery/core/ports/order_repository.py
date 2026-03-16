from abc import ABC, abstractmethod
from uuid import UUID

from delivery.core.domain.model.order.order import Order


class OrderRepository(ABC):
    @abstractmethod
    async def add(self, order: Order) -> None: ...

    @abstractmethod
    async def update(self, order: Order) -> None: ...

    @abstractmethod
    async def get_by_id(self, order_id: UUID) -> Order | None: ...

    @abstractmethod
    async def get_first_by_status_created(self) -> Order | None: ...

    @abstractmethod
    async def get_all_assigned(self) -> list[Order]: ...
