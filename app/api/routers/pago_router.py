# ─────────────────────────────────────────────────────────────
# ROUTER DE PAGOS — HU-062 (enviar solicitud de pago)
# y HU-052 (procesar pago con pasarela simulada)
# ─────────────────────────────────────────────────────────────

from fastapi import APIRouter, Depends, Query, status
from sqlalchemy.orm import Session

from app.api.schemas.pago_schema import (
    ApiResponse,
    IniciarPagoRequest,
    PagoDetalleData,
    PagoIniciadoData,
    PagoResponse,
    ProcesarPagoRequest,
    ReembolsoRequest,
    SolicitudPagoCreate,
)
from app.dependencies.auth import get_current_user
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


# ── HU-052 v1 ───────────────────────────────────────────────
v1_router = APIRouter(prefix="/api/v1", tags=["Pagos"])


@v1_router.post(
    "/reservas/{reserva_id}/pagos",
    response_model=ApiResponse[PagoIniciadoData],
    status_code=status.HTTP_201_CREATED,
    summary="HU-052: iniciar pago de reserva",
)
def iniciar_pago(
    reserva_id: int,
    data: IniciarPagoRequest,
    db: Session = Depends(get_db),
    current_user=Depends(get_current_user),
):
    pago = PagoService(db).iniciar_pago(
        reserva_id=reserva_id,
        metodo_pago=data.metodo_pago,
        idempotency_key=data.idempotency_key,
        usuario_actual=current_user,
    )
    rechazado = pago.estado == "RECHAZADO"
    return ApiResponse(
        mensaje="Pago rechazado por el proveedor" if rechazado else "Solicitud de pago iniciada",
        data=PagoIniciadoData(
            pago_id=pago.id,
            reserva_id=pago.reserva_id,
            estado=pago.estado,
            url_proveedor=pago.url_proveedor,
            referencia_externa=pago.referencia_externa,
            monto=pago.monto,
            moneda=pago.moneda,
        ),
        success=not rechazado,
    )


@v1_router.get(
    "/pagos/{pago_id}",
    response_model=ApiResponse[PagoDetalleData],
    summary="HU-052: consultar estado de pago",
)
def obtener_pago_v1(
    pago_id: int,
    db: Session = Depends(get_db),
    current_user=Depends(get_current_user),
):
    servicio = PagoService(db)
    pago = servicio.obtener(pago_id)
    reserva = servicio._reserva(pago.reserva_id)
    if reserva.usuario_id != current_user.id and getattr(getattr(current_user, "rol", None), "nombre", "") != "admin":
        from fastapi import HTTPException
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="No tienes permisos para consultar este pago")
    return ApiResponse(
        mensaje="Pago consultado correctamente",
        data=PagoDetalleData(
            pago_id=pago.id,
            reserva_id=pago.reserva_id,
            estado=pago.estado,
            metodo=pago.metodo,
            monto=pago.monto,
            moneda=pago.moneda,
            referencia_externa=pago.referencia_externa,
            url_proveedor=pago.url_proveedor,
            fecha_creacion=pago.fecha_creacion,
            fecha_pago=pago.fecha_pago,
        ),
        success=True,
    )
