from pydantic import BaseModel, Field
from typing import Optional


class EstimateRequest(BaseModel):
    year: int = Field(..., description="The year of the vehicle", examples=[2015])
    make: str = Field(..., description="The make of the vehicle", examples=["Toyota"])
    model: str = Field(..., description="The model of the vehicle", examples=["Camry"])
    mileage: Optional[int] = Field(
        None, description="The mileage of the vehicle", examples=[150000]
    )
