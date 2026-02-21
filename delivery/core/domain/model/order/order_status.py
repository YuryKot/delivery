import typing
from enum import StrEnum


class OrderStatus(StrEnum):
    CREATED = "Created"
    ASSIGNED = "Assigned"
    COMPLETED = "Completed"

    def can_transition_to(self, target: "OrderStatus") -> bool:
        transitions: typing.Final[dict[OrderStatus, set[OrderStatus]]] = {
            OrderStatus.CREATED: {OrderStatus.ASSIGNED},
            OrderStatus.ASSIGNED: {OrderStatus.COMPLETED},
            OrderStatus.COMPLETED: set(),
        }

        return target in transitions.get(self, set())
