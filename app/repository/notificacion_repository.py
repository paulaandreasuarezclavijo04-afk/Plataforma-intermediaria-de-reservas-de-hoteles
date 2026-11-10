# ─────────────────────────────────────────────────────────────
# REPOSITORIO DE NOTIFICACIONES (correos simulados)
# Soporta HU-068 (confirmación de reserva), HU-002 y HU-005.
# ─────────────────────────────────────────────────────────────

from datetime import datetime

from sqlalchemy import select
from sqlalchemy.orm import Session

from app.repository.base_repository import BaseRepository
from app.repository.database.models import Notificacion


class NotificacionRepository(BaseRepository[Notificacion]):

    def __init__(self, session: Session):
        super().__init__(session, Notificacion)

    def crear(
        self,
        usuario_id: int,
        tipo: str,
        asunto: str,
        contenido: str,
        reserva_id: int | None = None
    ) -> Notificacion:
        notificacion = Notificacion(
            usuario_id=usuario_id,
            tipo=tipo,
            asunto=asunto,
            contenido=contenido,
            reserva_id=reserva_id,
            estado="enviada",
            fecha_envio=datetime.utcnow()
        )
        return self.add(notificacion)

    def list_by_usuario(
        self,
        usuario_id: int,
        limit: int = 50
    ) -> list[Notificacion]:
        stmt = (
            select(Notificacion)
            .where(Notificacion.usuario_id == usuario_id)
            .order_by(Notificacion.fecha_creacion.desc())
            .limit(limit)
        )
        return list(self.session.scalars(stmt).all())
