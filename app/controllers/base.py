from typing import Any, Generic, Type, TypeVar

from app.core.database.session import Base
from app.core.exceptions import NotFoundException
from app.repositories.base import BaseRepository

ModelType = TypeVar("ModelType", bound=Base)


class BaseController(Generic[ModelType]):
    """Base class for data controllers."""

    def __init__(self, model: Type[ModelType], repository: BaseRepository) -> None:
        self.model_class: type[ModelType] = model
        self.repository: BaseRepository[Any] = repository

    async def get_by_id(self, id_: int, join_: set[str] | None = None) -> ModelType:
        """
        Returns the model instance matching the id.

        :param id_: The id to match.
        :param join_: The joins to make.
        :return: The model instance.
        """
        db_obj = await self.repository.get_by_column(
            column="id", value=id_, join_=join_, unique=True
        )
        if not db_obj:
            raise NotFoundException(
                f"{self.model_class.__tablename__.title()} with id: {id_} does not exist"
            )

        return db_obj

    async def get_by_ids(self, ids_: list[int]) -> list[ModelType]:
        """
        Returns the model instances matching the ids.

        :param ids_: The ids to match.
        :return: The model instances.
        """
        db_objs: list[Any] = await self.repository.get_by_ids(ids=ids_)
        return db_objs

    async def get_by_column(
        self,
        column: str,
        value: Any,
        join_: set[str] | None = None,
        unique: bool = False,
    ) -> list[ModelType]:
        """
        Returns the model instance matching the column and value.

        :param column: The column to match.
        :param value: The value to match.
        :param join_: The joins to make.
        :return: The model instance.
        """

        response = await self.repository.get_by_column(
            column=column, value=value, join_=join_, unique=unique
        )
        return response

    async def get_all(
        self, skip: int = 0, limit: int = 100, join_: set[str] | None = None
    ) -> list[ModelType]:
        """
        Returns a list of records based on pagination params.

        :param skip: The number of records to skip.
        :param limit: The number of records to return.
        :param join_: The joins to make.
        :return: A list of records.
        """

        response: list[Any] = await self.repository.get_all(skip, limit, join_)
        return response

    async def create(self, attributes: dict[str, Any]) -> ModelType:
        """
        Creates a new Object in the DB.

        :param attributes: The attributes to create the object with.
        :return: The created object.
        """
        create = await self.repository.create(attributes)
        await self.repository.session.commit()
        return create

    async def delete_by_id(self, id: int) -> None:
        """
        Deletes the object from the DB.

        :param id: The id of object to delete.
        :return: True if the object was deleted, False otherwise.
        """
        await self.repository.delete_by_id(id)
        await self.repository.session.commit()

    async def sort_by_column(
        self,
        column: str,
        join_: set[str] | None = None,
        order: str | None = "asc",
    ) -> list[ModelType]:
        """
        Returns the model instance matching the column and value.

        :param column: The column to match.
        :param join_: The joins to make.
        :return: The model instance.
        """
        query = await self.repository._query()
        query = await self.repository._sort_by(query=query, sort_by=column, order=order)
        response: list[Any] = await self.repository._all(query)
        return response
