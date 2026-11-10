
from sqlalchemy import String, Text, Boolean, ForeignKey
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.repository.database.base import Base


class Hotel(Base):
    __tablename__ = "hoteles"

    id: Mapped[int] = mapped_column(primary_key=True)

    nombre: Mapped[str] = mapped_column(
        String(150),
        nullable=False
    )

    descripcion: Mapped[str | None] = mapped_column(
        Text,
        nullable=True
    )

    direccion: Mapped[str] = mapped_column(
        String(200),
        nullable=False
    )

    ciudad: Mapped[str] = mapped_column(
        String(100),
        nullable=False
    )

    pais: Mapped[str] = mapped_column(
        String(100),
        nullable=False
    )

    telefono: Mapped[str | None] = mapped_column(
        String(30),
        nullable=True
    )

    activo: Mapped[bool] = mapped_column(
        Boolean,
        default=True,
        nullable=False
    )

    propietario_id: Mapped[int] = mapped_column(
        ForeignKey("usuarios.id"),
        nullable=False
    )

    propietario: Mapped["Usuario"] = relationship(
        back_populates="hoteles"
    )

    habitaciones: Mapped[list["Habitacion"]] = relationship(
        back_populates="hotel"
    )

    evaluaciones: Mapped[list["Evaluacion"]] = relationship(
        back_populates="hotel"
    )

    @property
    def propietario_nombre(self) -> str | None:
        """Nombre completo del propietario (para las respuestas)."""
        if self.propietario:
            return f"{self.propietario.nombres} {self.propietario.apellidos}"
        return None
