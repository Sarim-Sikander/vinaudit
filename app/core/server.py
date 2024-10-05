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
from app.repositories.base import BaseRepository
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
        title="CarValue Trial Project",
        description="Search Interface for CarValue",
        version="1.0.0",
        docs_url=None if config.ENVIRONMENT == "production" else "/docs",
        redoc_url=None if config.ENVIRONMENT == "production" else "/redoc",
    )

    @app_.on_event("startup")
    async def startup_populate_data():
        async for session in get_session():
            vehicle_repo = BaseRepository(model=Vehicle, db_session=session)
            result = await session.execute(select(Vehicle).limit(1))
            vehicle_exists = result.scalars().first()
            data_file_path = "data/NEWTEST-inventory-listing-2022-08-17.txt"
            chunksize = 100

            if vehicle_exists is None:
                for chunk in pd.read_csv(
                    data_file_path,
                    delimiter="|",
                    on_bad_lines="skip",
                    chunksize=chunksize,
                ):
                    df_filtered = chunk.replace({np.nan: None})
                    vehicles_data = df_filtered.to_dict(orient="records")

                    await vehicle_repo.insert_many(vehicles_data)
                    app_logger.info("Inserted a chunk of data into the database.")

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
