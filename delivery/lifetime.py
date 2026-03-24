import contextlib
import logging
import typing

import fastapi

from delivery.adapters.input.scheduler import create_scheduler
from delivery.ioc import IOCContainer


logger = logging.getLogger(__name__)


@contextlib.asynccontextmanager
async def run_lifespan(_application: fastapi.FastAPI) -> typing.AsyncIterator[None]:
    assign_orders_handler: typing.Final = await IOCContainer.app_assign_order_to_courier_handler()
    move_couriers_handler: typing.Final = await IOCContainer.app_move_couriers_handler()

    scheduler: typing.Final = create_scheduler(assign_orders_handler, move_couriers_handler)
    scheduler.start()

    try:
        yield
    finally:
        scheduler.shutdown()
        await IOCContainer.tear_down()
