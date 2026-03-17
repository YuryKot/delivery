from abc import ABC, abstractmethod

from delivery.libs.errs.error import Error
from delivery.libs.errs.result import Result
from .dto import IncompleteOrderDto
from .query import GetAllIncompleteOrdersQuery


class GetAllIncompleteOrdersQueryHandler(ABC):
    @abstractmethod
    async def handle(self, query: GetAllIncompleteOrdersQuery) -> Result[list[IncompleteOrderDto], Error]:
        pass
