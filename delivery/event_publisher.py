import typing

from delivery.libs.ddd import Aggregate, DomainEvent, DomainEventPublisher


class DefaultDomainEventPublisher(DomainEventPublisher):
    def __init__(self) -> None:
        self._published_events: list[DomainEvent] = []

    async def publish(self, aggregates: typing.Iterable[Aggregate[typing.Any]]) -> None:
        for aggregate in aggregates:
            for event in aggregate.get_domain_events():
                self._published_events.append(event)
                # TODO: Отправить событие в Kafka
                # await self._send_to_kafka(event)

    def get_published_events(self) -> list[DomainEvent]:
        return self._published_events.copy()

    def clear_published_events(self) -> None:
        self._published_events.clear()
