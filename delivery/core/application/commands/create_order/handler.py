from abc import ABC, abstractmethod

from delivery.libs.errs.error import Error
from delivery.libs.errs.result import UnitResult
from .command import CreateOrderCommand


class CreateOrderCommandHandler(ABC):
    @abstractmethod
    async def handle(self, command: CreateOrderCommand) -> UnitResult[Error]:
        pass
