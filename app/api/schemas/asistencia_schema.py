# ─────────────────────────────────────────────────────────────
# SCHEMAS DE ASISTENCIA — HU-092 (crear solicitud de asistencia)
# ─────────────────────────────────────────────────────────────

from datetime import datetime

from pydantic import BaseModel, ConfigDict, Field, field_validator

TIPOS_VALIDOS = ("consulta", "queja", "solicitud", "incidencia")
ESTADOS_VALIDOS = ("abierta", "en_proceso", "respondida", "cerrada")


class AsistenciaCreate(BaseModel):
    asunto: str = Field(..., min_length=3, max_length=150)
    descripcion: str = Field(..., min_length=10, max_length=4000)
    tipo: str = Field(default="consulta")
    usuario_id: int = Field(
        ...,
        description="Pendiente de reemplazar por el usuario de la sesión (JWT en v2)"
    )
    reserva_id: int | None = Field(
        None,
        description="Reserva relacionada con la solicitud (opcional)"
    )

    @field_validator("tipo")
    @classmethod
    def tipo_valido(cls, v: str) -> str:
        if v not in TIPOS_VALIDOS:
            raise ValueError(f"Tipo inválido: {' | '.join(TIPOS_VALIDOS)}")
        return v


class AsistenciaUpdate(BaseModel):
    """Actualización de estado por parte del equipo de soporte."""

    estado: str
    respuesta: str | None = Field(None, max_length=4000)

    @field_validator("estado")
    @classmethod
    def estado_valido(cls, v: str) -> str:
        if v not in ESTADOS_VALIDOS:
            raise ValueError(f"Estado inválido: {' | '.join(ESTADOS_VALIDOS)}")
        return v


class AsistenciaResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: int
    asunto: str
    descripcion: str
    tipo: str
    estado: str
    respuesta: str | None
    fecha_creacion: datetime
    fecha_cierre: datetime | None
    usuario_id: int
    reserva_id: int | None
