# ─────────────────────────────────────────────────────────────
# SCHEMAS DE USUARIO — HU-001 (CRUD de usuarios)
# ─────────────────────────────────────────────────────────────

from pydantic import BaseModel, ConfigDict, Field, validator


class UsuarioCreate(BaseModel):
    nombres: str = Field(..., min_length=2, max_length=100, description="Nombres del usuario")
    apellidos: str = Field(..., min_length=2, max_length=100, description="Apellidos del usuario")
    correo: str = Field(..., min_length=5, max_length=150, description="Correo electrónico único")
    telefono: str | None = Field(None, max_length=30, description="Teléfono opcional")
    rol_id: int = Field(..., description="ID del rol (1=admin, 2=propietario, 3=huesped)")

    @validator("correo")
    @classmethod
    def correo_valido(cls, v: str) -> str:
        v = v.strip().lower()
        if "@" not in v or "." not in v.split("@")[-1]:
            raise ValueError("Correo electrónico inválido")
        return v

    @validator("telefono")
    @classmethod
    def telefono_solo_numeros(cls, v: str | None) -> str | None:
        if v is not None:
            numeros = "".join(filter(str.isdigit, v))
            if len(numeros) > 15:
                raise ValueError("El teléfono no puede tener más de 15 dígitos")
            if len(numeros) > 0 and len(numeros) < 7:
                raise ValueError("El teléfono debe tener al menos 7 dígitos")
        return v


class UsuarioUpdate(BaseModel):
    nombres: str | None = Field(None, min_length=2, max_length=100)
    apellidos: str | None = Field(None, min_length=2, max_length=100)
    correo: str | None = Field(None, min_length=5, max_length=150)
    telefono: str | None = Field(None, max_length=30)
    activo: bool | None = Field(None, description="Activar/desactivar usuario")

    @validator("correo")
    @classmethod
    def correo_valido_actualizacion(cls, v: str | None) -> str | None:
        if v is not None:
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
    rol_nombre: str

    @validator("rol_nombre", always=True)
    @classmethod
    def obtener_rol_nombre(cls, v, values):
        obj = values["obj"] if "obj" in values else None
        if obj and hasattr(obj, "rol_nombre"):
            return obj.rol_nombre
        return "huesped"


class UsuarioAsignarRol(BaseModel):
    rol_id: int = Field(..., description="ID del rol a asignar (1=admin, 2=propietario, 3=huesped)")