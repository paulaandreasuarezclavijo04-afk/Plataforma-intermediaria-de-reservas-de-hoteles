# ─────────────────────────────────────────────────────────────
# ROUTER DE HOTELES — HU-016 (CRUD de hoteles)
# ─────────────────────────────────────────────────────────────

from datetime import date

from fastapi import APIRouter, Depends, Query, status
from sqlalchemy.orm import Session

from app.api.schemas.hotel_schema import (
    ApiResponse,
    DisponibilidadHotelData,
    HabitacionDisponibilidad,
    HotelCreate,
    HotelResponse,
    HotelUpdate,
)
from app.repository.database.session import get_db
from app.services.hotel_service import HotelService

router = APIRouter(prefix="/api/hoteles", tags=["Hoteles"])


@router.get(
    "",
    response_model=list[HotelResponse],
    summary="HU-016: buscar hoteles por ciudad, país o nombre"
)
def listar(
    ciudad: str | None = Query(None),
    pais: str | None = Query(None),
    nombre: str | None = Query(None),
    incluir_inactivos: bool = Query(False),
    db: Session = Depends(get_db)
):
    return HotelService(db).listar(
        ciudad=ciudad,
        pais=pais,
        nombre=nombre,
        incluir_inactivos=incluir_inactivos
    )


@router.get(
    "/{hotel_id}",
    response_model=HotelResponse,
    summary="HU-016: consultar hotel"
)
def obtener(hotel_id: int, db: Session = Depends(get_db)):
    return HotelService(db).obtener(hotel_id)


@router.post(
    "",
    response_model=HotelResponse,
    status_code=status.HTTP_201_CREATED,
    summary="HU-016: crear hotel"
)
def crear(data: HotelCreate, db: Session = Depends(get_db)):
    return HotelService(db).crear(data)


@router.put(
    "/{hotel_id}",
    response_model=HotelResponse,
    summary="HU-016: actualizar hotel"
)
def actualizar(
    hotel_id: int,
    data: HotelUpdate,
    db: Session = Depends(get_db)
):
    return HotelService(db).actualizar(hotel_id, data)


@router.delete(
    "/{hotel_id}",
    response_model=HotelResponse,
    summary="HU-016: desactivar hotel (borrado lógico)"
)
def eliminar(hotel_id: int, db: Session = Depends(get_db)):
    return HotelService(db).eliminar(hotel_id)


# ── HU-033 (v1) ─────────────────────────────────────────────
v1_router = APIRouter(prefix="/api/v1/hoteles", tags=["Hoteles"])


@v1_router.get(
    "/{hotel_id}/disponibilidad",
    response_model=ApiResponse[DisponibilidadHotelData],
    summary="HU-033: consultar disponibilidad de un hotel",
)
def consultar_disponibilidad(
    hotel_id: int,
    fecha_entrada: date = Query(..., description="YYYY-MM-DD"),
    fecha_salida: date = Query(..., description="YYYY-MM-DD"),
    huespedes: int = Query(..., ge=1, description="Número de huéspedes"),
    db: Session = Depends(get_db),
):
    habitaciones = HotelService(db).consultar_disponibilidad(
        hotel_id=hotel_id,
        fecha_entrada=fecha_entrada,
        fecha_salida=fecha_salida,
        huespedes=huespedes,
    )
    data = DisponibilidadHotelData(
        fecha_entrada=fecha_entrada,
        fecha_salida=fecha_salida,
        habitaciones=[HabitacionDisponibilidad(**h) for h in habitaciones],
    )
    return ApiResponse(
        mensaje="Consulta de disponibilidad exitosa",
        data=data,
        success=True,
    )
