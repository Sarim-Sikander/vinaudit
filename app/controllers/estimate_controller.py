from app.controllers.base import BaseController
from app.core.exceptions.base import NotFoundException
from app.models.estimate import Vehicle
from app.repositories import EstimateRepository
from app.schemas.responses.estimate import EstimateResponse, VehicleSample


class EstimateController(BaseController[Vehicle]):
    def __init__(self, estimate_repository: EstimateRepository) -> None:
        super().__init__(model=Vehicle, repository=estimate_repository)
        self.estimate_repository: EstimateRepository = estimate_repository

    async def get_estimate(self, request) -> EstimateResponse:

        vehicles: list[Vehicle] = await self.estimate_repository.get_estimate(
            make=request.make,
            year=request.year,
            model=request.model,
            listing_mileage=request.mileage,
        )

        if not vehicles:
            raise NotFoundException(
                custom_msg="No vehicles found for the given year, make, and model.",
            )

        base_price = sum(
            vehicle.listing_price
            for vehicle in vehicles
            if vehicle.listing_price is not None
        ) / len(vehicles)

        adjusted_price = self.calculate_adjusted_price(base_price, request.mileage)

        average_price = round(adjusted_price, -2)

        samples: list[VehicleSample] = [
            VehicleSample(
                year=vehicle.year,
                make=vehicle.make,
                model=vehicle.model,
                listing_price=vehicle.listing_price,
                listing_mileage=vehicle.listing_mileage,
                dealer_city=vehicle.dealer_city,
            )
            for vehicle in vehicles[:100]
        ]

        return EstimateResponse(average_price=average_price, samples=samples)

    def calculate_adjusted_price(self, base_price: float, mileage: int) -> float:
        """
        Calculate the adjusted price based on the provided mileage.

        Uses a piecewise function to account for depreciation rates in different mileage brackets.
        """
        if mileage is None:
            return base_price

        if mileage <= 30000:
            depreciation_rate = 0.000001
        elif mileage <= 100000:
            depreciation_rate = 0.000003
        else:
            depreciation_rate = 0.000005

        adjustment_factor = 1 - (depreciation_rate * mileage)
        adjusted_price = base_price * max(adjustment_factor, 0)
        return adjusted_price
