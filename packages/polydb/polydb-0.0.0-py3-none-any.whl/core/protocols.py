from abc import abstractmethod
from typing import Any, Protocol, Sequence, TypeVar

from pydantic import BaseModel

Model = TypeVar("Model", bound=BaseModel)
Id = TypeVar("Id")


class Collection(Protocol[Model]):
    """Abstract base class containing shared logic for database CRUD."""

    model_type: type[Model]

    def deserialize_model(self, doc: dict[str, Any], **kwargs: Any) -> Model:
        """
        Convert document into model type.

        Pydantic should handle this most of the time, but subclasses can
        override this method to inject custom deserialization logic if it is
        absolutely necessary.
        """
        return self.model_type(**doc)

    def serialize_model(self, model: Model, **kwargs: Any) -> dict[str, Any]:
        """
        Convert model into document.

        Pydantic should handle this most of the time, but subclasses can
        override this method to inject custom deserialization logic if it is
        absolutely necessary.
        """
        return model.model_dump()

    def serialize_value(self, value: Any) -> Any:
        """
        Hook for subclasses to provide custom serialization for certain values,
        to make them suitable for storage in the database.

        Args:
            value: the python-native datatype to be serialized
        """
        return value

    def deserialize_value(self, serialized: Any) -> Any:
        """
        Hook for subclasses to provide custom deserialization for certain values
        that come from the database.

        Args:
            serialized: The serialized value that comes from the database
        """
        return serialized


class Create(Collection[Model]):
    """Create mixin."""

    @abstractmethod
    async def create(self, *models: Model, **kwargs: Any) -> Any:
        """Insert several models into the db."""
        ...


class Read(Collection[Model]):
    """Read mixin."""

    @abstractmethod
    async def read(self, id: Id, **kwargs: Any) -> Model | None:
        """Get a model from the db by id."""
        ...


class Update(Collection[Model]):
    """Update mixin."""

    @abstractmethod
    async def update(
        self,
        *models: Model,
        update_fields: Sequence[str] = (),
        **kwargs: Any,
    ) -> Any:
        """Update the given model in the db.

        Args:
            update_fields: if empty, update all fields
        """
        ...


class Delete(Collection[Model]):
    """Delete mixin."""

    @abstractmethod
    async def delete(self, id: Id, **kwargs: Any) -> Any:
        """Delete an entry by id."""
        ...
