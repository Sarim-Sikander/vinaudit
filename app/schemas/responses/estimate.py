from pydantic import BaseModel, Field
from typing import List, Optional


class VehicleSample(BaseModel):
    year: int = Field(..., description="The year of the vehicle")
    make: str = Field(..., description="The make of the vehicle")
    model: str = Field(..., description="The model of the vehicle")
    listing_price: Optional[int] = Field(None, description="The price of the vehicle")
    listing_mileage: Optional[int] = Field(
        None, description="The mileage of the vehicle"
    )
    dealer_city: str = Field(..., description="The location of the vehicle")


class EstimateResponse(BaseModel):
    average_price: float = Field(
        ..., description="The estimated average price of the vehicle"
    )
    samples: List[VehicleSample] = Field(
        ..., description="List of sample vehicles used to calculate the average price"
    )
