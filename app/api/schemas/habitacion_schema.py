# ─────────────────────────────────────────────────────────────
# SCHEMAS DE HABITACIÓN Y TARIFA — HU-021 (CRUD de habitaciones)
# ─────────────────────────────────────────────────────────────

from datetime import date, datetime
from decimal import Decimal

from pydantic import BaseModel, ConfigDict, Field, field_validator


class TipoHabitacionCreate(BaseModel):
    nombre: str = Field(..., min_length=2, max_length=100)
    descripcion: str | None = Field(None, max_length=500)


class TipoHabitacionResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: int
    nombre: str
    descripcion: str | None


class HabitacionCreate(BaseModel):
    hotel_id: int
    tipo_id: int
    numero: str = Field(..., min_length=1, max_length=20)
    capacidad: int = Field(..., ge=1, le=20)
    precio_base: Decimal = Field(..., gt=0)

    @field_validator("numero")
    @classmethod
    def numero_limpio(cls, v: str) -> str:
        return v.strip()


class HabitacionUpdate(BaseModel):
    tipo_id: int | None = None
    numero: str | None = Field(None, min_length=1, max_length=20)
    capacidad: int | None = Field(None, ge=1, le=20)
    precio_base: Decimal | None = Field(None, gt=0)
    estado: str | None = Field(
        None,
        description="disponible | ocupada | mantenimiento"
    )

    @field_validator("estado")
    @classmethod
    def estado_valido(cls, v: str | None) -> str | None:
        if v is None:
            return v
        if v not in ("disponible", "ocupada", "mantenimiento"):
            raise ValueError("Estado inválido: disponible | ocupada | mantenimiento")
        return v


class HabitacionResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: int
    numero: str
    capacidad: int
    precio_base: Decimal
    estado: str
    hotel_id: int
    tipo_id: int
    tipo_nombre: str | None = None
    hotel_nombre: str | None = None


class TarifaCreate(BaseModel):
    nombre: str = Field(..., min_length=2, max_length=100)
    precio_noche: Decimal = Field(..., gt=0)
    moneda: str = Field(default="COP", min_length=3, max_length=3)
    fecha_inicio: date
    fecha_fin: date
    activa: bool = True

    @field_validator("fecha_fin")
    @classmethod
    def fechas_validas(cls, v: date, info) -> date:
        inicio = info.data.get("fecha_inicio")
        if inicio and v <= inicio:
            raise ValueError("fecha_fin debe ser posterior a fecha_inicio")
        return v


class TarifaUpdate(BaseModel):
    nombre: str | None = Field(None, min_length=2, max_length=100)
    precio_noche: Decimal | None = Field(None, gt=0)
    fecha_inicio: date | None = None
    fecha_fin: date | None = None
    activa: bool | None = None


class TarifaResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: int
    nombre: str
    precio_noche: Decimal
    moneda: str
    fecha_inicio: date
    fecha_fin: date
    activa: bool
    habitacion_id: int
