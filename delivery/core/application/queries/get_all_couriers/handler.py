from abc import ABC, abstractmethod

from delivery.libs.errs.error import Error
from delivery.libs.errs.result import Result
from .dto import CourierDto
from .query import GetAllCouriersQuery


class GetAllCouriersQueryHandler(ABC):
    @abstractmethod
    async def handle(self, query: GetAllCouriersQuery) -> Result[list[CourierDto], Error]:
        pass
