# ─────────────────────────────────────────────────────────────
# SCHEMAS DE PAGO — HU-062 (enviar solicitud de pago)
# y HU-052 (procesar pago)
# ─────────────────────────────────────────────────────────────

from datetime import datetime
from decimal import Decimal

from typing import Generic, TypeVar

from pydantic import BaseModel, ConfigDict, Field, field_validator

T = TypeVar("T")

METODOS_VALIDOS = ("tarjeta", "transferencia", "efectivo", "simulado")


class SolicitudPagoCreate(BaseModel):
    """HU-062: el huésped solicita pagar una reserva."""

    reserva_id: int
    metodo: str = Field(default="simulado")

    @field_validator("metodo")
    @classmethod
    def metodo_valido(cls, v: str) -> str:
        if v not in METODOS_VALIDOS:
            raise ValueError(f"Método inválido: {' | '.join(METODOS_VALIDOS)}")
        return v


class ProcesarPagoRequest(BaseModel):
    """HU-052: datos simulados de la pasarela de pago."""

    numero_tarjeta: str | None = Field(
        None,
        max_length=25,
        description="Simulación: termina en 0000 => pago rechazado"
    )
    titular: str | None = Field(None, max_length=150)


class PagoResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: int
    monto: Decimal
    moneda: str
    metodo: str
    estado: str
    referencia_externa: str | None
    fecha_pago: datetime | None
    reserva_id: int


class ReembolsoRequest(BaseModel):
    motivo: str | None = Field(None, max_length=500)


# ── HU-052 v1 ───────────────────────────────────────────────
class IniciarPagoRequest(BaseModel):
    metodo_pago: str = Field(default="PROVEEDOR_EXTERNO", min_length=2, max_length=50)
    idempotency_key: str = Field(..., min_length=3, max_length=120)


class PagoIniciadoData(BaseModel):
    pago_id: int
    reserva_id: int
    estado: str
    url_proveedor: str | None = None
    referencia_externa: str | None = None
    monto: Decimal
    moneda: str


class PagoDetalleData(BaseModel):
    pago_id: int
    reserva_id: int
    estado: str
    metodo: str
    monto: Decimal
    moneda: str
    referencia_externa: str | None = None
    url_proveedor: str | None = None
    fecha_creacion: datetime | None = None
    fecha_pago: datetime | None = None


class ApiResponse(BaseModel, Generic[T]):
    mensaje: str
    data: T | None = None
    success: bool = True
