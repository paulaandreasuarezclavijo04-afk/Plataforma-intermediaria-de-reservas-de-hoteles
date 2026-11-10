# ─────────────────────────────────────────────────────────────
# SCHEMAS DE EVALUACIÓN — HU-076 (CRUD de evaluaciones)
# ─────────────────────────────────────────────────────────────

from datetime import datetime
from decimal import Decimal

from pydantic import BaseModel, ConfigDict, Field, field_validator


class EvaluacionCreate(BaseModel):
    """Solo se evalúa la reserva en la que se hospedó el usuario."""

    reserva_id: int
    puntuacion: int = Field(..., ge=1, le=5)
    comentario: str | None = Field(None, max_length=2000)


class EvaluacionUpdate(BaseModel):
    puntuacion: int | None = Field(None, ge=1, le=5)
    comentario: str | None = Field(None, max_length=2000)


class RespuestaHotelRequest(BaseModel):
    respuesta: str = Field(..., min_length=2, max_length=2000)


class EvaluacionResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: int
    puntuacion: int
    comentario: str | None
    respuesta_hotel: str | None
    fecha_creacion: datetime
    fecha_respuesta: datetime | None
    usuario_id: int
    hotel_id: int
    reserva_id: int
    autor: str | None = None


class ResumenHotelEvaluaciones(BaseModel):
    hotel_id: int
    total_evaluaciones: int
    promedio: Decimal
    distribucion: dict
