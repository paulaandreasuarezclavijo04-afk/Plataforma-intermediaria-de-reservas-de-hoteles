# ─────────────────────────────────────────────────────────────
# REPOSITORIO DE HABITACIONES Y TARIFAS — HU-021
# Incluye las consultas de disponibilidad — HU-031 / HU-033
# ─────────────────────────────────────────────────────────────

from datetime import date
from decimal import Decimal

from sqlalchemy import exists, select
from sqlalchemy.orm import Session

from app.domain.disponibilidad import ESTADOS_QUE_OCUPAN
from app.repository.base_repository import BaseRepository
from app.repository.database.models import (
    Habitacion,
    Hotel,
    Reserva,
    Tarifa,
    TipoHabitacion
)


class HabitacionRepository(BaseRepository[Habitacion]):

    def __init__(self, session: Session):
        super().__init__(session, Habitacion)

    def list_by_hotel(
        self,
        hotel_id: int,
        incluir_todos: bool = False,
        limit: int = 200
    ) -> list[Habitacion]:
        stmt = select(Habitacion).where(Habitacion.hotel_id == hotel_id)

        if not incluir_todos:
            stmt = stmt.where(Habitacion.estado != "mantenimiento")

        stmt = stmt.order_by(Habitacion.numero).limit(limit)
        return list(self.session.scalars(stmt).all())

    def get_by_hotel_y_numero(
        self,
        hotel_id: int,
        numero: str
    ) -> Habitacion | None:
        stmt = select(Habitacion).where(
            Habitacion.hotel_id == hotel_id,
            Habitacion.numero == numero
        )
        return self.session.scalars(stmt).first()

    # ── Disponibilidad (HU-033) ─────────────────────────────
    def reservas_solapadas(
        self,
        habitacion_id: int,
        entrada: date,
        salida: date
    ) -> list[tuple[date, date]]:
        """Reservas que OCUPAN la habitación en el rango consultado."""
        stmt = select(
            Reserva.fecha_entrada,
            Reserva.fecha_salida
        ).where(
            Reserva.habitacion_id == habitacion_id,
            Reserva.estado.in_(ESTADOS_QUE_OCUPAN),
            Reserva.fecha_entrada < salida,
            Reserva.fecha_salida > entrada
        )
        return [(f[0], f[1]) for f in self.session.execute(stmt).all()]

    def listar_tarifas(self, habitacion_id: int) -> list[Tarifa]:
        stmt = (
            select(Tarifa)
            .where(Tarifa.habitacion_id == habitacion_id)
            .order_by(Tarifa.fecha_inicio)
        )
        return list(self.session.scalars(stmt).all())

    # ── Búsqueda de alojamiento (HU-031) ────────────────────
    def buscar_disponibles(
        self,
        entrada: date,
        salida: date,
        huespedes: int,
        ciudad: str | None = None,
        precio_max: Decimal | None = None,
        tipo: str | None = None,
        limit: int = 200
    ) -> list[Habitacion]:
        conflicto = exists().where(
            Reserva.habitacion_id == Habitacion.id,
            Reserva.estado.in_(ESTADOS_QUE_OCUPAN),
            Reserva.fecha_entrada < salida,
            Reserva.fecha_salida > entrada
        )

        stmt = (
            select(Habitacion)
            .join(Habitacion.hotel)
            .join(Habitacion.tipo)
            .where(
                Habitacion.capacidad >= huespedes,
                Habitacion.estado == "disponible",
                Hotel.activo == True,
                ~conflicto
            )
        )

        if precio_max is not None:
            stmt = stmt.where(Habitacion.precio_base <= precio_max)
        if ciudad:
            stmt = stmt.where(Hotel.ciudad.ilike(f"%{ciudad}%"))
        if tipo:
            stmt = stmt.where(TipoHabitacion.nombre.ilike(f"%{tipo}%"))

        stmt = stmt.order_by(Habitacion.precio_base).limit(limit)
        return list(self.session.scalars(stmt).all())

    # ── Tipos de habitación ─────────────────────────────────
    def list_tipos(self) -> list[TipoHabitacion]:
        stmt = select(TipoHabitacion).order_by(TipoHabitacion.nombre)
        return list(self.session.scalars(stmt).all())

    def get_tipo(self, tipo_id: int) -> TipoHabitacion | None:
        return self.session.get(TipoHabitacion, tipo_id)

    def add_tipo(self, tipo: TipoHabitacion) -> TipoHabitacion:
        self.session.add(tipo)
        return tipo
