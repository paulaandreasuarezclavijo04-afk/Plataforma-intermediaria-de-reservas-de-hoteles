# ─────────────────────────────────────────────────────────────
# REPOSITORIO DE EVALUACIONES — HU-076
# ─────────────────────────────────────────────────────────────

from sqlalchemy import func, select
from sqlalchemy.orm import Session

from app.repository.base_repository import BaseRepository
from app.repository.database.models import Evaluacion


class EvaluacionRepository(BaseRepository[Evaluacion]):

    def __init__(self, session: Session):
        super().__init__(session, Evaluacion)

    def list_by_hotel(
        self,
        hotel_id: int,
        limit: int = 100,
        offset: int = 0
    ) -> list[Evaluacion]:
        stmt = (
            select(Evaluacion)
            .where(Evaluacion.hotel_id == hotel_id)
            .order_by(Evaluacion.fecha_creacion.desc())
            .limit(limit)
            .offset(offset)
        )
        return list(self.session.scalars(stmt).all())

    def list_all(
        self,
        usuario_id: int | None = None,
        limit: int = 100,
        offset: int = 0
    ) -> list[Evaluacion]:
        stmt = select(Evaluacion)
        if usuario_id:
            stmt = stmt.where(Evaluacion.usuario_id == usuario_id)
        stmt = stmt.order_by(Evaluacion.fecha_creacion.desc())
        stmt = stmt.limit(limit).offset(offset)
        return list(self.session.scalars(stmt).all())

    def get_by_reserva(self, reserva_id: int) -> Evaluacion | None:
        stmt = select(Evaluacion).where(Evaluacion.reserva_id == reserva_id)
        return self.session.scalars(stmt).first()

    def promedio_by_hotel(self, hotel_id: int) -> tuple[int, float]:
        stmt = select(
            func.count(Evaluacion.id),
            func.coalesce(func.avg(Evaluacion.puntuacion), 0.0)
        ).where(Evaluacion.hotel_id == hotel_id)
        total, promedio = self.session.execute(stmt).one()
        return total, float(promedio)

    def distribucion_by_hotel(self, hotel_id: int) -> dict:
        stmt = (
            select(Evaluacion.puntuacion, func.count(Evaluacion.id))
            .where(Evaluacion.hotel_id == hotel_id)
            .group_by(Evaluacion.puntuacion)
        )
        return {str(p): c for p, c in self.session.execute(stmt).all()}
