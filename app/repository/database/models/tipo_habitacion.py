
from sqlalchemy import String, Text
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.repository.database.base import Base


class TipoHabitacion(Base):
    __tablename__ = "tipos_habitacion"

    id: Mapped[int] = mapped_column(primary_key=True)

    nombre: Mapped[str] = mapped_column(
        String(80),
        unique=True,
        nullable=False
    )

    descripcion: Mapped[str | None] = mapped_column(
        Text,
        nullable=True
    )

    habitaciones: Mapped[list["Habitacion"]] = relationship(
        back_populates="tipo"
    )
