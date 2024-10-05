from typing import List

from app.controllers.base import BaseController
from app.core.exceptions.base import NotFoundException
from app.integration.lr_model import VehiclePriceEstimator
from app.models.estimate import Vehicle
from app.repositories import EstimateRepository
from app.schemas.responses.estimate import EstimateResponse, VehicleSample


class EstimateController(BaseController[Vehicle]):
    def __init__(self, estimate_repository: EstimateRepository) -> None:
        super().__init__(model=Vehicle, repository=estimate_repository)
        self.estimate_repository: EstimateRepository = estimate_repository
        self.estimator = VehiclePriceEstimator(model_path="app/regression_model.json")
        self.estimator.load_model()

    async def get_estimate(self, request) -> EstimateResponse:

        vehicles: List[Vehicle] = await self.estimate_repository.get_estimate(
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

        adjusted_price = self.estimator.calculate_adjusted_price(
            base_price=base_price, mileage=request.mileage, year=request.year
        )

        average_price = round(adjusted_price, -2)

        samples: List[VehicleSample] = [
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
