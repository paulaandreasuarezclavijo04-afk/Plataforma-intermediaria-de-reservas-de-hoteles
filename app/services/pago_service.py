# ─────────────────────────────────────────────────────────────
# SERVICIO DE PAGOS — HU-062 (enviar solicitud de pago)
# y HU-052 (procesar pago con pasarela simulada)
# ─────────────────────────────────────────────────────────────

import uuid
from datetime import datetime

from fastapi import HTTPException, status
from sqlalchemy.orm import Session

from app.api.schemas.pago_schema import ProcesarPagoRequest, SolicitudPagoCreate
from app.repository.database.models import Pago, Reserva
from app.repository.notificacion_repository import NotificacionRepository
from app.repository.pago_repository import PagoRepository
from app.repository.reserva_repository import ReservaRepository


class PagoService:

    def __init__(self, db: Session):
        self.db = db
        self.repo = PagoRepository(db)
        self.reservas = ReservaRepository(db)

    # ── HU-062: solicitud de pago ───────────────────────────
    def solicitar(self, data: SolicitudPagoCreate) -> Pago:
        reserva = self._reserva(data.reserva_id)

        if reserva.estado in ("cancelada", "completada"):
            raise HTTPException(
                status_code=status.HTTP_409_CONFLICT,
                detail=f"No se puede pagar una reserva '{reserva.estado}'"
            )

        activo = self.repo.get_activo(reserva.id)
        if activo and activo.estado == "pagado":
            raise HTTPException(
                status_code=status.HTTP_409_CONFLICT,
                detail="La reserva ya está pagada"
            )
        if activo and activo.estado == "pendiente":
            return activo  # ya hay una solicitud en curso

        pago = Pago(
            monto=reserva.total,
            moneda="COP",
            metodo=data.metodo,
            estado="pendiente",
            referencia_externa=None,
            fecha_pago=None,
            reserva_id=reserva.id
        )
        self.repo.add(pago)
        self.repo.commit()
        self.repo.flush()
        return pago

    # ── HU-052: procesar pago ───────────────────────────────
    def procesar(
        self,
        pago_id: int,
        data: ProcesarPagoRequest
    ) -> Pago:
        pago = self._pago(pago_id)

        if pago.estado == "pagado":
            raise HTTPException(
                status_code=status.HTTP_409_CONFLICT,
                detail="El pago ya fue procesado"
            )
        if pago.estado == "reembolsado":
            raise HTTPException(
                status_code=status.HTTP_409_CONFLICT,
                detail="El pago fue reembolsado"
            )

        reserva = self._reserva(pago.reserva_id)

        if reserva.estado == "cancelada":
            raise HTTPException(
                status_code=status.HTTP_409_CONFLICT,
                detail="La reserva fue cancelada"
            )

        # ── Pasarela SIMULADA: tarjeta terminada en 0000 falla ──
        tarjeta = (data.numero_tarjeta or "").strip()
        if tarjeta.endswith("0000"):
            pago.estado = "fallido"
            self.repo.commit()
            self.repo.flush()
            raise HTTPException(
                status_code=status.HTTP_402_PAYMENT_REQUIRED,
                detail="Pago rechazado por la pasarela simulada"
            )

        pago.estado = "pagado"
        pago.referencia_externa = f"SIM-{uuid.uuid4().hex[:10].upper()}"
        pago.fecha_pago = datetime.utcnow()

        # Confirmar la reserva y enviar la confirmación (HU-068)
        reserva.estado = "confirmada"
        hotel_nombre = "el hotel"
        detalle = self.reservas.get_detalle(reserva.id)
        if detalle and detalle.habitacion:
            hotel = self.reservas.get_hotel(detalle.habitacion.hotel_id)
            if hotel:
                hotel_nombre = hotel.nombre

        self._notificar_confirmacion(reserva, hotel_nombre)

        self.repo.commit()
        self.repo.flush()
        return pago

    # ── Reembolso ───────────────────────────────────────────
    def reembolsar(self, pago_id: int, motivo: str | None = None) -> Pago:
        pago = self._pago(pago_id)

        if pago.estado == "reembolsado":
            raise HTTPException(
                status_code=status.HTTP_409_CONFLICT,
                detail="El pago ya fue reembolsado"
            )
        if pago.estado != "pagado":
            raise HTTPException(
                status_code=status.HTTP_409_CONFLICT,
                detail="Solo se pueden reembolsar pagos realizados"
            )

        reserva = self._reserva(pago.reserva_id)
        if reserva.estado != "cancelada":
            raise HTTPException(
                status_code=status.HTTP_409_CONFLICT,
                detail="Primero se debe cancelar la reserva para reembolsar"
            )

        pago.estado = "reembolsado"
        pago.fecha_pago = datetime.utcnow()

        self.repo.commit()
        self.repo.flush()
        return pago

    # ── Consultas ───────────────────────────────────────────
    def obtener(self, pago_id: int) -> Pago:
        return self._pago(pago_id)

    def listar_por_reserva(self, reserva_id: int) -> list[Pago]:
        self._reserva(reserva_id)
        return self.repo.list_by_reserva(reserva_id)

    # ── Auxiliares ──────────────────────────────────────────
    def _pago(self, pago_id: int) -> Pago:
        pago = self.repo.get_by_id(pago_id)
        if not pago:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Pago no encontrado"
            )
        return pago

    def _reserva(self, reserva_id: int) -> Reserva:
        reserva = self.reservas.get_by_id(reserva_id)
        if not reserva:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Reserva no encontrada"
            )
        return reserva

    def _notificar_confirmacion(self, reserva: Reserva, hotel_nombre: str) -> None:
        notificaciones = NotificacionRepository(self.db)
        notificaciones.crear(
            usuario_id=reserva.usuario_id,
            tipo="confirmacion_reserva",
            asunto=f"Reserva #{reserva.id} confirmada",
            contenido=(
                f"Tu pago por {reserva.total} COP fue aprobado. "
                f"Reserva #{reserva.id} en {hotel_nombre}: "
                f"entrada {reserva.fecha_entrada:%d/%m/%Y}, "
                f"salida {reserva.fecha_salida:%d/%m/%Y}, "
                f"{reserva.huespedes} huésped(es)."
            ),
            reserva_id=reserva.id
        )
