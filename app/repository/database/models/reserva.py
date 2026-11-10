
from datetime import date, datetime
from decimal import Decimal

from sqlalchemy import (
    Date,
    DateTime,
    ForeignKey,
    Integer,
    Numeric,
    String,
    CheckConstraint
)
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.repository.database.base import Base


class Reserva(Base):
    __tablename__ = "reservas"

    __table_args__ = (
        CheckConstraint(
            "fecha_salida > fecha_entrada",
            name="ck_reserva_fechas"
        ),
        CheckConstraint(
            "huespedes > 0",
            name="ck_reserva_huespedes"
        ),
    )

    id: Mapped[int] = mapped_column(primary_key=True)

    fecha_entrada: Mapped[date] = mapped_column(
        Date,
        nullable=False
    )

    fecha_salida: Mapped[date] = mapped_column(
        Date,
        nullable=False
    )

    huespedes: Mapped[int] = mapped_column(
        Integer,
        nullable=False
    )

    total: Mapped[Decimal] = mapped_column(
        Numeric(10, 2),
        nullable=False
    )

    estado: Mapped[str] = mapped_column(
        String(30),
        default="pendiente",
        nullable=False
    )

    fecha_creacion: Mapped[datetime] = mapped_column(
        DateTime,
        default=datetime.utcnow
    )

    usuario_id: Mapped[int] = mapped_column(
        ForeignKey("usuarios.id"),
        nullable=False
    )

    habitacion_id: Mapped[int] = mapped_column(
        ForeignKey("habitaciones.id"),
        nullable=False
    )

    usuario: Mapped["Usuario"] = relationship(
        back_populates="reservas"
    )

    habitacion: Mapped["Habitacion"] = relationship(
        back_populates="reservas"
    )

    pagos: Mapped[list["Pago"]] = relationship(
        back_populates="reserva"
    )

    evaluacion: Mapped["Evaluacion | None"] = relationship(
        back_populates="reserva"
    )

    solicitudes_asistencia: Mapped[list["SolicitudAsistencia"]] = relationship(
        back_populates="reserva"
    )

    notificaciones: Mapped[list["Notificacion"]] = relationship(
        back_populates="reserva"
    )
