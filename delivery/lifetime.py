import contextlib
import logging
import typing

import fastapi

from delivery.adapters.input.scheduler import create_scheduler
from delivery.ioc import IOCContainer
from delivery.kafka import setup_kafka_broker


logger = logging.getLogger(__name__)


@contextlib.asynccontextmanager
async def run_lifespan(application: fastapi.FastAPI) -> typing.AsyncIterator[None]:
    assign_orders_handler: typing.Final = await IOCContainer.app_assign_order_to_courier_handler()
    move_couriers_handler: typing.Final = await IOCContainer.app_move_couriers_handler()
    outbox_repository: typing.Final = await IOCContainer.app_outbox_repository()
    order_events_producer: typing.Final = await IOCContainer.order_events_producer()

    scheduler: typing.Final = create_scheduler(
        assign_orders_handler,
        move_couriers_handler,
        outbox_repository,
        order_events_producer,
    )
    scheduler.start()

    kafka_broker: typing.Final = await IOCContainer.kafka_broker()
    setup_kafka_broker(application, kafka_broker)

    await kafka_broker.start()

    try:
        yield
    finally:
        scheduler.shutdown()
        await kafka_broker.close()
        await IOCContainer.tear_down()
