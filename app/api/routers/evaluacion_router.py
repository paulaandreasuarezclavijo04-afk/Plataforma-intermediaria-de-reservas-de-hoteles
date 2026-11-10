# ─────────────────────────────────────────────────────────────
# ROUTER DE EVALUACIONES — HU-076 (CRUD de evaluaciones)
# ─────────────────────────────────────────────────────────────

from fastapi import APIRouter, Depends, Query, status
from sqlalchemy.orm import Session

from app.api.schemas.evaluacion_schema import (
    EvaluacionCreate,
    EvaluacionResponse,
    EvaluacionUpdate,
    ResumenHotelEvaluaciones,
    RespuestaHotelRequest
)
from app.repository.database.session import get_db
from app.services.evaluacion_service import EvaluacionService

router = APIRouter(prefix="/api/evaluaciones", tags=["Evaluaciones"])


@router.get(
    "",
    response_model=list[EvaluacionResponse],
    summary="HU-076: listar evaluaciones (todas o por usuario)"
)
def listar(
    usuario_id: int | None = Query(None),
    db: Session = Depends(get_db)
):
    return EvaluacionService(db).listar(usuario_id=usuario_id)


@router.post(
    "",
    response_model=EvaluacionResponse,
    status_code=status.HTTP_201_CREATED,
    summary="HU-076: crear evaluación (solo reservas completadas)"
)
def crear(data: EvaluacionCreate, db: Session = Depends(get_db)):
    return EvaluacionService(db).crear(data)


# ── Consultas por hotel (antes de /{id}) ────────────────────
@router.get(
    "/hotel/{hotel_id}",
    response_model=list[EvaluacionResponse],
    summary="HU-076: evaluaciones públicas de un hotel"
)
def listar_por_hotel(hotel_id: int, db: Session = Depends(get_db)):
    return EvaluacionService(db).listar_por_hotel(hotel_id)


@router.get(
    "/hotel/{hotel_id}/resumen",
    response_model=ResumenHotelEvaluaciones,
    summary="HU-076: promedio y distribución de un hotel"
)
def resumen(hotel_id: int, db: Session = Depends(get_db)):
    return EvaluacionService(db).resumen(hotel_id)


@router.get(
    "/{evaluacion_id}",
    response_model=EvaluacionResponse,
    summary="HU-076: consultar evaluación"
)
def obtener(evaluacion_id: int, db: Session = Depends(get_db)):
    return EvaluacionService(db).obtener(evaluacion_id)


@router.put(
    "/{evaluacion_id}",
    response_model=EvaluacionResponse,
    summary="HU-076: actualizar evaluación"
)
def actualizar(
    evaluacion_id: int,
    data: EvaluacionUpdate,
    db: Session = Depends(get_db)
):
    return EvaluacionService(db).actualizar(evaluacion_id, data)


@router.delete(
    "/{evaluacion_id}",
    status_code=status.HTTP_204_NO_CONTENT,
    summary="HU-076: eliminar evaluación"
)
def eliminar(evaluacion_id: int, db: Session = Depends(get_db)):
    EvaluacionService(db).eliminar(evaluacion_id)


@router.post(
    "/{evaluacion_id}/respuesta",
    response_model=EvaluacionResponse,
    summary="HU-076: responder evaluación (hotel)"
)
def responder(
    evaluacion_id: int,
    data: RespuestaHotelRequest,
    db: Session = Depends(get_db)
):
    return EvaluacionService(db).responder(evaluacion_id, data.respuesta)
