from abc import ABC, abstractmethod

from delivery.libs.errs.error import Error
from delivery.libs.errs.result import UnitResult
from .command import CreateCourierCommand


class CreateCourierCommandHandler(ABC):
    @abstractmethod
    async def handle(self, command: CreateCourierCommand) -> UnitResult[Error]:
        pass
