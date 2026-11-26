# ─────────────────────────────────────────────────────────────
# SCHEMAS DE NOTIFICACIONES — HU-068
# ─────────────────────────────────────────────────────────────

from datetime import datetime
from typing import Generic, TypeVar

from pydantic import BaseModel, Field

T = TypeVar("T")


class ApiResponse(BaseModel, Generic[T]):
    mensaje: str
    data: T | None = None
    success: bool = True


class ConfirmacionReservaRequest(BaseModel):
    reserva_id: int = Field(..., gt=0)
    canal: str = Field(default="EMAIL", min_length=2, max_length=30)


class ConfirmacionReservaData(BaseModel):
    reserva_id: int
    canal: str
    estado: str
    notificacion_id: int | None = None
    fecha: datetime | None = None
    resultado: str | None = None
