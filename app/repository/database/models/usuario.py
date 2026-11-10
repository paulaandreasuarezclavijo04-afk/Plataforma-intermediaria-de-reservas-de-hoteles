
from datetime import datetime

from sqlalchemy import String, Boolean, DateTime, ForeignKey
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.repository.database.base import Base


class Usuario(Base):
    __tablename__ = "usuarios"

    id: Mapped[int] = mapped_column(primary_key=True)

    nombres: Mapped[str] = mapped_column(
        String(100),
        nullable=False
    )

    apellidos: Mapped[str] = mapped_column(
        String(100),
        nullable=False
    )

    correo: Mapped[str] = mapped_column(
        String(150),
        unique=True,
        index=True,
        nullable=False
    )

    telefono: Mapped[str | None] = mapped_column(
        String(30),
        nullable=True
    )

    password_hash: Mapped[str] = mapped_column(
        String(255),
        nullable=False
    )

    correo_verificado: Mapped[bool] = mapped_column(
        Boolean,
        default=False,
        nullable=False
    )

    activo: Mapped[bool] = mapped_column(
        Boolean,
        default=True,
        nullable=False
    )

    rol_id: Mapped[int] = mapped_column(
        ForeignKey("roles.id"),
        nullable=False
    )

    fecha_creacion: Mapped[datetime] = mapped_column(
        DateTime,
        default=datetime.utcnow
    )

    rol: Mapped["Rol"] = relationship(
        back_populates="usuarios"
    )

    hoteles: Mapped[list["Hotel"]] = relationship(
        back_populates="propietario"
    )

    reservas: Mapped[list["Reserva"]] = relationship(
        back_populates="usuario"
    )

    evaluaciones: Mapped[list["Evaluacion"]] = relationship(
        back_populates="usuario"
    )

    solicitudes_asistencia: Mapped[list["SolicitudAsistencia"]] = relationship(
        back_populates="usuario"
    )

    notificaciones: Mapped[list["Notificacion"]] = relationship(
        back_populates="usuario"
    )

    tokens: Mapped[list["TokenSeguro"]] = relationship(
        back_populates="usuario"
    )

    @property
    def rol_nombre(self) -> str | None:
        """Nombre del rol (para las respuestas)."""
        if self.rol:
            return self.rol.nombre
        return None
