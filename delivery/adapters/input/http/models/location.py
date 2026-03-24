from pydantic import BaseModel, Field


class Location(BaseModel):
    x: int = Field(..., ge=0, description="X coordinate")
    y: int = Field(..., ge=0, description="Y coordinate")
