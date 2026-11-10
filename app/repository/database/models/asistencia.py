
from datetime import datetime

from sqlalchemy import (
    CheckConstraint,
    DateTime,
    ForeignKey,
    String,
    Text
)
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.repository.database.base import Base


class SolicitudAsistencia(Base):
    __tablename__ = "solicitudes_asistencia"

    __table_args__ = (
        CheckConstraint(
            "estado IN ('abierta', 'en_proceso', 'respondida', 'cerrada')",
            name="ck_asistencia_estado"
        ),
        CheckConstraint(
            "tipo IN ('consulta', 'queja', 'solicitud', 'incidencia')",
            name="ck_asistencia_tipo"
        ),
    )

    id: Mapped[int] = mapped_column(primary_key=True)

    asunto: Mapped[str] = mapped_column(
        String(150),
        nullable=False
    )

    descripcion: Mapped[str] = mapped_column(
        Text,
        nullable=False
    )

    tipo: Mapped[str] = mapped_column(
        String(30),
        default="consulta",
        nullable=False
    )

    estado: Mapped[str] = mapped_column(
        String(30),
        default="abierta",
        nullable=False
    )

    respuesta: Mapped[str | None] = mapped_column(
        Text,
        nullable=True
    )

    fecha_creacion: Mapped[datetime] = mapped_column(
        DateTime,
        default=datetime.utcnow
    )

    fecha_cierre: Mapped[datetime | None] = mapped_column(
        DateTime,
        nullable=True
    )

    usuario_id: Mapped[int] = mapped_column(
        ForeignKey("usuarios.id"),
        nullable=False
    )

    reserva_id: Mapped[int | None] = mapped_column(
        ForeignKey("reservas.id"),
        nullable=True
    )

    usuario: Mapped["Usuario"] = relationship(
        back_populates="solicitudes_asistencia"
    )

    reserva: Mapped["Reserva"] = relationship(
        back_populates="solicitudes_asistencia"
    )
