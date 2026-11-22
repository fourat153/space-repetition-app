from typing import Generic, TypeVar

from sqlalchemy.orm import Session

from app.db.base import Base

ModelT = TypeVar("ModelT", bound=Base)


class BaseRepository(Generic[ModelT]):
    """Generic data access for one model. Subclasses set `model` and add their own queries.

    Repositories only read and stage changes; services decide when to commit.
    """

    model: type[ModelT]

    def __init__(self, session: Session) -> None:
        self.session = session

    def get(self, id: str) -> ModelT | None:
        return self.session.get(self.model, id)

    def add(self, obj: ModelT) -> ModelT:
        self.session.add(obj)
        return obj

    def delete(self, obj: ModelT) -> None:
        self.session.delete(obj)
