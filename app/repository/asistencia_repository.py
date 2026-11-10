# ─────────────────────────────────────────────────────────────
# REPOSITORIO DE SOLICITUDES DE ASISTENCIA — HU-092
# ─────────────────────────────────────────────────────────────

from sqlalchemy import select
from sqlalchemy.orm import Session

from app.repository.base_repository import BaseRepository
from app.repository.database.models import SolicitudAsistencia


class AsistenciaRepository(BaseRepository[SolicitudAsistencia]):

    def __init__(self, session: Session):
        super().__init__(session, SolicitudAsistencia)

    def list_filtrado(
        self,
        usuario_id: int | None = None,
        estado: str | None = None,
        tipo: str | None = None,
        limit: int = 100,
        offset: int = 0
    ) -> list[SolicitudAsistencia]:
        stmt = select(SolicitudAsistencia)

        if usuario_id:
            stmt = stmt.where(SolicitudAsistencia.usuario_id == usuario_id)
        if estado:
            stmt = stmt.where(SolicitudAsistencia.estado == estado)
        if tipo:
            stmt = stmt.where(SolicitudAsistencia.tipo == tipo)

        stmt = stmt.order_by(SolicitudAsistencia.fecha_creacion.desc())
        stmt = stmt.limit(limit).offset(offset)
        return list(self.session.scalars(stmt).all())
