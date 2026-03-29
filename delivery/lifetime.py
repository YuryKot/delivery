import contextlib
import logging
import typing

import fastapi

from delivery.adapters.input.scheduler import create_scheduler
from delivery.ioc import IOCContainer
from delivery.kafka import create_kafka_broker, setup_kafka_broker


logger = logging.getLogger(__name__)


@contextlib.asynccontextmanager
async def run_lifespan(application: fastapi.FastAPI) -> typing.AsyncIterator[None]:
    assign_orders_handler: typing.Final = await IOCContainer.app_assign_order_to_courier_handler()
    move_couriers_handler: typing.Final = await IOCContainer.app_move_couriers_handler()

    scheduler: typing.Final = create_scheduler(assign_orders_handler, move_couriers_handler)
    scheduler.start()

    kafka_broker: typing.Final = create_kafka_broker()
    setup_kafka_broker(application, kafka_broker)

    try:
        yield
    finally:
        scheduler.shutdown()
        await kafka_broker.close()
        await IOCContainer.tear_down()
