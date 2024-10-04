from app.models.estimate import Vehicle
from app.repositories.base import BaseRepository


class EstimateRepository(BaseRepository[Vehicle]):
    async def get_estimate(self, year: int, make: str, model: str) -> list[Vehicle]:
        query = await self._query()
        query = query.filter(
            Vehicle.year == year, Vehicle.make == make, Vehicle.model == model
        )

        return await self._all(query)
