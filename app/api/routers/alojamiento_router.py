# ─────────────────────────────────────────────────────────────
# ROUTER DE ALOJAMIENTO — HU-031 (buscar alojamiento)
# y HU-033 (consultar disponibilidad)
# ─────────────────────────────────────────────────────────────

from datetime import date
from decimal import Decimal

from fastapi import APIRouter, Depends, Query
from sqlalchemy.orm import Session

from app.api.schemas.alojamiento_schema import (
    BusquedaRequest,
    DisponibilidadRequest,
    DisponibilidadResponse,
    ResultadoBusqueda
)
from app.repository.database.session import get_db
from app.services.alojamiento_service import AlojamientoService

router = APIRouter(prefix="/api/alojamientos", tags=["Alojamientos"])


@router.get(
    "/buscar",
    response_model=list[ResultadoBusqueda],
    summary="HU-031: buscar alojamientos disponibles por ciudad y fechas"
)
def buscar(
    fecha_entrada: date = Query(..., description="YYYY-MM-DD"),
    fecha_salida: date = Query(..., description="YYYY-MM-DD"),
    huespedes: int = Query(1, ge=1, le=20),
    ciudad: str | None = Query(None),
    precio_max: Decimal | None = Query(None, gt=0),
    tipo: str | None = Query(None, description="Tipo de habitación"),
    db: Session = Depends(get_db)
):
    data = BusquedaRequest(
        fecha_entrada=fecha_entrada,
        fecha_salida=fecha_salida,
        huespedes=huespedes,
        ciudad=ciudad,
        precio_max=precio_max,
        tipo=tipo
    )
    return AlojamientoService(db).buscar(data)


@router.get(
    "/disponibilidad/{habitacion_id}",
    response_model=DisponibilidadResponse,
    summary="HU-033: consultar disponibilidad y precio de una habitación"
)
def disponibilidad(
    habitacion_id: int,
    fecha_entrada: date = Query(..., description="YYYY-MM-DD"),
    fecha_salida: date = Query(..., description="YYYY-MM-DD"),
    db: Session = Depends(get_db)
):
    data = DisponibilidadRequest(
        fecha_entrada=fecha_entrada,
        fecha_salida=fecha_salida
    )
    return AlojamientoService(db).disponibilidad(habitacion_id, data)
