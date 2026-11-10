
from datetime import datetime

from sqlalchemy import CheckConstraint, DateTime, ForeignKey, String, Text
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.repository.database.base import Base


class Notificacion(Base):
    """
    Correos/confirmaciones simulados (HU-068, HU-002, HU-005).
    No se envían correos reales: cada mensaje queda registrado aquí.
    """

    __tablename__ = "notificaciones"

    __table_args__ = (
        CheckConstraint(
            "estado IN ('pendiente', 'enviada')",
            name="ck_notificacion_estado"
        ),
    )

    id: Mapped[int] = mapped_column(primary_key=True)

    tipo: Mapped[str] = mapped_column(
        String(50),
        nullable=False
    )

    asunto: Mapped[str] = mapped_column(
        String(200),
        nullable=False
    )

    contenido: Mapped[str] = mapped_column(
        Text,
        nullable=False
    )

    estado: Mapped[str] = mapped_column(
        String(30),
        default="enviada",
        nullable=False
    )

    fecha_creacion: Mapped[datetime] = mapped_column(
        DateTime,
        default=datetime.utcnow
    )

    fecha_envio: Mapped[datetime | None] = mapped_column(
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
        back_populates="notificaciones"
    )

    reserva: Mapped["Reserva"] = relationship(
        back_populates="notificaciones"
    )
