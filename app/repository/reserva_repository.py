# ─────────────────────────────────────────────────────────────
# REPOSITORIO DE RESERVAS — HU-036 / HU-039
# ─────────────────────────────────────────────────────────────

from sqlalchemy import select
from sqlalchemy.orm import Session, selectinload

from app.repository.base_repository import BaseRepository
from app.repository.database.models import (
    Habitacion,
    Hotel,
    Notificacion,
    Reserva,
    Usuario
)


class ReservaRepository(BaseRepository[Reserva]):

    def __init__(self, session: Session):
        super().__init__(session, Reserva)

    def list_filtrado(
        self,
        usuario_id: int | None = None,
        hotel_id: int | None = None,
        estado: str | None = None,
        limit: int = 100,
        offset: int = 0
    ) -> list[Reserva]:
        stmt = select(Reserva).options(
            selectinload(Reserva.pagos),
            selectinload(Reserva.habitacion).selectinload(Habitacion.hotel)
        )

        if usuario_id:
            stmt = stmt.where(Reserva.usuario_id == usuario_id)
        if hotel_id:
            stmt = stmt.join(Habitacion).where(Habitacion.hotel_id == hotel_id)
        if estado:
            stmt = stmt.where(Reserva.estado == estado)

        stmt = stmt.order_by(Reserva.fecha_creacion.desc())
        stmt = stmt.limit(limit).offset(offset)
        return list(self.session.scalars(stmt).all())

    def get_detalle(self, reserva_id: int) -> Reserva | None:
        stmt = (
            select(Reserva)
            .where(Reserva.id == reserva_id)
            .options(
                selectinload(Reserva.pagos),
                selectinload(Reserva.usuario),
                selectinload(Reserva.habitacion).selectinload(Habitacion.hotel),
                selectinload(Reserva.notificaciones)
            )
        )
        return self.session.scalars(stmt).first()

    def get_notificacion(
        self,
        reserva_id: int,
        tipo: str
    ) -> Notificacion | None:
        stmt = (
            select(Notificacion)
            .where(
                Notificacion.reserva_id == reserva_id,
                Notificacion.tipo == tipo
            )
            .order_by(Notificacion.fecha_creacion.desc())
        )
        return self.session.scalars(stmt).first()

    def list_by_habitacion(
        self,
        habitacion_id: int,
        limit: int = 100
    ) -> list[Reserva]:
        stmt = (
            select(Reserva)
            .where(Reserva.habitacion_id == habitacion_id)
            .order_by(Reserva.fecha_creacion.desc())
            .limit(limit)
        )
        return list(self.session.scalars(stmt).all())

    def get_hotel(self, hotel_id: int) -> Hotel | None:
        return self.session.get(Hotel, hotel_id)

    def get_usuario(self, usuario_id: int) -> Usuario | None:
        return self.session.get(Usuario, usuario_id)
