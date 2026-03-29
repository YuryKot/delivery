import typing

import structlog

from delivery.adapters.input.kafka import baskets_events_pb2 as pb2
from delivery.adapters.input.kafka.mappers.basket_event_mapper import map_basket_confirmed_to_create_order_command
from delivery.core.application.commands.create_order.handler import CreateOrderCommandHandler
from delivery.core.ports.kafka_consumer import KafkaConsumer
from delivery.core.ports.kafka_consumer_registry import KafkaConsumerRegistry
from delivery.libs.errs.error import Error
from delivery.libs.errs.result import Result
from delivery.settings import settings

logger = structlog.get_logger(__name__)


@KafkaConsumerRegistry.register
class BasketEventsConsumer(KafkaConsumer):
    def __init__(
        self,
        create_order_handler: CreateOrderCommandHandler,
    ) -> None:
        self._create_order_handler = create_order_handler

    @property
    def topic(self) -> str:
        return settings.kafka_baskets_events_topic

    @property
    def group_id(self) -> str | None:
        return settings.kafka_consumer_group

    async def consume(self, message: bytes) -> None:
        try:
            confirmed_event: typing.Final = pb2.BasketConfirmedIntegrationEvent.FromString(message)
            await self.handle_basket_confirmed(confirmed_event)

        except Exception as e:
            logger.exception(
                "Failed to parse basket event",
                error=str(e),
            )

    async def handle_basket_confirmed(
        self,
        message: pb2.BasketConfirmedIntegrationEvent,
    ) -> None:
        logger.info(
            "Received basket confirmed event",
            basket_id=message.basket_id,
        )

        command_result: typing.Final = map_basket_confirmed_to_create_order_command(message)
        if command_result.is_failure:
            error: typing.Final = command_result.get_error()
            logger.error(
                "Failed to map basket event to command",
                basket_id=message.basket_id,
                error_code=error.code,
                error_message=error.message,
            )
            return

        command: typing.Final = command_result.get_value()

        handle_result: typing.Final = await self._create_order_handler.handle(command)
        if handle_result.is_failure:
            handle_error: typing.Final = handle_result.get_error()
            logger.error(
                "Failed to create order from basket event",
                basket_id=message.basket_id,
                order_id=command.order_id,
                error_code=handle_error.code,
                error_message=handle_error.message,
            )
        else:
            logger.info(
                "Successfully created order from basket event",
                basket_id=message.basket_id,
                order_id=command.order_id,
            )
