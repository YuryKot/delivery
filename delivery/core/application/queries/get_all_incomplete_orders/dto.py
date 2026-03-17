import dataclasses
from uuid import UUID


@dataclasses.dataclass(frozen=True, slots=True)
class IncompleteOrderDto:
    id: UUID
    location_x: int
    location_y: int
