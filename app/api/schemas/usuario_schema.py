# ─────────────────────────────────────────────────────────────
# SCHEMAS DE USUARIO — HU-001 (CRUD de usuarios)
# ─────────────────────────────────────────────────────────────

from datetime import datetime

from pydantic import BaseModel, ConfigDict, Field, field_validator


class UsuarioCreate(BaseModel):
    nombres: str = Field(..., min_length=2, max_length=100)
    apellidos: str = Field(..., min_length=2, max_length=100)
    correo: str = Field(..., max_length=150)
    password: str = Field(..., min_length=6, max_length=128)
    telefono: str | None = Field(None, max_length=30)
    rol: str = Field(default="huesped", description="admin | propietario | huesped")

    @field_validator("correo")
    @classmethod
    def correo_valido(cls, v: str) -> str:
        v = v.strip().lower()
        if "@" not in v or "." not in v.split("@")[-1]:
            raise ValueError("Correo electrónico inválido")
        return v


class UsuarioUpdate(BaseModel):
    nombres: str | None = Field(None, min_length=2, max_length=100)
    apellidos: str | None = Field(None, min_length=2, max_length=100)
    correo: str | None = Field(None, max_length=150)
    telefono: str | None = Field(None, max_length=30)
    password: str | None = Field(None, min_length=6, max_length=128)
    rol: str | None = None
    activo: bool | None = None

    @field_validator("correo")
    @classmethod
    def correo_valido(cls, v: str | None) -> str | None:
        if v is None:
            return v
        v = v.strip().lower()
        if "@" not in v or "." not in v.split("@")[-1]:
            raise ValueError("Correo electrónico inválido")
        return v


class UsuarioResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: int
    nombres: str
    apellidos: str
    correo: str
    telefono: str | None
    activo: bool
    correo_verificado: bool
    rol_nombre: str | None = None
    fecha_creacion: datetime
