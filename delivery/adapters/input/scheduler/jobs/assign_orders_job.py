import logging
import typing

from delivery.core.application.commands.assign_order_to_courier import (
    AssignOrderToCourierCommand,
    AssignOrderToCourierCommandHandler,
)


logger = logging.getLogger(__name__)


class AssignOrdersJob:
    def __init__(self, handler: AssignOrderToCourierCommandHandler) -> None:
        self._handler = handler

    async def run(self) -> None:
        try:
            command: typing.Final = AssignOrderToCourierCommand()
            result: typing.Final = await self._handler.handle(command)
            if result.is_failure:
                error: typing.Final = result.get_error()
                logger.warning("AssignOrdersJob failed: %s - %s", error.code, error.message)
        except Exception:
            logger.exception("AssignOrdersJob unexpected error")
