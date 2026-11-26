# ─────────────────────────────────────────────────────────────
# SERVICIO DE RESERVAS — HU-036 (crear), HU-039 (consultar)
# y HU-068 (confirmación de reserva)
#
# REGLA DE NEGOCIO CLAVE: impedir que dos usuarios reserven la
# misma habitación en las mismas fechas (verificación + alta en
# la misma transacción, con lock para el servidor en un proceso).
# ─────────────────────────────────────────────────────────────

import threading
from datetime import date, datetime

from fastapi import HTTPException, status
from sqlalchemy.orm import Session

from app.api.schemas.reserva_schema import ReservaCreate
from app.domain.disponibilidad import (
    ESTADOS_QUE_OCUPAN,
    calcular_total,
    hay_conflicto,
    noches
)
from app.repository.database.models import Notificacion, Reserva
from app.repository.habitacion_repository import HabitacionRepository
from app.repository.hotel_repository import HotelRepository
from app.repository.notificacion_repository import NotificacionRepository
from app.repository.reserva_repository import ReservaRepository
from app.repository.usuario_repository import UsuarioRepository

# Lock para la sección crítica de creación de reservas
_lock_creacion = threading.Lock()

ESTADOS_CANCELABLES = ("pendiente", "confirmada")
ESTADOS_COMPLETADOS = ("confirmada", "pagada", "completada")


class ReservaService:

    def __init__(self, db: Session):
        self.db = db
        self.repo = ReservaRepository(db)
        self.habitaciones = HabitacionRepository(db)
        self.hoteles = HotelRepository(db)
        self.usuarios = UsuarioRepository(db)
        self.notificaciones = NotificacionRepository(db)

    # ── HU-036: crear reserva ───────────────────────────────
    def crear(self, data: ReservaCreate) -> Reserva:
        hoy = date.today()

        if data.fecha_entrada < hoy:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="La fecha de entrada no puede ser en el pasado"
            )

        usuario = self.usuarios.get_by_id(data.usuario_id)
        if not usuario or not usuario.activo:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Usuario no encontrado o inactivo"
            )

        habitacion = self.habitaciones.get_by_id(data.habitacion_id)
        if not habitacion:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Habitación no encontrada"
            )

        hotel = self.hoteles.get_by_id(habitacion.hotel_id)
        if not hotel or not hotel.activo:
            raise HTTPException(
                status_code=status.HTTP_409_CONFLICT,
                detail="El hotel no acepta reservas"
            )

        if habitacion.estado == "mantenimiento":
            raise HTTPException(
                status_code=status.HTTP_409_CONFLICT,
                detail="La habitación está en mantenimiento"
            )

        if data.huespedes > habitacion.capacidad:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=(
                    f"La capacidad máxima es {habitacion.capacidad} huéspedes"
                )
            )

        # ── Sección crítica: verificar y crear en la misma transacción
        with _lock_creacion:
            existentes = self.habitaciones.reservas_solapadas(
                habitacion.id, data.fecha_entrada, data.fecha_salida
            )
            if hay_conflicto(data.fecha_entrada, data.fecha_salida, existentes):
                raise HTTPException(
                    status_code=status.HTTP_409_CONFLICT,
                    detail="La habitación no está disponible en esas fechas"
                )

            tarifas = self.habitaciones.listar_tarifas(habitacion.id)
            total, _ = calcular_total(
                habitacion.precio_base,
                tarifas,
                data.fecha_entrada,
                data.fecha_salida
            )

            reserva = Reserva(
                fecha_entrada=data.fecha_entrada,
                fecha_salida=data.fecha_salida,
                huespedes=data.huespedes,
                total=total,
                estado="pendiente",
                usuario_id=usuario.id,
                habitacion_id=habitacion.id
            )
            self.repo.add(reserva)
            self.repo.flush()

            self.notificaciones.crear(
                usuario_id=usuario.id,
                tipo="reserva_creada",
                asunto=f"Reserva #{reserva.id} registrada",
                contenido=(
                    f"Tu reserva en {hotel.nombre} del "
                    f"{data.fecha_entrada:%d/%m/%Y} al {data.fecha_salida:%d/%m/%Y} "
                    f"por {noches(data.fecha_entrada, data.fecha_salida)} noches "
                    f"quedó registrada con estado 'pendiente'. Total: {total} COP."
                ),
                reserva_id=reserva.id
            )

            self.repo.commit()
            self.repo.flush()

        return reserva

    # ── HU-039: consultar reservas ──────────────────────────
    def listar(
        self,
        usuario_id: int | None = None,
        hotel_id: int | None = None,
        estado: str | None = None
    ) -> list[Reserva]:
        return self.repo.list_filtrado(
            usuario_id=usuario_id,
            hotel_id=hotel_id,
            estado=estado
        )

    def obtener(self, reserva_id: int) -> Reserva:
        reserva = self.repo.get_detalle(reserva_id)
        if not reserva:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Reserva no encontrada"
            )
        return reserva

    # ── HU-068: confirmación de reserva ─────────────────────
    def confirmar(self, reserva_id: int) -> tuple[Reserva, Notificacion | None]:
        reserva = self.obtener(reserva_id)

        if reserva.estado not in ("pendiente", "confirmada"):
            raise HTTPException(
                status_code=status.HTTP_409_CONFLICT,
                detail=f"No se puede confirmar una reserva '{reserva.estado}'"
            )

        reserva.estado = "confirmada"
        notificacion = self._generar_confirmacion(reserva)
        self.repo.commit()
        self.repo.flush()
        return reserva, notificacion

    def obtener_confirmacion(self, reserva_id: int) -> Notificacion | None:
        self.obtener(reserva_id)
        return self.repo.get_notificacion(reserva_id, "confirmacion_reserva")

    # ── Cancelar reserva (con reembolso automático) ─────────
    def cancelar(self, reserva_id: int, motivo: str | None = None) -> Reserva:
        reserva = self.obtener(reserva_id)

        if reserva.estado == "cancelada":
            raise HTTPException(
                status_code=status.HTTP_409_CONFLICT,
                detail="La reserva ya está cancelada"
            )
        if reserva.estado == "completada":
            raise HTTPException(
                status_code=status.HTTP_409_CONFLICT,
                detail="No se puede cancelar una reserva completada"
            )

        reserva.estado = "cancelada"

        # Reembolso automático de pagos ya realizados
        for pago in reserva.pagos:
            if pago.estado == "pagado":
                pago.estado = "reembolsado"
                pago.fecha_pago = datetime.utcnow()

        contenido = f"La reserva #{reserva.id} fue cancelada."
        if motivo:
            contenido += f" Motivo: {motivo}"

        self.notificaciones.crear(
            usuario_id=reserva.usuario_id,
            tipo="reserva_cancelada",
            asunto=f"Reserva #{reserva.id} cancelada",
            contenido=contenido,
            reserva_id=reserva.id
        )

        self.repo.commit()
        self.repo.flush()
        return reserva

    # ── Completar estancia (permite evaluar después) ────────
    def completar(self, reserva_id: int) -> Reserva:
        reserva = self.obtener(reserva_id)

        if reserva.estado in ("cancelada", "completada"):
            raise HTTPException(
                status_code=status.HTTP_409_CONFLICT,
                detail=f"No se puede completar una reserva '{reserva.estado}'"
            )
        if reserva.fecha_salida > date.today():
            raise HTTPException(
                status_code=status.HTTP_409_CONFLICT,
                detail="La reserva aún no puede completarse: falta la fecha de salida"
            )

        reserva.estado = "completada"
        self.repo.commit()
        self.repo.flush()
        return reserva

    # ── Auxiliares ──────────────────────────────────────────
    def _generar_confirmacion(self, reserva: Reserva) -> Notificacion:
        habitacion = self.habitaciones.get_by_id(reserva.habitacion_id)
        hotel = self.hoteles.get_by_id(habitacion.hotel_id) if habitacion else None
        nombre_hotel = hotel.nombre if hotel else "el hotel"

        contenido = (
            f"Confirmamos tu reserva #{reserva.id} en {nombre_hotel}: "
            f"entrada {reserva.fecha_entrada:%d/%m/%Y}, "
            f"salida {reserva.fecha_salida:%d/%m/%Y}, "
            f"{reserva.huespedes} huésped(es), total {reserva.total} COP."
        )

        return self.notificaciones.crear(
            usuario_id=reserva.usuario_id,
            tipo="confirmacion_reserva",
            asunto=f"Reserva #{reserva.id} confirmada",
            contenido=contenido,
            reserva_id=reserva.id
        )
