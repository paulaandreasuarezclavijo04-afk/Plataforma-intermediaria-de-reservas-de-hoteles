# ─────────────────────────────────────────────────────────────
# SERVICIO DE ASISTENCIA — HU-092 (crear solicitud de asistencia)
#
# CICLO DE VIDA: abierta → en_proceso → respondida → cerrada
# ─────────────────────────────────────────────────────────────

from datetime import datetime

from fastapi import HTTPException, status
from sqlalchemy.orm import Session

from app.api.schemas.asistencia_schema import AsistenciaCreate, AsistenciaUpdate
from app.repository.asistencia_repository import AsistenciaRepository
from app.repository.database.models import SolicitudAsistencia
from app.repository.reserva_repository import ReservaRepository
from app.repository.usuario_repository import UsuarioRepository

TRANSICIONES = {
    "abierta": ("en_proceso", "respondida", "cerrada"),
    "en_proceso": ("respondida", "cerrada"),
    "respondida": ("cerrada",),
    "cerrada": (),
}


class AsistenciaService:

    def __init__(self, db: Session):
        self.db = db
        self.repo = AsistenciaRepository(db)
        self.usuarios = UsuarioRepository(db)
        self.reservas = ReservaRepository(db)

    # ── HU-092: crear solicitud ─────────────────────────────
    def crear(self, data: AsistenciaCreate) -> SolicitudAsistencia:
        usuario = self.usuarios.get_by_id(data.usuario_id)
        if not usuario or not usuario.activo:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Usuario no encontrado o inactivo"
            )

        if data.reserva_id:
            reserva = self.reservas.get_by_id(data.reserva_id)
            if not reserva:
                raise HTTPException(
                    status_code=status.HTTP_404_NOT_FOUND,
                    detail="Reserva no encontrada"
                )

        solicitud = SolicitudAsistencia(
            asunto=data.asunto.strip(),
            descripcion=data.descripcion.strip(),
            tipo=data.tipo,
            estado="abierta",
            usuario_id=usuario.id,
            reserva_id=data.reserva_id
        )
        self.repo.add(solicitud)
        self.repo.commit()
        self.repo.flush()
        return solicitud

    # ── Consultas ───────────────────────────────────────────
    def listar(
        self,
        usuario_id: int | None = None,
        estado: str | None = None,
        tipo: str | None = None
    ) -> list[SolicitudAsistencia]:
        return self.repo.list_filtrado(
            usuario_id=usuario_id,
            estado=estado,
            tipo=tipo
        )

    def obtener(self, solicitud_id: int) -> SolicitudAsistencia:
        solicitud = self.repo.get_by_id(solicitud_id)
        if not solicitud:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Solicitud de asistencia no encontrada"
            )
        return solicitud

    # ── Actualizar estado / responder ───────────────────────
    def actualizar_estado(
        self,
        solicitud_id: int,
        data: AsistenciaUpdate
    ) -> SolicitudAsistencia:
        solicitud = self.obtener(solicitud_id)
        nuevo_estado = data.estado
        actual = solicitud.estado

        if nuevo_estado == actual:
            return solicitud

        if nuevo_estado not in TRANSICIONES.get(actual, ()):
            raise HTTPException(
                status_code=status.HTTP_409_CONFLICT,
                detail=f"No se puede pasar de '{actual}' a '{nuevo_estado}'"
            )

        if nuevo_estado == "respondida" and not (
            data.respuesta or solicitud.respuesta
        ):
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Para responder la solicitud debe envíar 'respuesta'"
            )

        solicitud.estado = nuevo_estado

        if data.respuesta:
            solicitud.respuesta = data.respuesta.strip()

        if nuevo_estado == "cerrada":
            solicitud.fecha_cierre = datetime.utcnow()

        self.repo.commit()
        self.repo.flush()
        return solicitud
