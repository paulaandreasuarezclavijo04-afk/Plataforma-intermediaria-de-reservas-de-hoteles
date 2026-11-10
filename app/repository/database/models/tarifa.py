
from datetime import date

from sqlalchemy import (
    String, Boolean, Date, ForeignKey, Numeric
)
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.repository.database.base import Base
from decimal import Decimal

class Tarifa(Base):
    __tablename__ = "tarifas"

    id: Mapped[int] = mapped_column(primary_key=True)

    nombre: Mapped[str] = mapped_column(
        String(100),
        nullable=False
    )

    precio_noche: Mapped[Decimal] = mapped_column(
        Numeric(10, 2),
        nullable=False
    )

    moneda: Mapped[str] = mapped_column(
        String(3),
        default="COP",
        nullable=False
    )

    fecha_inicio: Mapped[date] = mapped_column(
        Date,
        nullable=False
    )

    fecha_fin: Mapped[date] = mapped_column(
        Date,
        nullable=False
    )

    activa: Mapped[bool] = mapped_column(
        Boolean,
        default=True,
        nullable=False
    )

    habitacion_id: Mapped[int] = mapped_column(
        ForeignKey("habitaciones.id"),
        nullable=False
    )

    habitacion: Mapped["Habitacion"] = relationship(
        back_populates="tarifas"
    )
