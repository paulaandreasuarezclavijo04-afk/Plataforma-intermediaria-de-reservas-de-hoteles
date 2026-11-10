# ─────────────────────────────────────────────────────────────
# SERVICIO DE EVALUACIONES — HU-076 (CRUD de evaluaciones)
#
# REGLAS DE NEGOCIO:
#  - Solo se evalúa una reserva que fue COMPLETADA por el huésped.
#  - Una sola evaluación por reserva.
#  - Puntuación entre 1 y 5.
# ─────────────────────────────────────────────────────────────

from datetime import datetime
from decimal import Decimal, ROUND_HALF_UP

from fastapi import HTTPException, status
from sqlalchemy.orm import Session

from app.api.schemas.evaluacion_schema import (
    EvaluacionCreate,
    EvaluacionUpdate,
    ResumenHotelEvaluaciones
)
from app.repository.database.models import Evaluacion
from app.repository.evaluacion_repository import EvaluacionRepository
from app.repository.reserva_repository import ReservaRepository


class EvaluacionService:

    def __init__(self, db: Session):
        self.db = db
        self.repo = EvaluacionRepository(db)
        self.reservas = ReservaRepository(db)

    # ── Crear ───────────────────────────────────────────────
    def crear(self, data: EvaluacionCreate) -> Evaluacion:
        reserva = self.reservas.get_detalle(data.reserva_id)
        if not reserva:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Reserva no encontrada"
            )

        if reserva.estado != "completada":
            raise HTTPException(
                status_code=status.HTTP_409_CONFLICT,
                detail=(
                    "Solo se pueden evaluar reservas COMPLETADAS "
                    f"(estado actual: {reserva.estado})"
                )
            )

        if self.repo.get_by_reserva(reserva.id):
            raise HTTPException(
                status_code=status.HTTP_409_CONFLICT,
                detail="Esta reserva ya fue evaluada"
            )

        hotel_id = reserva.habitacion.hotel_id if reserva.habitacion else None
        if not hotel_id:
            raise HTTPException(
                status_code=status.HTTP_409_CONFLICT,
                detail="La reserva no tiene hotel asociado"
            )

        evaluacion = Evaluacion(
            puntuacion=data.puntuacion,
            comentario=data.comentario.strip() if data.comentario else None,
            usuario_id=reserva.usuario_id,
            hotel_id=hotel_id,
            reserva_id=reserva.id
        )
        self.repo.add(evaluacion)
        self.repo.commit()
        self.repo.flush()
        return evaluacion

    # ── Consultar ───────────────────────────────────────────
    def listar_por_hotel(self, hotel_id: int) -> list[Evaluacion]:
        return self.repo.list_by_hotel(hotel_id)

    def listar(self, usuario_id: int | None = None) -> list[Evaluacion]:
        return self.repo.list_all(usuario_id=usuario_id)

    def obtener(self, evaluacion_id: int) -> Evaluacion:
        evaluacion = self.repo.get_by_id(evaluacion_id)
        if not evaluacion:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Evaluación no encontrada"
            )
        return evaluacion

    def resumen(self, hotel_id: int) -> ResumenHotelEvaluaciones:
        total, promedio = self.repo.promedio_by_hotel(hotel_id)
        distribucion = self.repo.distribucion_by_hotel(hotel_id)
        return ResumenHotelEvaluaciones(
            hotel_id=hotel_id,
            total_evaluaciones=total,
            promedio=Decimal(str(promedio)).quantize(
                Decimal("0.01"), rounding=ROUND_HALF_UP
            ),
            distribucion=distribucion
        )

    # ── Actualizar (solo puntuación y comentario) ───────────
    def actualizar(
        self,
        evaluacion_id: int,
        data: EvaluacionUpdate
    ) -> Evaluacion:
        evaluacion = self.obtener(evaluacion_id)
        cambios = data.model_dump(exclude_unset=True)

        if "puntuacion" in cambios and cambios["puntuacion"] is not None:
            evaluacion.puntuacion = cambios["puntuacion"]
        if "comentario" in cambios and cambios["comentario"] is not None:
            evaluacion.comentario = cambios["comentario"].strip()

        self.repo.commit()
        self.repo.flush()
        return evaluacion

    # ── Eliminar ────────────────────────────────────────────
    def eliminar(self, evaluacion_id: int) -> None:
        evaluacion = self.obtener(evaluacion_id)
        self.repo.delete(evaluacion)
        self.repo.commit()

    # ── Respuesta del hotel ─────────────────────────────────
    def responder(self, evaluacion_id: int, respuesta: str) -> Evaluacion:
        evaluacion = self.obtener(evaluacion_id)
        evaluacion.respuesta_hotel = respuesta.strip()
        evaluacion.fecha_respuesta = datetime.utcnow()
        self.repo.commit()
        self.repo.flush()
        return evaluacion
