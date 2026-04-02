import json
import logging
import typing

from delivery.adapters.out.kafka.order_events_producer import OrderEventsProducerImpl
from delivery.core.domain.model.order.events.order_completed_domain_event import OrderCompletedDomainEvent
from delivery.core.domain.model.order.events.order_created_domain_event import OrderCreatedDomainEvent
from delivery.core.ports.outbox_repository import OutboxRepository
from delivery.database.models import OutboxMessageModel
from delivery.libs.ddd.events import DomainEvent


logger = logging.getLogger(__name__)


class OutboxJob:
    def __init__(
        self,
        outbox_repository: OutboxRepository,
        order_events_producer: OrderEventsProducerImpl,
    ) -> None:
        self._outbox_repository = outbox_repository
        self._order_events_producer = order_events_producer

    async def run(self) -> None:
        unprocessed_messages: typing.Final = await self._outbox_repository.find_unprocessed_messages()

        for message in unprocessed_messages:
            try:
                domain_event = self._deserialize_event(message)
                await self._order_events_producer.publish([domain_event])
                await self._outbox_repository.mark_as_processed(message.id)
            except Exception:
                logger.exception("Failed to publish outbox message %s", message.id)

    def _deserialize_event(self, message: OutboxMessageModel) -> DomainEvent:
        json.loads(message.payload)

        if message.event_type == "OrderCreatedDomainEvent":
            return OrderCreatedDomainEvent(order_id=message.aggregate_id)
        if message.event_type == "OrderCompletedDomainEvent":
            return OrderCompletedDomainEvent(order_id=message.aggregate_id)
        raise ValueError(f"Unknown event type: {message.event_type}")
