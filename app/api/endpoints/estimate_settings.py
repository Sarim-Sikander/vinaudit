from typing import Optional
from fastapi import APIRouter, Depends, Request, Form
from fastapi.responses import HTMLResponse
from fastapi.templating import Jinja2Templates

from app.controllers import EstimateController
from app.core.factory import Factory
from app.schemas.requests.estimate import EstimateRequest
from app.schemas.responses.estimate import EstimateResponse

router = APIRouter()
templates = Jinja2Templates(directory="app/templates")


@router.get("/", response_class=HTMLResponse)
async def show_estimate_form(request: Request):
    return templates.TemplateResponse(
        "estimate_form_with_result.html", {"request": request}
    )


@router.post("/")
async def estimate_value(
    request: Request,
    year: int = Form(...),
    make: str = Form(...),
    model: str = Form(...),
    mileage: Optional[int] = Form(0),
    estimate_controller: EstimateController = Depends(
        Factory().get_estimate_controller
    ),
):
    estimate_request = EstimateRequest(
        year=year, make=make, model=model, mileage=mileage
    )
    response: EstimateResponse = await estimate_controller.get_estimate(
        estimate_request
    )

    return templates.TemplateResponse(
        "estimate_form_with_result.html",
        {
            "request": request,
            "average_price": response.average_price,
            "samples": response.samples,
        },
    )
