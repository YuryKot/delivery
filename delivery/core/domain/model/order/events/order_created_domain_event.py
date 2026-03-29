import typing
from uuid import UUID

from delivery.libs.ddd.events import DomainEvent


class OrderCreatedDomainEvent(DomainEvent):
    def __init__(self, order_id: UUID) -> None:
        super().__init__()
        self._order_id: typing.Final = order_id

    @property
    def order_id(self) -> UUID:
        return self._order_id
