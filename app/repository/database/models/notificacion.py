
from datetime import datetime

from sqlalchemy import DateTime, ForeignKey, Integer, String, Text
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.repository.database.base import Base


class Notificacion(Base):
    """
    Notificaciones/correos simulados (HU-068, HU-002, HU-005).
    Registra canal, resultado e intentos para trazabilidad y reintentos.
    """

    __tablename__ = "notificaciones"

    id: Mapped[int] = mapped_column(primary_key=True)

    tipo: Mapped[str] = mapped_column(String(50), nullable=False)
    canal: Mapped[str] = mapped_column(String(30), default="EMAIL", nullable=False)
    asunto: Mapped[str] = mapped_column(String(200), nullable=False)
    contenido: Mapped[str] = mapped_column(Text, nullable=False)

    estado: Mapped[str] = mapped_column(String(30), default="PENDIENTE_ENVIO", nullable=False)
    resultado: Mapped[str | None] = mapped_column(Text, nullable=True)
    intentos: Mapped[int] = mapped_column(Integer, default=0, nullable=False)

    fecha_creacion: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow)
    fecha_envio: Mapped[datetime | None] = mapped_column(DateTime, nullable=True)

    usuario_id: Mapped[int] = mapped_column(ForeignKey("usuarios.id"), nullable=False)
    reserva_id: Mapped[int | None] = mapped_column(ForeignKey("reservas.id"), nullable=True)

    usuario: Mapped["Usuario"] = relationship(back_populates="notificaciones")
    reserva: Mapped["Reserva"] = relationship(back_populates="notificaciones")
