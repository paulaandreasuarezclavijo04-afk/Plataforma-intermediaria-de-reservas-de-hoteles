# ─────────────────────────────────────────────────────────────
# SERVICIO DE HABITACIONES Y TARIFAS — HU-021
# ─────────────────────────────────────────────────────────────

from fastapi import HTTPException, status
from sqlalchemy.orm import Session

from app.api.schemas.habitacion_schema import (
    HabitacionCreate,
    HabitacionUpdate,
    TarifaCreate,
    TarifaUpdate,
    TipoHabitacionCreate
)
from app.repository.database.models import Habitacion, Tarifa, TipoHabitacion
from app.repository.habitacion_repository import HabitacionRepository
from app.repository.reserva_repository import ReservaRepository
from app.repository.hotel_repository import HotelRepository


class HabitacionService:

    def __init__(self, db: Session):
        self.db = db
        self.repo = HabitacionRepository(db)
        self.hoteles = HotelRepository(db)
        self.reservas = ReservaRepository(db)

    # ── Tipos de habitación ─────────────────────────────────
    def listar_tipos(self) -> list[TipoHabitacion]:
        return self.repo.list_tipos()

    def crear_tipo(self, data: TipoHabitacionCreate) -> TipoHabitacion:
        tipo = TipoHabitacion(
            nombre=data.nombre.strip().title(),
            descripcion=data.descripcion
        )
        self.repo.add_tipo(tipo)
        self.repo.commit()
        self.repo.flush()
        return tipo

    # ── Consultas ───────────────────────────────────────────
    def listar(self, hotel_id: int, incluir_todos: bool = False) -> list[Habitacion]:
        self._hotel_existe(hotel_id)
        return self.repo.list_by_hotel(hotel_id, incluir_todos=incluir_todos)

    def obtener(self, habitacion_id: int) -> Habitacion:
        habitacion = self.repo.get_by_id(habitacion_id)
        if not habitacion:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Habitación no encontrado"
            )
        return habitacion

    # ── Crear ───────────────────────────────────────────────
    def crear(self, data: HabitacionCreate) -> Habitacion:
        self._hotel_existe(data.hotel_id, solo_activos=True)

        if not self.repo.get_tipo(data.tipo_id):
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Tipo de habitación no existe"
            )

        if self.repo.get_by_hotel_y_numero(data.hotel_id, data.numero):
            raise HTTPException(
                status_code=status.HTTP_409_CONFLICT,
                detail=f"Ya existe la habitación {data.numero} en ese hotel"
            )

        habitacion = Habitacion(
            numero=data.numero,
            capacidad=data.capacidad,
            precio_base=data.precio_base,
            estado="disponible",
            hotel_id=data.hotel_id,
            tipo_id=data.tipo_id
        )
        self.repo.add(habitacion)
        self.repo.commit()
        self.repo.flush()
        return habitacion

    # ── Actualizar ──────────────────────────────────────────
    def actualizar(self, habitacion_id: int, data: HabitacionUpdate) -> Habitacion:
        habitacion = self.obtener(habitacion_id)
        cambios = data.model_dump(exclude_unset=True)

        if "numero" in cambios and cambios["numero"]:
            numero = cambios["numero"].strip()
            existente = self.repo.get_by_hotel_y_numero(
                habitacion.hotel_id, numero
            )
            if existente and existente.id != habitacion_id:
                raise HTTPException(
                    status_code=status.HTTP_409_CONFLICT,
                    detail=f"Ya existe la habitación {numero} en ese hotel"
                )
            habitacion.numero = numero

        if cambios.get("tipo_id") and not self.repo.get_tipo(cambios["tipo_id"]):
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Tipo de habitación no existe"
            )

        for campo in ("tipo_id", "capacidad", "precio_base", "estado"):
            if campo in cambios and cambios[campo] is not None:
                setattr(habitacion, campo, cambios[campo])

        self.repo.commit()
        self.repo.flush()
        return habitacion

    # ── Eliminar (solo si no tiene reservas) ────────────────
    def eliminar(self, habitacion_id: int) -> None:
        habitacion = self.obtener(habitacion_id)

        reservas = self.reservas.list_by_habitacion(habitacion_id)
        if reservas:
            raise HTTPException(
                status_code=status.HTTP_409_CONFLICT,
                detail="No se puede eliminar: la habitación tiene reservas"
            )

        self.repo.delete(habitacion)
        self.repo.commit()

    # ── Tarifas ─────────────────────────────────────────────
    def listar_tarifas(self, habitacion_id: int) -> list[Tarifa]:
        self.obtener(habitacion_id)
        return self.repo.listar_tarifas(habitacion_id)

    def crear_tarifa(self, habitacion_id: int, data: TarifaCreate) -> Tarifa:
        self.obtener(habitacion_id)
        tarifa = Tarifa(
            nombre=data.nombre.strip(),
            precio_noche=data.precio_noche,
            moneda=data.moneda.upper(),
            fecha_inicio=data.fecha_inicio,
            fecha_fin=data.fecha_fin,
            activa=data.activa,
            habitacion_id=habitacion_id
        )
        self.repo.add(tarifa)
        self.repo.commit()
        self.repo.flush()
        return tarifa

    def actualizar_tarifa(self, tarifa_id: int, data: TarifaUpdate) -> Tarifa:
        tarifa = self.db.get(Tarifa, tarifa_id)
        if not tarifa:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Tarifa no encontrada"
            )

        cambios = data.model_dump(exclude_unset=True)
        if "fecha_inicio" in cambios and "fecha_fin" in cambios:
            if cambios["fecha_fin"] <= cambios["fecha_inicio"]:
                raise HTTPException(
                    status_code=status.HTTP_400_BAD_REQUEST,
                    detail="fecha_fin debe ser posterior a fecha_inicio"
                )

        for campo, valor in cambios.items():
            if valor is not None:
                setattr(tarifa, campo, valor)

        self.repo.commit()
        self.repo.flush()
        return tarifa

    def eliminar_tarifa(self, tarifa_id: int) -> None:
        tarifa = self.db.get(Tarifa, tarifa_id)
        if not tarifa:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Tarifa no encontrada"
            )
        self.repo.delete(tarifa)
        self.repo.commit()

    # ── Auxiliares ──────────────────────────────────────────
    def _hotel_existe(self, hotel_id: int, solo_activos: bool = False) -> None:
        hotel = self.hoteles.get_by_id(hotel_id)
        if not hotel or (solo_activos and not hotel.activo):
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Hotel no encontrado"
            )
