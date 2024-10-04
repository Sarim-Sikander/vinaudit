from fastapi import APIRouter

from app.api.endpoints import estimate_settings

router = APIRouter()

router.include_router(
    router=estimate_settings.router, prefix="/estimate", tags=["estimate_car_value"]
)
