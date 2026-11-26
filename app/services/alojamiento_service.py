# ─────────────────────────────────────────────────────────────
# SERVICIO DE ALOJAMIENTO — HU-031 (buscar alojamiento)
# y HU-033 (consultar disponibilidad)
# ─────────────────────────────────────────────────────────────

from datetime import date

from fastapi import HTTPException, status
from sqlalchemy.orm import Session

from app.api.schemas.alojamiento_schema import (
    BusquedaRequest,
    DisponibilidadRequest,
    DisponibilidadResponse,
    HabitacionDisponible,
    ResultadoBusqueda
)
from app.domain.disponibilidad import (
    calcular_total,
    hay_conflicto,
    noches
)
from app.repository.habitacion_repository import HabitacionRepository
from app.repository.hotel_repository import HotelRepository


class AlojamientoService:

    def __init__(self, db: Session):
        self.db = db
        self.habitaciones = HabitacionRepository(db)
        self.hoteles = HotelRepository(db)

    # ── HU-031: buscar alojamiento ──────────────────────────
    def buscar(self, data: BusquedaRequest) -> list[ResultadoBusqueda]:
        self._validar_fechas(data.fecha_entrada, data.fecha_salida)

        habitaciones = self.habitaciones.buscar_disponibles(
            entrada=data.fecha_entrada,
            salida=data.fecha_salida,
            huespedes=data.huespedes,
            ciudad=data.ciudad,
            precio_max=data.precio_max,
            tipo=data.tipo
        )

        # Agrupar por hotel
        por_hotel: dict[int, ResultadoBusqueda] = {}
        for hab in habitaciones:
            tarifas = self.habitaciones.listar_tarifas(hab.id)
            total, _ = calcular_total(
                hab.precio_base, tarifas, data.fecha_entrada, data.fecha_salida
            )

            if hab.hotel_id not in por_hotel:
                hotel = self.hoteles.get_by_id(hab.hotel_id)
                por_hotel[hab.hotel_id] = ResultadoBusqueda(
                    hotel_id=hotel.id,
                    nombre=hotel.nombre,
                    ciudad=hotel.ciudad,
                    pais=hotel.pais,
                    direccion=hotel.direccion,
                    telefono=hotel.telefono,
                    habitaciones_disponibles=[]
                )

            por_hotel[hab.hotel_id].habitaciones_disponibles.append(
                HabitacionDisponible(
                    habitacion_id=hab.id,
                    numero=hab.numero,
                    tipo=hab.tipo.nombre if hab.tipo else "",
                    capacidad=hab.capacidad,
                    precio_base=hab.precio_base,
                    precio_total=total,
                    noches=noches(data.fecha_entrada, data.fecha_salida)
                )
            )

        return list(por_hotel.values())

    # ── HU-033: consultar disponibilidad ────────────────────
    def disponibilidad(
        self,
        habitacion_id: int,
        data: DisponibilidadRequest
    ) -> DisponibilidadResponse:
        self._validar_fechas(data.fecha_entrada, data.fecha_salida)

        habitacion = self.habitaciones.get_by_id(habitacion_id)
        if not habitacion:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Habitación no encontrada"
            )

        hotel = self.hoteles.get_by_id(habitacion.hotel_id)
        cantidad_noches = noches(data.fecha_entrada, data.fecha_salida)

        reservas = self.habitaciones.reservas_solapadas(
            habitacion_id, data.fecha_entrada, data.fecha_salida
        )
        ocupada = hay_conflicto(
            data.fecha_entrada, data.fecha_salida, reservas
        )

        motivo = None
        if not hotel.activo:
            motivo = "El hotel no está disponible"
        elif habitacion.estado == "mantenimiento":
            motivo = "Habitación en mantenimiento"
        elif ocupada:
            motivo = "Ya existe una reserva en esas fechas"

        tarifas = self.habitaciones.listar_tarifas(habitacion.id)
        total, desglose = calcular_total(
            habitacion.precio_base, tarifas, data.fecha_entrada, data.fecha_salida
        )

        return DisponibilidadResponse(
            habitacion_id=habitacion.id,
            hotel_id=hotel.id,
            hotel=hotel.nombre,
            fecha_entrada=data.fecha_entrada,
            fecha_salida=data.fecha_salida,
            noches=cantidad_noches,
            disponible=motivo is None,
            motivo=motivo,
            precio_total=total,
            desglose=desglose
        )

    # ── Auxiliares ──────────────────────────────────────────
    def _validar_fechas(self, entrada: date, salida: date) -> None:
        if salida <= entrada:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="La fecha de salida debe ser posterior a la de entrada"
            )
