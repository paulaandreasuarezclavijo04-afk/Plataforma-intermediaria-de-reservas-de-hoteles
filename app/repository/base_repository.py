# ─────────────────────────────────────────────────────────────
# REPOSITORIO BASE — operaciones genéricas sobre una entidad
# ─────────────────────────────────────────────────────────────

from typing import Generic, Sequence, Type, TypeVar

from sqlalchemy import select
from sqlalchemy.orm import Session

ModelType = TypeVar("ModelType")


class BaseRepository(Generic[ModelType]):

    def __init__(self, session: Session, model: Type[ModelType]):
        self.session = session
        self.model = model

    def get_by_id(self, entity_id: int) -> ModelType | None:
        return self.session.get(self.model, entity_id)

    def list(
        self,
        limit: int = 100,
        offset: int = 0
    ) -> Sequence[ModelType]:
        stmt = (
            select(self.model)
            .limit(limit)
            .offset(offset)
        )
        return self.session.scalars(stmt).all()

    def add(self, entity: ModelType) -> ModelType:
        self.session.add(entity)
        return entity

    def delete(self, entity: ModelType) -> None:
        self.session.delete(entity)

    def flush(self) -> None:
        self.session.flush()

    def commit(self) -> None:
        self.session.commit()

    def rollback(self) -> None:
        self.session.rollback()
