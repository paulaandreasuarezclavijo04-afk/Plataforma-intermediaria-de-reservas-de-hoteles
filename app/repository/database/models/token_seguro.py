
from datetime import datetime

from sqlalchemy import Boolean, CheckConstraint, DateTime, ForeignKey, String
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.repository.database.base import Base


class TokenSeguro(Base):
    """
    Tokens de un solo uso para validación de correo (HU-002)
    y recuperación de contraseña (HU-005).
    """

    __tablename__ = "tokens_seguros"

    __table_args__ = (
        CheckConstraint(
            "tipo IN ('verificacion', 'recuperacion')",
            name="ck_token_tipo"
        ),
    )

    id: Mapped[int] = mapped_column(primary_key=True)

    token: Mapped[str] = mapped_column(
        String(64),
        unique=True,
        index=True,
        nullable=False
    )

    tipo: Mapped[str] = mapped_column(
        String(30),
        nullable=False
    )

    expira: Mapped[datetime] = mapped_column(
        DateTime,
        nullable=False
    )

    usado: Mapped[bool] = mapped_column(
        Boolean,
        default=False,
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

    usuario: Mapped["Usuario"] = relationship(
        back_populates="tokens"
    )
