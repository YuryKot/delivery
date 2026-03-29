import typing
from uuid import UUID

from faststream.kafka import KafkaBroker

from delivery.adapters.out.kafka.proto import orders_events_pb2 as pb2
from delivery.core.domain.model.order.events import (
    OrderCompletedDomainEvent,
    OrderCreatedDomainEvent,
)
from delivery.core.ports.order_events_producer import OrderEventsProducer
from delivery.libs.ddd.events import DomainEvent
from delivery.settings import settings


class OrderEventsProducerImpl(OrderEventsProducer):
    def __init__(self, kafka_broker: KafkaBroker) -> None:
        self._kafka_broker = kafka_broker

    async def publish(self, events: list[DomainEvent]) -> None:
        for event in events:
            if isinstance(event, OrderCreatedDomainEvent):
                await self._publish_created(event.order_id)
            elif isinstance(event, OrderCompletedDomainEvent):
                await self._publish_completed(event.order_id)

    async def _publish_created(self, order_id: UUID) -> None:
        integration_event: typing.Final = pb2.OrderCreatedIntegrationEvent(order_id=str(order_id))  # type: ignore[attr-defined]
        await self._send_to_kafka(integration_event)

    async def _publish_completed(self, order_id: UUID) -> None:
        integration_event: typing.Final = pb2.OrderCompletedIntegrationEvent(order_id=str(order_id))  # type: ignore[attr-defined]
        await self._send_to_kafka(integration_event)

    async def _send_to_kafka(
        self,
        event: pb2.OrderCreatedIntegrationEvent | pb2.OrderCompletedIntegrationEvent,  # type: ignore[name-defined]
    ) -> None:
        await self._kafka_broker.publish(
            event.SerializeToString(),
            topic=settings.kafka_orders_events_topic,
            key=event.order_id.encode("utf-8"),
        )
