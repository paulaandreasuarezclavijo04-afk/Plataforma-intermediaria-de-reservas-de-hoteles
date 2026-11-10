# ─────────────────────────────────────────────────────────────
# ROUTER DE PAGOS — HU-062 (enviar solicitud de pago)
# y HU-052 (procesar pago con pasarela simulada)
# ─────────────────────────────────────────────────────────────

from fastapi import APIRouter, Depends, Query, status
from sqlalchemy.orm import Session

from app.api.schemas.pago_schema import (
    PagoResponse,
    ProcesarPagoRequest,
    ReembolsoRequest,
    SolicitudPagoCreate
)
from app.repository.database.session import get_db
from app.services.pago_service import PagoService

router = APIRouter(prefix="/api/pagos", tags=["Pagos"])


@router.get(
    "",
    response_model=list[PagoResponse],
    summary="Listar pagos (de una reserva o todos)"
)
def listar(
    reserva_id: int | None = Query(None),
    db: Session = Depends(get_db)
):
    servicio = PagoService(db)
    if reserva_id:
        return servicio.listar_por_reserva(reserva_id)
    return servicio.repo.list()


@router.post(
    "",
    response_model=PagoResponse,
    status_code=status.HTTP_201_CREATED,
    summary="HU-062: enviar solicitud de pago"
)
def solicitar(data: SolicitudPagoCreate, db: Session = Depends(get_db)):
    return PagoService(db).solicitar(data)


@router.get(
    "/{pago_id}",
    response_model=PagoResponse,
    summary="Consultar pago"
)
def obtener(pago_id: int, db: Session = Depends(get_db)):
    return PagoService(db).obtener(pago_id)


@router.post(
    "/{pago_id}/procesar",
    response_model=PagoResponse,
    summary="HU-052: procesar pago (pasarela simulada)"
)
def procesar(
    pago_id: int,
    data: ProcesarPagoRequest | None = None,
    db: Session = Depends(get_db)
):
    datos = data or ProcesarPagoRequest()
    return PagoService(db).procesar(pago_id, datos)


@router.post(
    "/{pago_id}/reembolso",
    response_model=PagoResponse,
    summary="Reembolsar un pago de reserva cancelada"
)
def reembolsar(
    pago_id: int,
    data: ReembolsoRequest | None = None,
    db: Session = Depends(get_db)
):
    motivo = data.motivo if data else None
    return PagoService(db).reembolsar(pago_id, motivo)
