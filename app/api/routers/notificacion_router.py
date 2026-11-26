# ─────────────────────────────────────────────────────────────
# ROUTER DE NOTIFICACIONES — HU-068
# ─────────────────────────────────────────────────────────────

from fastapi import APIRouter, Depends, status
from sqlalchemy.orm import Session

from app.api.schemas.notificacion_schema import (
    ApiResponse,
    ConfirmacionReservaData,
    ConfirmacionReservaRequest,
)
from app.repository.database.session import get_db
from app.services.notificacion_service import NotificacionService

router = APIRouter(prefix="/api/v1/notificaciones", tags=["Notificaciones"])


@router.post(
    "/confirmaciones-reserva",
    response_model=ApiResponse[ConfirmacionReservaData],
    status_code=status.HTTP_201_CREATED,
    summary="HU-068: encolar/enviar confirmación de reserva",
)
def encolar_confirmacion_reserva(
    data: ConfirmacionReservaRequest,
    db: Session = Depends(get_db),
):
    notificacion = NotificacionService(db).encolar_confirmacion_reserva(
        reserva_id=data.reserva_id,
        canal=data.canal,
    )
    enviada = notificacion.estado == "ENVIADA"
    pendiente = notificacion.estado == "PENDIENTE_ENVIO"
    mensaje = (
        "Notificación de confirmación enviada"
        if enviada
        else "Notificación de confirmación encolada"
        if pendiente
        else "No se pudo enviar la notificación de confirmación"
    )
    return ApiResponse(
        mensaje=mensaje,
        data=ConfirmacionReservaData(
            reserva_id=notificacion.reserva_id,
            canal=notificacion.canal,
            estado=notificacion.estado,
            notificacion_id=notificacion.id,
            fecha=notificacion.fecha_envio or notificacion.fecha_creacion,
            resultado=notificacion.resultado,
        ),
        success=enviada or pendiente,
    )