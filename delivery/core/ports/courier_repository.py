from abc import ABC, abstractmethod
from uuid import UUID

from delivery.core.domain.model.courier.courier import Courier


class CourierRepository(ABC):
    @abstractmethod
    async def add(self, courier: Courier) -> None: ...

    @abstractmethod
    async def update(self, courier: Courier) -> None: ...

    @abstractmethod
    async def get_by_id(self, courier_id: UUID) -> Courier | None: ...

    @abstractmethod
    async def get_all_free(self) -> list[Courier]: ...
