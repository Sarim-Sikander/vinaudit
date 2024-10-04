from app.models.estimate import Vehicle
from app.repositories.base import BaseRepository


class EstimateRepository(BaseRepository[Vehicle]):
    async def get_estimate(
        self, year: int, make: str, model: str, listing_mileage: int
    ) -> list[Vehicle]:
        query = await self._query()
        if listing_mileage != 0:
            query = query.filter(
                Vehicle.year == year,
                Vehicle.make == make,
                Vehicle.model == model,
                Vehicle.listing_mileage <= listing_mileage,
            )
        else:
            query = query.filter(
                Vehicle.year == year, Vehicle.make == make, Vehicle.model == model
            )

        return await self._all(query)
