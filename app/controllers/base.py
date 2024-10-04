from typing import Any, Generic, Type, TypeVar

from app.core.database.session import Base
from app.repositories.base import BaseRepository

ModelType = TypeVar("ModelType", bound=Base)


class BaseController(Generic[ModelType]):
    """Base class for data controllers."""

    def __init__(self, model: Type[ModelType], repository: BaseRepository) -> None:
        self.model_class: Type[ModelType] = model
        self.repository: BaseRepository[Any] = repository
