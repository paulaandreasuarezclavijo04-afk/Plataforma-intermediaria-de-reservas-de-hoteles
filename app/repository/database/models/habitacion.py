
from sqlalchemy import String, Integer, ForeignKey, Numeric, UniqueConstraint
from sqlalchemy.orm import Mapped, mapped_column, relationship
from decimal import Decimal

from app.repository.database.base import Base


class Habitacion(Base):
    __tablename__ = "habitaciones"

    __table_args__ = (
        UniqueConstraint(
            "hotel_id",
            "numero",
            name="uq_habitacion_hotel_numero"
        ),
    )

    id: Mapped[int] = mapped_column(primary_key=True)

    numero: Mapped[str] = mapped_column(
        String(20),
        nullable=False
    )

    capacidad: Mapped[int] = mapped_column(
        Integer,
        nullable=False
    )

    precio_base: Mapped[Decimal] = mapped_column(
        Numeric(10, 2),
        nullable=False
    )

    estado: Mapped[str] = mapped_column(
        String(30),
        default="disponible",
        nullable=False
    )

    hotel_id: Mapped[int] = mapped_column(
        ForeignKey("hoteles.id"),
        nullable=False
    )

    tipo_id: Mapped[int] = mapped_column(
        ForeignKey("tipos_habitacion.id"),
        nullable=False
    )

    hotel: Mapped["Hotel"] = relationship(
        back_populates="habitaciones"
    )

    tipo: Mapped["TipoHabitacion"] = relationship(
        back_populates="habitaciones"
    )

    tarifas: Mapped[list["Tarifa"]] = relationship(
        back_populates="habitacion"
    )

    reservas: Mapped[list["Reserva"]] = relationship(
        back_populates="habitacion"
    )

    @property
    def tipo_nombre(self) -> str | None:
        """Nombre del tipo de habitación (para las respuestas)."""
        if self.tipo:
            return self.tipo.nombre
        return None

    @property
    def hotel_nombre(self) -> str | None:
        """Nombre del hotel (para las respuestas)."""
        if self.hotel:
            return self.hotel.nombre
        return None
