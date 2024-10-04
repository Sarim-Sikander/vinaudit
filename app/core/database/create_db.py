from sqlalchemy import create_engine
from sqlalchemy_utils.functions import database_exists, create_database
from app.core.config import config


def validate_database():
    engine = create_engine(config.DATABASE_URL)

    if database_exists(engine.url):
        print("Database already exists")
    else:
        create_database(engine.url)
        print("New database created")
