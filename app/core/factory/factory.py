from functools import partial

from fastapi import Depends

from app.controllers import (
    EstimateController,
)
from app.core.database.session import get_session
from app.models import Vehicle
from app.repositories import (
    EstimateRepository,
)


class Factory:
    estimate_repository = partial(EstimateRepository, Vehicle)

    def get_estimate_controller(
        self, db_session=Depends(get_session)
    ) -> EstimateController:
        return EstimateController(
            estimate_repository=self.estimate_repository(db_session=db_session),
        )
