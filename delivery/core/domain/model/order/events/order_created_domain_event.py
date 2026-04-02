from uuid import UUID

from delivery.libs.ddd.events import DomainEvent


class OrderCreatedDomainEvent(DomainEvent):
    order_id: UUID

    def __init__(self, order_id: UUID) -> None:
        super().__init__(order_id=order_id)
