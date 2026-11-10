# ─────────────────────────────────────────────────────────────
# SCHEMAS DE AUTH — registro, login, validación de correo (HU-002)
# y recuperación de contraseña (HU-005)
# ─────────────────────────────────────────────────────────────

from pydantic import BaseModel, ConfigDict, Field, field_validator


class RegistroRequest(BaseModel):
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


class LoginRequest(BaseModel):
    correo: str
    password: str

    @field_validator("correo")
    @classmethod
    def correo_valido(cls, v: str) -> str:
        return v.strip().lower()


class UsuarioSesion(BaseModel):
    """Datos del usuario autenticado (token JWT pendiente en v2)."""

    model_config = ConfigDict(from_attributes=True)

    id: int
    nombres: str
    apellidos: str
    correo: str
    rol: str
    correo_verificado: bool


class LoginResponse(BaseModel):
    mensaje: str
    usuario: UsuarioSesion


class CorreoRequest(BaseModel):
    correo: str

    @field_validator("correo")
    @classmethod
    def correo_valido(cls, v: str) -> str:
        return v.strip().lower()


class ValidarCorreoRequest(BaseModel):
    token: str = Field(..., min_length=10, max_length=64)


class RecuperarPasswordRequest(BaseModel):
    token: str = Field(..., min_length=10, max_length=64)
    nueva_password: str = Field(..., min_length=6, max_length=128)


class MensajeResponse(BaseModel):
    mensaje: str
    detalle: str | None = None
