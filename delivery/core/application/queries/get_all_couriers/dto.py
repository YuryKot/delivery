import dataclasses
from uuid import UUID


@dataclasses.dataclass(frozen=True, slots=True)
class CourierDto:
    id: UUID
    name: str
    location_x: int
    location_y: int
