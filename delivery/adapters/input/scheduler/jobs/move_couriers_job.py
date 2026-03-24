import logging
import typing

from delivery.core.application.commands.move_couriers import (
    MoveCouriersCommand,
    MoveCouriersCommandHandler,
)


logger = logging.getLogger(__name__)


class MoveCouriersJob:
    def __init__(self, handler: MoveCouriersCommandHandler) -> None:
        self._handler = handler

    async def run(self) -> None:
        try:
            command: typing.Final = MoveCouriersCommand()
            result: typing.Final = await self._handler.handle(command)
            if result.is_failure:
                error: typing.Final = result.get_error()
                logger.warning("MoveCouriersJob failed: %s - %s", error.code, error.message)
        except Exception:
            logger.exception("MoveCouriersJob unexpected error")
