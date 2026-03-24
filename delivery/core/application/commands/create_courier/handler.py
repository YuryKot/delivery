from abc import ABC, abstractmethod
from uuid import UUID

from delivery.libs.errs.error import Error
from delivery.libs.errs.result import Result
from .command import CreateCourierCommand


class CreateCourierCommandHandler(ABC):
    @abstractmethod
    async def handle(self, command: CreateCourierCommand) -> Result[UUID, Error]:
        pass
