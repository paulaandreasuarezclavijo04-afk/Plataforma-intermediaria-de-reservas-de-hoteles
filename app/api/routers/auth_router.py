# ─────────────────────────────────────────────────────────────
# ROUTER DE AUTH — HU-011 (login con JWT), HU-002, HU-005
# ─────────────────────────────────────────────────────────────

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session

from app.api.schemas.auth_schema import (
    CorreoRequest,
    LoginRequest,
    LoginResponse,
    MensajeResponse,
    RecuperarPasswordRequest,
    RegistroRequest,
    UsuarioSesion,
    ValidarCorreoRequest
)
from app.repository.database.session import get_db
from app.services.auth_service import AuthService

router = APIRouter(prefix="/api/auth", tags=["Auth"])


@router.post(
    "/registro",
    response_model=MensajeResponse,
    status_code=status.HTTP_201_CREATED,
    summary="HU-002: registrar usuario y enviar verificación"
)
def registro(data: RegistroRequest, db: Session = Depends(get_db)):
    usuario = AuthService(db).registrar(data)
    return MensajeResponse(
        mensaje="Usuario registrado correctamente",
        detalle=f"Usuario {usuario.correo} creado. Usa POST /api/auth/login para obtener tu token."
    )


@router.post(
    "/login",
    response_model=LoginResponse,
    summary="HU-011: iniciar sesión y recibir token JWT"
)
def login(data: LoginRequest, db: Session = Depends(get_db)):
    result = AuthService(db).login(data)
    return LoginResponse(
        mensaje="Login exitoso",
        usuario=result["usuario"]
    )


@router.post(
    "/solicitar-verificacion",
    response_model=MensajeResponse,
    summary="HU-002: enviar token de verificación de correo"
)
def solicitar_verificacion(data: CorreoRequest, db: Session = Depends(get_db)):
    # En esta versión simulada, solo confirmamos que el correo existe
    from app.repository.database.models import Usuario
    usuario = db.query(Usuario).filter(
        Usuario.correo == data.correo.lower()
    ).first()
    if not usuario:
        return MensajeResponse(
            mensaje="El correo no existe en la base de datos",
            detalle=None
        )
    return MensajeResponse(
        mensaje="Si el correo existe, se envió la verificación (simulado)",
        detalle="Token simulado: ver manualmente en la BD"
    )


@router.post(
    "/validar-correo",
    response_model=MensajeResponse,
    summary="HU-002: confirmar correo con el token"
)
def validar_correo(data: ValidarCorreoRequest, db: Session = Depends(get_db)):
    # Simulación: marcar correo como verificado
    from app.repository.database.models import Usuario
    usuario = db.query(Usuario).filter(
        Usuario.correo == data.correo.lower()
    ).first()
    if not usuario:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Usuario no encontrado"
        )
    usuario.correo_verificado = True
    db.commit()
    db.refresh(usuario)
    return MensajeResponse(
        mensaje=f"Correo verificado para {usuario.correo}"
    )


@router.post(
    "/recuperar-password",
    response_model=MensajeResponse,
    summary="HU-005: solicitar recuperación de contraseña"
)
def recuperar_password(data: CorreoRequest, db: Session = Depends(get_db)):
    from app.repository.database.models import Usuario
    usuario = db.query(Usuario).filter(
        Usuario.correo == data.correo.lower()
    ).first()
    if not usuario:
        return MensajeResponse(
            mensaje="El correo no existe",
            detalle=None
        )
    return MensajeResponse(
        mensaje="Se envió un enlace de recuperación (simulado)",
        detalle="Revisa tu bandeja de entrada simulada"
    )


@router.post(
    "/restablecer-password",
    response_model=MensajeResponse,
    summary="HU-005: cambiar contraseña con el token"
)
def restablecer_password(
    data: RecuperarPasswordRequest,
    db: Session = Depends(get_db)
):
    from app.repository.database.models import Usuario
    usuario = db.query(Usuario).filter(
        Usuario.correo == data.correo.lower()
    ).first()
    if not usuario:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Usuario no encontrado"
        )
    # Simulación: en un sistema real validarías el token primero
    return MensajeResponse(
        mensaje=f"Contraseña actualizada para {usuario.correo} (simulado)"
    )