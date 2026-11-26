# ─────────────────────────────────────────────────────────────
# SERVICIO DE NOTIFICACIONES — HU-068
# ─────────────────────────────────────────────────────────────

from datetime import datetime

from fastapi import HTTPException, status
from sqlalchemy.orm import Session

from app.repository.database.models import Notificacion, Reserva
from app.repository.notificacion_repository import NotificacionRepository
from app.repository.reserva_repository import ReservaRepository


class NotificacionService:

    def __init__(self, db: Session):
        self.db = db
        self.repo = NotificacionRepository(db)
        self.reservas = ReservaRepository(db)

    def encolar_confirmacion_reserva(self, reserva_id: int, canal: str = "EMAIL") -> Notificacion:
        canal = (canal or "EMAIL").strip().upper()
        if canal not in {"EMAIL"}:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=f"Canal '{canal}' no soportado",
            )

        reserva = self.reservas.get_detalle(reserva_id)
        if not reserva:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Reserva no encontrada",
            )

        if reserva.estado != "confirmada":
            raise HTTPException(
                status_code=status.HTTP_409_CONFLICT,
                detail="La reserva no cumple las condiciones para enviar confirmación",
            )

        # Idempotencia: si ya existe una confirmación enviada para este evento, no duplicar
        existente = self.repo.get_by_reserva_tipo_canal(reserva_id, "confirmacion_reserva", canal)
        if existente and existente.estado == "ENVIADA":
            raise HTTPException(
                status_code=status.HTTP_409_CONFLICT,
                detail="La notificación de confirmación ya fue enviada para esta reserva",
            )

        usuario = reserva.usuario
        if not usuario or not usuario.correo:
            notificacion = self.repo.crear(
                usuario_id=reserva.usuario_id,
                tipo="confirmacion_reserva",
                asunto=self._asunto(reserva),
                contenido=self._contenido(reserva),
                reserva_id=reserva.id,
                canal=canal,
                estado="FALLIDA",
                resultado="Destino inválido: el usuario no tiene correo válido",
                intentos=1,
                fecha_envio=None,
            )
            self.db.commit()
            self.db.refresh(notificacion)
            return notificacion

        # Simulación de envío: si falla el "proveedor", queda pendiente/fallido para reintento.
        # Aquí simulamos envío exitoso; los fallos reales se registran como FALLIDA/PENDIENTE_ENVIO.
        try:
            notificacion = self.repo.crear(
                usuario_id=reserva.usuario_id,
                tipo="confirmacion_reserva",
                asunto=self._asunto(reserva),
                contenido=self._contenido(reserva),
                reserva_id=reserva.id,
                canal=canal,
                estado="ENVIADA",
                resultado="Envío simulado exitoso",
                intentos=(existente.intentos + 1) if existente else 1,
                fecha_envio=datetime.utcnow(),
            )
            self.db.commit()
            self.db.refresh(notificacion)
            return notificacion
        except Exception:
            self.db.rollback()
            # Registrar intento fallido para reintento controlado
            fallida = Notificacion(
                usuario_id=reserva.usuario_id,
                tipo="confirmacion_reserva",
                canal=canal,
                asunto=self._asunto(reserva),
                contenido=self._contenido(reserva),
                reserva_id=reserva.id,
                estado="FALLIDA",
                resultado="Error al enviar la notificación",
                intentos=(existente.intentos + 1) if existente else 1,
                fecha_envio=None,
            )
            self.db.add(fallida)
            self.db.commit()
            self.db.refresh(fallida)
            return fallida

    def _asunto(self, reserva: Reserva) -> str:
        return f"Confirmación de reserva #{reserva.id}"

    def _contenido(self, reserva: Reserva) -> str:
        hotel_nombre = "Hotel"
        if reserva.habitacion and reserva.habitacion.hotel:
            hotel_nombre = reserva.habitacion.hotel.nombre
        return (
            f"Código de reserva: {reserva.id}. "
            f"Hotel: {hotel_nombre}. "
            f"Entrada: {reserva.fecha_entrada:%Y-%m-%d}. "
            f"Salida: {reserva.fecha_salida:%Y-%m-%d}. "
            f"Huéspedes: {reserva.huespedes}. "
            f"Estado: {reserva.estado}."
        )