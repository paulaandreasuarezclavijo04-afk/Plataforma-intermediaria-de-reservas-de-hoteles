# ─────────────────────────────────────────────────────────────
# SCHEMAS DE PAGO — HU-062 (enviar solicitud de pago)
# y HU-052 (procesar pago)
# ─────────────────────────────────────────────────────────────

from datetime import datetime
from decimal import Decimal

from pydantic import BaseModel, ConfigDict, Field, field_validator

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
