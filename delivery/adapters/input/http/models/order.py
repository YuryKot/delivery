from uuid import UUID

from pydantic import BaseModel, Field

from delivery.adapters.input.http.models.location import Location


class Order(BaseModel):
    id: UUID = Field(..., description="Order identifier")
    location: Location = Field(..., description="Order location")


class CreateOrderRequest(BaseModel):
    order_id: UUID = Field(..., description="Order identifier (client-generated)")
    country: str = Field(..., min_length=1, description="Country")
    city: str = Field(..., min_length=1, description="City")
    street: str = Field(..., min_length=1, description="Street")
    house: str = Field(..., min_length=1, description="House number")
    apartment: str = Field(..., min_length=1, description="Apartment number")
    volume: int = Field(..., ge=1, le=100, description="Order volume (1-100)")


class CreateOrderResponse(BaseModel):
    order_id: UUID = Field(..., description="Created order identifier", alias="orderId")
