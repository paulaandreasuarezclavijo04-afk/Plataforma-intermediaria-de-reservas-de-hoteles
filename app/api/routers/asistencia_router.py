# ─────────────────────────────────────────────────────────────
# ROUTER DE ASISTENCIA — HU-092 (crear solicitud de asistencia)
# ─────────────────────────────────────────────────────────────

from fastapi import APIRouter, Depends, Query, status
from sqlalchemy.orm import Session

from app.api.schemas.asistencia_schema import (
    AsistenciaCreate,
    AsistenciaResponse,
    AsistenciaUpdate
)
from app.repository.database.session import get_db
from app.services.asistencia_service import AsistenciaService

router = APIRouter(prefix="/api/asistencias", tags=["Asistencia"])


@router.get(
    "",
    response_model=list[AsistenciaResponse],
    summary="HU-092: listar solicitudes (por usuario, estado o tipo)"
)
def listar(
    usuario_id: int | None = Query(None),
    estado: str | None = Query(
        None,
        description="abierta | en_proceso | respondida | cerrada"
    ),
    tipo: str | None = Query(
        None,
        description="consulta | queja | solicitud | incidencia"
    ),
    db: Session = Depends(get_db)
):
    return AsistenciaService(db).listar(
        usuario_id=usuario_id,
        estado=estado,
        tipo=tipo
    )


@router.post(
    "",
    response_model=AsistenciaResponse,
    status_code=status.HTTP_201_CREATED,
    summary="HU-092: crear solicitud de asistencia"
)
def crear(data: AsistenciaCreate, db: Session = Depends(get_db)):
    return AsistenciaService(db).crear(data)


@router.get(
    "/{solicitud_id}",
    response_model=AsistenciaResponse,
    summary="HU-092: consultar solicitud"
)
def obtener(solicitud_id: int, db: Session = Depends(get_db)):
    return AsistenciaService(db).obtener(solicitud_id)


@router.patch(
    "/{solicitud_id}/estado",
    response_model=AsistenciaResponse,
    summary="HU-092: responder o cerrar solicitud"
)
def actualizar_estado(
    solicitud_id: int,
    data: AsistenciaUpdate,
    db: Session = Depends(get_db)
):
    return AsistenciaService(db).actualizar_estado(solicitud_id, data)
