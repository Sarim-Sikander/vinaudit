from pydantic.v1 import BaseSettings


class BaseConfig(BaseSettings):
    class Config:
        case_sensitive = True


class Config(BaseConfig):
    HOST: str = "0.0.0.0"
    PORT: int = 8000
    ENVIRONMENT: str
    DATABASE_URL: str = "mysql+mysqlconnector://root:1234@localhost:3306/carvalue"

    class Config:
        env_file = "./.env"


config: Config = Config()
