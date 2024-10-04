from typing import List

from fastapi import FastAPI
from fastapi.middleware import Middleware
from fastapi.middleware.cors import CORSMiddleware

import numpy as np
import pandas as pd
from sqlalchemy.future import select
from sqlalchemy import insert

from app.api.api import router
from app.core.config import config
from app.core.database.create_db import validate_database
from app.core.middlewares.sqlalchemy import SQLAlchemyMiddleware
from app.core.database.session import get_session
from app.models.estimate import Vehicle
from app.utils.logger import app_logger


def init_db():
    validate_database()


def init_routers(app_: FastAPI) -> None:
    app_.include_router(router)


def make_middleware() -> List[Middleware]:
    middleware = [
        Middleware(
            CORSMiddleware,
            allow_origins=["*"],
            allow_credentials=True,
            allow_methods=["*"],
            allow_headers=["*"],
        ),
        Middleware(SQLAlchemyMiddleware),
    ]
    return middleware


def create_app() -> FastAPI:
    app_ = FastAPI(
        title="CarValue Trial Porject",
        description="Search Interface for CarValue",
        version="1.0.0",
        docs_url=None if config.ENVIRONMENT == "production" else "/docs",
        redoc_url=None if config.ENVIRONMENT == "production" else "/redoc",
    )

    @app_.on_event("startup")
    async def startup_populate_data():
        async for session in get_session():
            result = await session.execute(select(Vehicle).limit(1))
            vehicle_exists = result.scalars().first()

            if vehicle_exists is None:
                data_file_path = "data/NEWTEST-inventory-listing-2022-08-17.txt"
                df = pd.read_csv(data_file_path, delimiter="|", on_bad_lines="skip")
                df_filtered = df.replace({np.nan: None})
                vehicles_data = df_filtered.to_dict(orient="records")

                await session.execute(insert(Vehicle), vehicles_data)
                await session.commit()

                app_logger.info("Database populated with initial data.")
            else:
                app_logger.info("Database already contains data.")

    app_.add_middleware(
        CORSMiddleware,
        allow_origins=["*"],
        allow_credentials=True,
        allow_methods=["*"],
        allow_headers=["*"],
    )
    app_.add_middleware(SQLAlchemyMiddleware)
    init_routers(app_=app_)
    return app_


app = create_app()
