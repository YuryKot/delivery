import json
import typing

from delivery.core.ports.outbox_repository import OutboxRepository
from delivery.libs.ddd import Aggregate
from delivery.libs.ddd.events import DomainEvent, DomainEventPublisher


class OutboxDomainEventPublisher(DomainEventPublisher):
    def __init__(self, outbox_repository: OutboxRepository) -> None:
        self._outbox_repository = outbox_repository

    async def publish(self, aggregates: typing.Iterable[Aggregate[typing.Any]]) -> None:
        for aggregate in aggregates:
            for domain_event in aggregate.get_domain_events():
                event_type = domain_event.__class__.__name__
                aggregate_id = aggregate.id
                aggregate_type = aggregate.__class__.__name__
                payload = json.dumps(self._event_to_dict(domain_event))

                await self._outbox_repository.add(
                    event_id=domain_event.event_id,
                    event_type=event_type,
                    aggregate_id=aggregate_id,  # type: ignore[arg-type]
                    aggregate_type=aggregate_type,
                    payload=payload,
                    occurred_on_utc=domain_event.occurred_on_utc,
                )

            aggregate.clear_domain_events()

    def _event_to_dict(self, event: DomainEvent) -> dict[str, typing.Any]:
        data: typing.Final = event.model_dump(mode="json")
        return {k: v for k, v in data.items() if not k.startswith("_")}
