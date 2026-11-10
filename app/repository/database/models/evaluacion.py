
from datetime import datetime

from sqlalchemy import (
    CheckConstraint,
    DateTime,
    ForeignKey,
    Integer,
    String,
    Text,
    UniqueConstraint
)
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.repository.database.base import Base


class Evaluacion(Base):
    __tablename__ = "evaluaciones"

    __table_args__ = (
        CheckConstraint(
            "puntuacion >= 1 AND puntuacion <= 5",
            name="ck_evaluacion_puntuacion"
        ),
        UniqueConstraint(
            "reserva_id",
            name="uq_evaluacion_reserva"
        ),
    )

    id: Mapped[int] = mapped_column(primary_key=True)

    puntuacion: Mapped[int] = mapped_column(
        Integer,
        nullable=False
    )

    comentario: Mapped[str | None] = mapped_column(
        Text,
        nullable=True
    )

    respuesta_hotel: Mapped[str | None] = mapped_column(
        Text,
        nullable=True
    )

    fecha_creacion: Mapped[datetime] = mapped_column(
        DateTime,
        default=datetime.utcnow
    )

    fecha_respuesta: Mapped[datetime | None] = mapped_column(
        DateTime,
        nullable=True
    )

    usuario_id: Mapped[int] = mapped_column(
        ForeignKey("usuarios.id"),
        nullable=False
    )

    hotel_id: Mapped[int] = mapped_column(
        ForeignKey("hoteles.id"),
        nullable=False
    )

    reserva_id: Mapped[int] = mapped_column(
        ForeignKey("reservas.id"),
        nullable=False
    )

    usuario: Mapped["Usuario"] = relationship(
        back_populates="evaluaciones"
    )

    hotel: Mapped["Hotel"] = relationship(
        back_populates="evaluaciones"
    )

    reserva: Mapped["Reserva"] = relationship(
        back_populates="evaluacion"
    )

    @property
    def autor(self) -> str | None:
        """Nombre del huésped que dejó la evaluación."""
        if self.usuario:
            return f"{self.usuario.nombres} {self.usuario.apellidos}"
        return None
