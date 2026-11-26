# ─────────────────────────────────────────────────────────────
# SCHEMAS DE BÚSQUEDA — HU-031 (buscar alojamiento)
# y HU-033 (consultar disponibilidad)
# ─────────────────────────────────────────────────────────────

from datetime import date
from decimal import Decimal

from pydantic import BaseModel, Field, field_validator


class BusquedaRequest(BaseModel):
    """Parámetros de búsqueda de alojamiento (HU-031)."""

    ciudad: str | None = Field(None, max_length=100)
    fecha_entrada: date
    fecha_salida: date
    huespedes: int = Field(default=1, ge=1, le=20)
    precio_max: Decimal | None = Field(None, gt=0)
    tipo: str | None = Field(None, max_length=100, description="Tipo de habitación")

    @field_validator("fecha_salida")
    @classmethod
    def fechas_validas(cls, v: date, info) -> date:
        entrada = info.data.get("fecha_entrada")
        if entrada and v <= entrada:
            raise ValueError("fecha_salida debe ser posterior a fecha_entrada")
        return v


class HabitacionDisponible(BaseModel):
    habitacion_id: int
    numero: str
    tipo: str
    capacidad: int
    precio_base: Decimal
    precio_total: Decimal
    noches: int


class ResultadoBusqueda(BaseModel):
    hotel_id: int
    nombre: str
    ciudad: str
    pais: str
    direccion: str
    telefono: str | None
    habitaciones_disponibles: list[HabitacionDisponible]


class DisponibilidadRequest(BaseModel):
    """Consulta puntual de disponibilidad de una habitación (HU-033)."""

    fecha_entrada: date
    fecha_salida: date

    @field_validator("fecha_salida")
    @classmethod
    def fechas_validas(cls, v: date, info) -> date:
        entrada = info.data.get("fecha_entrada")
        if entrada and v <= entrada:
            raise ValueError("fecha_salida debe ser posterior a fecha_entrada")
        return v


class DisponibilidadResponse(BaseModel):
    habitacion_id: int
    hotel_id: int
    hotel: str
    fecha_entrada: date
    fecha_salida: date
    noches: int
    disponible: bool
    motivo: str | None = None
    precio_total: Decimal
    desglose: list[dict]
