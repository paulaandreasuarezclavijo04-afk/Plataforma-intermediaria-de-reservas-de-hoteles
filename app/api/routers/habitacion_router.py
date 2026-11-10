# ─────────────────────────────────────────────────────────────
# ROUTER DE HABITACIONES — HU-021 (CRUD de habitaciones + tarifas)
# ─────────────────────────────────────────────────────────────

from fastapi import APIRouter, Depends, Query, status
from sqlalchemy.orm import Session

from app.api.schemas.habitacion_schema import (
    HabitacionCreate,
    HabitacionResponse,
    HabitacionUpdate,
    TarifaCreate,
    TarifaResponse,
    TarifaUpdate,
    TipoHabitacionCreate,
    TipoHabitacionResponse
)
from app.repository.database.session import get_db
from app.services.habitacion_service import HabitacionService

router = APIRouter(prefix="/api/habitaciones", tags=["Habitaciones"])


# ── Tipos de habitación (antes de /{id}) ────────────────────
@router.get(
    "/tipos",
    response_model=list[TipoHabitacionResponse],
    summary="HU-021: listar tipos de habitación"
)
def listar_tipos(db: Session = Depends(get_db)):
    return HabitacionService(db).listar_tipos()


@router.post(
    "/tipos",
    response_model=TipoHabitacionResponse,
    status_code=status.HTTP_201_CREATED,
    summary="HU-021: crear tipo de habitación"
)
def crear_tipo(data: TipoHabitacionCreate, db: Session = Depends(get_db)):
    return HabitacionService(db).crear_tipo(data)


# ── Habitaciones ────────────────────────────────────────────
@router.get(
    "",
    response_model=list[HabitacionResponse],
    summary="HU-021: listar habitaciones de un hotel"
)
def listar(
    hotel_id: int = Query(..., description="Hotel a consultar"),
    incluir_todos: bool = Query(False, description="Incluir mantenimiento"),
    db: Session = Depends(get_db)
):
    return HabitacionService(db).listar(
        hotel_id, incluir_todos=incluir_todos
    )


@router.post(
    "",
    response_model=HabitacionResponse,
    status_code=status.HTTP_201_CREATED,
    summary="HU-021: crear habitación"
)
def crear(data: HabitacionCreate, db: Session = Depends(get_db)):
    return HabitacionService(db).crear(data)


@router.get(
    "/{habitacion_id}",
    response_model=HabitacionResponse,
    summary="HU-021: consultar habitación"
)
def obtener(habitacion_id: int, db: Session = Depends(get_db)):
    return HabitacionService(db).obtener(habitacion_id)


@router.put(
    "/{habitacion_id}",
    response_model=HabitacionResponse,
    summary="HU-021: actualizar habitación"
)
def actualizar(
    habitacion_id: int,
    data: HabitacionUpdate,
    db: Session = Depends(get_db)
):
    return HabitacionService(db).actualizar(habitacion_id, data)


@router.delete(
    "/{habitacion_id}",
    status_code=status.HTTP_204_NO_CONTENT,
    summary="HU-021: eliminar habitación (si no tiene reservas)"
)
def eliminar(habitacion_id: int, db: Session = Depends(get_db)):
    HabitacionService(db).eliminar(habitacion_id)


# ── Tarifas ─────────────────────────────────────────────────
@router.get(
    "/{habitacion_id}/tarifas",
    response_model=list[TarifaResponse],
    summary="HU-021: listar tarifas de una habitación"
)
def listar_tarifas(habitacion_id: int, db: Session = Depends(get_db)):
    return HabitacionService(db).listar_tarifas(habitacion_id)


@router.post(
    "/{habitacion_id}/tarifas",
    response_model=TarifaResponse,
    status_code=status.HTTP_201_CREATED,
    summary="HU-021: crear tarifa"
)
def crear_tarifa(
    habitacion_id: int,
    data: TarifaCreate,
    db: Session = Depends(get_db)
):
    return HabitacionService(db).crear_tarifa(habitacion_id, data)


@router.put(
    "/tarifas/{tarifa_id}",
    response_model=TarifaResponse,
    summary="HU-021: actualizar tarifa"
)
def actualizar_tarifa(
    tarifa_id: int,
    data: TarifaUpdate,
    db: Session = Depends(get_db)
):
    return HabitacionService(db).actualizar_tarifa(tarifa_id, data)


@router.delete(
    "/tarifas/{tarifa_id}",
    status_code=status.HTTP_204_NO_CONTENT,
    summary="HU-021: eliminar tarifa"
)
def eliminar_tarifa(tarifa_id: int, db: Session = Depends(get_db)):
    HabitacionService(db).eliminar_tarifa(tarifa_id)
