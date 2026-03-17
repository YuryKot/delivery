from abc import ABC, abstractmethod

from delivery.libs.errs.error import Error
from delivery.libs.errs.result import UnitResult
from .command import MoveCouriersCommand


class MoveCouriersCommandHandler(ABC):
    @abstractmethod
    async def handle(self, command: MoveCouriersCommand) -> UnitResult[Error]:
        pass
