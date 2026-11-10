
from datetime import datetime
from decimal import Decimal

from sqlalchemy import (
    DateTime,
    ForeignKey,
    Numeric,
    String
)
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.repository.database.base import Base


class Pago(Base):
    __tablename__ = "pagos"

    id: Mapped[int] = mapped_column(primary_key=True)

    monto: Mapped[Decimal] = mapped_column(
        Numeric(10, 2),
        nullable=False
    )

    moneda: Mapped[str] = mapped_column(
        String(3),
        default="COP",
        nullable=False
    )

    metodo: Mapped[str] = mapped_column(
        String(50),
        nullable=False
    )

    estado: Mapped[str] = mapped_column(
        String(30),
        default="pendiente",
        nullable=False
    )

    referencia_externa: Mapped[str | None] = mapped_column(
        String(150),
        nullable=True
    )

    fecha_pago: Mapped[datetime | None] = mapped_column(
        DateTime,
        nullable=True
    )

    reserva_id: Mapped[int] = mapped_column(
        ForeignKey("reservas.id"),
        nullable=False
    )

    reserva: Mapped["Reserva"] = relationship(
        back_populates="pagos"
    )
