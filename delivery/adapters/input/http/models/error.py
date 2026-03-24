from pydantic import BaseModel, Field


class Error(BaseModel):
    code: int = Field(..., description="HTTP status code")
    message: str = Field(..., description="Error message")
