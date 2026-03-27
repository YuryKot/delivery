from uuid import UUID

from pydantic import BaseModel, Field

from delivery.adapters.input.http.models.location import Location


class Courier(BaseModel):
    id: UUID = Field(..., description="Courier identifier")
    name: str = Field(..., description="Courier name")
    location: Location = Field(..., description="Courier location")


class NewCourier(BaseModel):
    name: str = Field(..., min_length=1, description="Courier name")


class CreateCourierResponse(BaseModel):
    courier_id: UUID = Field(..., description="Created courier identifier", alias="courierId")
