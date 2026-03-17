from abc import ABC, abstractmethod

from delivery.libs.errs.error import Error
from delivery.libs.errs.result import UnitResult
from .command import AssignOrderToCourierCommand


class AssignOrderToCourierCommandHandler(ABC):
    @abstractmethod
    async def handle(self, command: AssignOrderToCourierCommand) -> UnitResult[Error]:
        pass
