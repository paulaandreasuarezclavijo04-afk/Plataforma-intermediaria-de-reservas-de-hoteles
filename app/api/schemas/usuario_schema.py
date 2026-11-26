# ─────────────────────────────────────────────────────────────
# SCHEMAS DE USUARIO — HU-001 (CRUD de usuarios)
# ─────────────────────────────────────────────────────────────

from typing import Generic, TypeVar

from pydantic import BaseModel, ConfigDict, Field, field_validator

T = TypeVar("T")


class ApiResponse(BaseModel, Generic[T]):
    mensaje: str
    data: T | None = None
    success: bool = True


class UsuarioData(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: int
    nombre: str
    correo: str
    rol: str
    activo: bool = True
    telefono: str | None = None


class UsuarioCreate(BaseModel):
    nombre: str | None = Field(None, min_length=2, max_length=200, description="Nombre completo")
    nombres: str | None = Field(None, min_length=2, max_length=100, description="Nombres (alternativo)")
    apellidos: str | None = Field(None, min_length=2, max_length=100, description="Apellidos (alternativo)")
    correo: str = Field(..., min_length=5, max_length=150, description="Correo electrónico único")
    telefono: str | None = Field(None, max_length=30, description="Teléfono opcional")
    rol: str | int = Field(default="HUESPED", description="Rol: admin | propietario | huesped (o rol_id)")
    password: str = Field(..., min_length=6, max_length=128, description="Contraseña del usuario")

    @field_validator("correo")
    @classmethod
    def correo_valido(cls, v: str) -> str:
        v = v.strip().lower()
        if "@" not in v or "." not in v.split("@")[-1]:
            raise ValueError("Correo electrónico inválido")
        return v

    @field_validator("telefono")
    @classmethod
    def telefono_valido(cls, v: str | None) -> str | None:
        if v is not None:
            numeros = "".join(filter(str.isdigit, v))
            if len(numeros) > 15:
                raise ValueError("El teléfono no puede tener más de 15 dígitos")
            if len(numeros) > 0 and len(numeros) < 7:
                raise ValueError("El teléfono debe tener al menos 7 dígitos")
        return v


class UsuarioUpdate(BaseModel):
    nombre: str | None = Field(None, min_length=2, max_length=200)
    nombres: str | None = Field(None, min_length=2, max_length=100)
    apellidos: str | None = Field(None, min_length=2, max_length=100)
    correo: str | None = Field(None, min_length=5, max_length=150)
    telefono: str | None = Field(None, max_length=30)
    activo: bool | None = Field(None, description="Activar/desactivar usuario")

    @field_validator("correo")
    @classmethod
    def correo_valido(cls, v: str | None) -> str | None:
        if v is not None:
            v = v.strip().lower()
            if "@" not in v or "." not in v.split("@")[-1]:
                raise ValueError("Correo electrónico inválido")
        return v


class UsuarioAsignarRol(BaseModel):
    rol: str | int = Field(..., description="Rol a asignar: admin | propietario | huesped (o rol_id)")


class ValidarCorreoRequest(BaseModel):
    correo: str = Field(..., min_length=1, max_length=150)

    @field_validator("correo")
    @classmethod
    def correo_valido(cls, v: str) -> str:
        v = v.strip().lower()
        if not v:
            raise ValueError("El correo es obligatorio")
        if "@" not in v or "." not in v.split("@")[-1] or v.startswith("@") or v.endswith("@"):
            raise ValueError("Formato de correo inválido")
        return v


class ValidarCorreoData(BaseModel):
    correo: str
    disponible: bool


# Compatibilidad con nombres anteriores usados en otras partes
UsuarioResponse = UsuarioData