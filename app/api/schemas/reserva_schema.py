# ─────────────────────────────────────────────────────────────
# SCHEMAS DE RESERVA — HU-036 (crear), HU-039 (consultar)
# y HU-068 (confirmación de reserva)
# ─────────────────────────────────────────────────────────────

from datetime import date, datetime
from decimal import Decimal

from pydantic import BaseModel, ConfigDict, Field, field_validator


class ReservaCreate(BaseModel):
    habitacion_id: int
    fecha_entrada: date
    fecha_salida: date
    huespedes: int = Field(
        ...,
        ge=1,
        description="Se valida contra la capacidad real de la habitación (400)"
    )
    usuario_id: int = Field(
        ...,
        description="Pendiente de reemplazar por el usuario de la sesión (JWT en v2)"
    )

    @field_validator("fecha_salida")
    @classmethod
    def fechas_validas(cls, v: date, info) -> date:
        entrada = info.data.get("fecha_entrada")
        if entrada and v <= entrada:
            raise ValueError("fecha_salida debe ser posterior a fecha_entrada")
        return v


class ResumenHabitacion(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: int
    numero: str
    hotel_id: int
    hotel_nombre: str | None = None


class ResumenUsuario(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: int
    nombres: str
    apellidos: str
    correo: str


class PagoResumen(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: int
    monto: Decimal
    metodo: str
    estado: str


class ReservaResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: int
    fecha_entrada: date
    fecha_salida: date
    huespedes: int
    total: Decimal
    estado: str
    fecha_creacion: datetime
    usuario_id: int
    habitacion_id: int


class ReservaDetalle(ReservaResponse):
    usuario: ResumenUsuario | None = None
    habitacion: ResumenHabitacion | None = None
    pagos: list[PagoResumen] = []
    confirmacion: dict | None = None


class CancelarReservaRequest(BaseModel):
    motivo: str | None = Field(None, max_length=500)


class ConfirmacionResponse(BaseModel):
    """HU-068 — confirmación de reserva enviada al huésped."""

    reserva_id: int
    estado: str
    notificacion_id: int | None
    asunto: str | None = None
    contenido: str | None = None
    fecha: datetime | None = None
