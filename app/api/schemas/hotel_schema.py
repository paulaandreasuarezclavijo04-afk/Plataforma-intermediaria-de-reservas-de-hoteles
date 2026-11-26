# ─────────────────────────────────────────────────────────────
# SCHEMAS DE HOTEL — HU-016 (CRUD de hoteles)
# ─────────────────────────────────────────────────────────────

from datetime import date
from decimal import Decimal
from typing import Generic, TypeVar

from pydantic import BaseModel, ConfigDict, Field, field_validator

T = TypeVar("T")


class HotelCreate(BaseModel):
    nombre: str = Field(..., min_length=2, max_length=150)

    descripcion: str | None = Field(None, max_length=1000)

    direccion: str = Field(..., min_length=3, max_length=200)

    ciudad: str = Field(..., min_length=2, max_length=100)

    pais: str = Field(..., min_length=2, max_length=100)

    telefono: str | None = Field(None, max_length=30, description="Formato: solo números, máximo 15 dígitos")

    propietario_id: int | None = Field(
        None,
        description="Si no se envía, se usa el primer propietario registrado"
    )

    @field_validator("nombre")
    @classmethod
    def nombre_titlecase(cls, v: str) -> str:
        return v.strip().title()

    @field_validator("ciudad")
    @classmethod
    def ciudad_titlecase(cls, v: str) -> str:
        return v.strip().title()

    @field_validator("pais")
    @classmethod
    def pais_titlecase(cls, v: str) -> str:
        return v.strip().title()

    @field_validator("telefono")
    @classmethod
    def telefono_solo_numeros(cls, v: str | None) -> str | None:
        if v is not None:
            numeros = "".join(filter(str.isdigit, v))
            if len(numeros) > 15:
                raise ValueError("El teléfono no puede tener más de 15 dígitos")
            if len(numeros) < 7:
                raise ValueError("El teléfono debe tener al menos 7 dígitos")
        return v


class HotelUpdate(BaseModel):
    nombre: str | None = Field(None, min_length=2, max_length=150)

    descripcion: str | None = Field(None, max_length=1000)

    direccion: str | None = Field(None, min_length=3, max_length=200)

    ciudad: str | None = Field(None, min_length=2, max_length=100)

    pais: str | None = Field(None, min_length=2, max_length=100)

    telefono: str | None = Field(None, max_length=30, description="Formato: solo números, máximo 15 dígitos")

    model_config = ConfigDict(populate_by_name=True)

    @field_validator("nombre")
    @classmethod
    def nombre_titlecase_if_provided(cls, v: str | None) -> str | None:
        if v is not None:
            return v.strip().title()
        return v

    @field_validator("ciudad")
    @classmethod
    def ciudad_titlecase_if_provided(cls, v: str | None) -> str | None:
        if v is not None:
            return v.strip().title()
        return v

    @field_validator("pais")
    @classmethod
    def pais_titlecase_if_provided(cls, v: str | None) -> str | None:
        if v is not None:
            return v.strip().title()
        return v

    @field_validator("telefono")
    @classmethod
    def telefono_solo_numeros_if_provided(cls, v: str | None) -> str | None:
        if v is not None:
            numeros = "".join(filter(str.isdigit, v))
            if len(numeros) > 15:
                raise ValueError("El teléfono no puede tener más de 15 dígitos")
            if len(numeros) < 7:
                raise ValueError("El teléfono debe tener al menos 7 dígitos")
        return v


class HotelResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: int
    nombre: str
    descripcion: str | None
    direccion: str
    ciudad: str
    pais: str
    telefono: str | None
    activo: bool
    propietario_id: int
    propietario_nombre: str | None = None


class ApiResponse(BaseModel, Generic[T]):
    mensaje: str
    data: T | None = None
    success: bool = True


class HabitacionDisponibilidad(BaseModel):
    id: int
    tipo: str
    capacidad: int
    tarifa_noche: Decimal


class DisponibilidadHotelData(BaseModel):
    fecha_entrada: date
    fecha_salida: date
    habitaciones: list[HabitacionDisponibilidad]