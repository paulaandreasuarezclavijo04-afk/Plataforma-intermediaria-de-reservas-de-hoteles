# ─────────────────────────────────────────────────────────────
# SCHEMAS DE HOTEL — HU-016 (CRUD de hoteles)
# ─────────────────────────────────────────────────────────────

from pydantic import BaseModel, ConfigDict, Field, field_validator


class HotelCreate(BaseModel):
    nombre: str = Field(..., min_length=2, max_length=150)
    descripcion: str | None = Field(None, max_length=1000)
    direccion: str = Field(..., min_length=3, max_length=200)
    ciudad: str = Field(..., min_length=2, max_length=100)
    pais: str = Field(..., min_length=2, max_length=100)
    telefono: str | None = Field(None, max_length=30)
    propietario_id: int | None = Field(
        None,
        description="Si no se envía, se usa el primer propietario registrado"
    )


class HotelUpdate(BaseModel):
    nombre: str | None = Field(None, min_length=2, max_length=150)
    descripcion: str | None = Field(None, max_length=1000)
    direccion: str | None = Field(None, min_length=3, max_length=200)
    ciudad: str | None = Field(None, min_length=2, max_length=100)
    pais: str | None = Field(None, min_length=2, max_length=100)
    telefono: str | None = Field(None, max_length=30)


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
