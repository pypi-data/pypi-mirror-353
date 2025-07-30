from abc import ABC, abstractmethod
from typing import TypeVar, Generic, Optional, Hashable, List
from pydantic import BaseModel

from ..domain.entity import IEntity, TEntityId
from ..domain.model import IModel


class RepositoryError(Exception):
    """Base exception for repository operations."""

    pass


class RecordNotFoundError(RepositoryError):
    """Raised when a record is not found."""

    pass


class DuplicateRecordError(RepositoryError):
    """Raised when trying to create a duplicate record."""

    pass


class ICreateSchema(BaseModel):
    """
    Schema for create operations.
    This can be used to specify fields required for creating a new record.
    """

    pass


class IReadSchema(BaseModel):
    """
    Schema for read operations.
    This can be used to specify fields that can be retrieved.
    """

    pass


class IReadAggregateSchema(BaseModel):
    """
    Schema for read aggregate operations.
    This can be used to specify fields that can be aggregated or summarized.
    """

    pass


class IUpdateSchema(BaseModel):
    """
    Schema for update operations.
    This can be used to specify fields that can be updated.
    """

    pass


TEntity = TypeVar("TEntity", bound=IEntity)
TModel = TypeVar("TModel", bound=IModel)
TCreateSchema = TypeVar("TCreateSchema", bound=ICreateSchema)
TReadSchema = TypeVar("TReadSchema", bound=IReadSchema)
TReadAggregateSchema = TypeVar("TReadAggregateSchema", bound=IReadAggregateSchema)
TUpdateSchema = TypeVar("TUpdateSchema", bound=IUpdateSchema)


class ICrudRepository(
    ABC,
    Generic[TEntity, TCreateSchema, TReadSchema, TUpdateSchema],
):
    """
    Base interface for CRUD repositories.
    All repositories should implement the basic CRUD operations.
    This repository works with single entities without relationships.
    """

    @abstractmethod
    async def create(self, schema: TCreateSchema) -> TEntity:
        """
        Create a new record.
        """
        raise NotImplementedError

    @abstractmethod
    async def read(self, id: Hashable) -> TEntity:
        """
        Read a record by its ID.
        The ID type should match the entity's TEntityId type parameter.
        Raises RecordNotFoundError if record doesn't exist.
        """
        raise NotImplementedError

    @abstractmethod
    async def read_optional(self, id: Hashable) -> Optional[TEntity]:
        """
        Read a record by its ID, returning None if not found.
        The ID type should match the entity's TEntityId type parameter.
        """
        raise NotImplementedError

    @abstractmethod
    async def update(self, id: Hashable, schema: TUpdateSchema) -> TEntity:
        """
        Update a record by its schema.
        The ID type should match the entity's TEntityId type parameter.
        """
        raise NotImplementedError

    @abstractmethod
    async def delete(self, id: Hashable) -> bool:
        """
        Delete a record by its ID.
        The ID type should match the entity's TEntityId type parameter.
        Returns True if deletion was successful, False otherwise.
        """
        raise NotImplementedError

    @abstractmethod
    async def list(
        self, limit: Optional[int] = None, offset: Optional[int] = None, **filters
    ) -> List[TEntity]:
        """
        List records with optional pagination and filtering.
        """
        raise NotImplementedError


class IReadRepository(ABC, Generic[TEntity, TReadSchema]):
    """
    Base interface for read-only repositories.
    This repository works with single entities without relationships.
    Use this for simple read operations that return entities.
    """

    @abstractmethod
    async def read(self, id: Hashable) -> TEntity:
        """
        Read an entity by its ID.
        The ID type should match the entity's TEntityId type parameter.
        Raises RecordNotFoundError if entity doesn't exist.

        Returns:
            Single entity without relationships
        """
        raise NotImplementedError

    @abstractmethod
    async def read_optional(self, id: Hashable) -> Optional[TEntity]:
        """
        Read an entity by its ID, returning None if not found.
        The ID type should match the entity's TEntityId type parameter.

        Returns:
            Single entity without relationships, or None if not found
        """
        raise NotImplementedError

    @abstractmethod
    async def list(
        self, limit: Optional[int] = None, offset: Optional[int] = None, **filters
    ) -> List[TEntity]:
        """
        List entities with optional pagination and filtering.

        Returns:
            List of entities without relationships
        """
        raise NotImplementedError


class IReadAggregateRepository(ABC, Generic[TModel, TReadAggregateSchema]):
    """
    Base interface for read aggregate repositories.
    This repository works with models that include relationships and aggregated data.
    Use this for complex read operations that return models with relationships.
    """

    @abstractmethod
    async def read(self, id: Hashable) -> TModel:
        """
        Read an aggregate model by its ID.
        The ID type should match the related entity's TEntityId type parameter.
        Raises RecordNotFoundError if model doesn't exist.

        Returns:
            Model with relationships and aggregated data
        """
        raise NotImplementedError

    @abstractmethod
    async def read_optional(self, id: Hashable) -> Optional[TModel]:
        """
        Read an aggregate model by its ID, returning None if not found.
        The ID type should match the related entity's TEntityId type parameter.

        Returns:
            Model with relationships and aggregated data, or None if not found
        """
        raise NotImplementedError

    @abstractmethod
    async def list(
        self, limit: Optional[int] = None, offset: Optional[int] = None, **filters
    ) -> List[TModel]:
        """
        List aggregate models with optional pagination and filtering.

        Returns:
            List of models with relationships and aggregated data
        """
        raise NotImplementedError
