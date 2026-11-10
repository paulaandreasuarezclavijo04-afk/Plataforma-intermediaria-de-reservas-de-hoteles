# ─────────────────────────────────────────────────────────────
# ROUTER DE RESERVAS — HU-036 (crear), HU-039 (consultar)
# y HU-068 (confirmación de reserva)
# ─────────────────────────────────────────────────────────────

from fastapi import APIRouter, Depends, Query, status
from sqlalchemy.orm import Session

from app.api.schemas.reserva_schema import (
    CancelarReservaRequest,
    ConfirmacionResponse,
    ReservaCreate,
    ReservaDetalle,
    ReservaResponse
)
from app.repository.database.session import get_db
from app.services.reserva_service import ReservaService

router = APIRouter(prefix="/api/reservas", tags=["Reservas"])


@router.get(
    "",
    response_model=list[ReservaDetalle],
    summary="HU-039: listar reservas (por usuario, hotel o estado)"
)
def listar(
    usuario_id: int | None = Query(None),
    hotel_id: int | None = Query(None),
    estado: str | None = Query(
        None,
        description="pendiente | confirmada | completada | cancelada"
    ),
    db: Session = Depends(get_db)
):
    return ReservaService(db).listar(
        usuario_id=usuario_id,
        hotel_id=hotel_id,
        estado=estado
    )


@router.post(
    "",
    response_model=ReservaResponse,
    status_code=status.HTTP_201_CREATED,
    summary="HU-036: crear reserva (con control de disponibilidad)"
)
def crear(data: ReservaCreate, db: Session = Depends(get_db)):
    return ReservaService(db).crear(data)


@router.get(
    "/{reserva_id}",
    response_model=ReservaDetalle,
    summary="HU-039: consultar reserva con sus pagos"
)
def obtener(reserva_id: int, db: Session = Depends(get_db)):
    servicio = ReservaService(db)
    reserva = servicio.obtener(reserva_id)
    notificacion = servicio.obtener_confirmacion(reserva_id)

    detalle = ReservaDetalle.model_validate(reserva)
    if notificacion:
        detalle.confirmacion = {
            "asunto": notificacion.asunto,
            "contenido": notificacion.contenido,
            "fecha": notificacion.fecha_envio.isoformat()
            if notificacion.fecha_envio else None,
        }
    return detalle


@router.post(
    "/{reserva_id}/confirmar",
    response_model=ReservaResponse,
    summary="HU-068: confirmar reserva y generar la notificación"
)
def confirmar(reserva_id: int, db: Session = Depends(get_db)):
    reserva, _ = ReservaService(db).confirmar(reserva_id)
    return reserva


@router.get(
    "/{reserva_id}/confirmacion",
    response_model=ConfirmacionResponse,
    summary="HU-068: consultar la confirmación enviada"
)
def obtener_confirmacion(reserva_id: int, db: Session = Depends(get_db)):
    servicio = ReservaService(db)
    reserva = servicio.obtener(reserva_id)
    notificacion = servicio.obtener_confirmacion(reserva_id)
    return ConfirmacionResponse(
        reserva_id=reserva.id,
        estado=reserva.estado,
        notificacion_id=notificacion.id if notificacion else None,
        asunto=notificacion.asunto if notificacion else None,
        contenido=notificacion.contenido if notificacion else None,
        fecha=notificacion.fecha_envio if notificacion else None
    )


@router.post(
    "/{reserva_id}/cancelar",
    response_model=ReservaResponse,
    summary="Cancelar reserva (con reembolso automático)"
)
def cancelar(
    reserva_id: int,
    data: CancelarReservaRequest | None = None,
    db: Session = Depends(get_db)
):
    motivo = data.motivo if data else None
    return ReservaService(db).cancelar(reserva_id, motivo)


@router.post(
    "/{reserva_id}/completar",
    response_model=ReservaResponse,
    summary="Marcar estancia completada (habilita evaluar)"
)
def completar(reserva_id: int, db: Session = Depends(get_db)):
    return ReservaService(db).completar(reserva_id)
