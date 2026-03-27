import logging
import typing

from apscheduler.schedulers.asyncio import AsyncIOScheduler  # type: ignore[import-untyped]
from apscheduler.triggers.interval import IntervalTrigger  # type: ignore[import-untyped]

from delivery.adapters.input.scheduler.jobs.assign_orders_job import AssignOrdersJob
from delivery.adapters.input.scheduler.jobs.move_couriers_job import MoveCouriersJob
from delivery.core.application.commands.assign_order_to_courier import AssignOrderToCourierCommandHandler
from delivery.core.application.commands.move_couriers import MoveCouriersCommandHandler


logger = logging.getLogger(__name__)


def create_scheduler(
    assign_orders_handler: AssignOrderToCourierCommandHandler,
    move_couriers_handler: MoveCouriersCommandHandler,
) -> AsyncIOScheduler:
    scheduler: typing.Final = AsyncIOScheduler()

    assign_orders_job: typing.Final = AssignOrdersJob(assign_orders_handler)
    move_couriers_job: typing.Final = MoveCouriersJob(move_couriers_handler)

    scheduler.add_job(
        assign_orders_job.run,
        trigger=IntervalTrigger(seconds=1),
        id="assign_orders_job",
        name="Assign Orders to Couriers",
        replace_existing=True,
    )

    scheduler.add_job(
        move_couriers_job.run,
        trigger=IntervalTrigger(seconds=1),
        id="move_couriers_job",
        name="Move Couriers",
        replace_existing=True,
    )

    return scheduler
