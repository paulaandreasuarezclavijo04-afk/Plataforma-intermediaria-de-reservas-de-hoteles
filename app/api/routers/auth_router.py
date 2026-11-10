# ─────────────────────────────────────────────────────────────
# ROUTER DE AUTH — HU-011 (iniciar sesión), HU-002 (validar
# correo) y HU-005 (recuperar contraseña)
# ─────────────────────────────────────────────────────────────

from fastapi import APIRouter, Depends, status
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
    summary="HU-001/HU-002: registrar usuario y enviar verificación"
)
def registro(data: RegistroRequest, db: Session = Depends(get_db)):
    usuario, token = AuthService(db).registrar(data)
    return MensajeResponse(
        mensaje="Usuario registrado correctamente",
        detalle=(
            f"Correo de verificación simulado. Token: {token}"
        )
    )


@router.post(
    "/login",
    response_model=LoginResponse,
    summary="HU-011: iniciar sesión"
)
def login(data: LoginRequest, db: Session = Depends(get_db)):
    usuario = AuthService(db).login(data)
    rol = usuario.rol.nombre if usuario.rol else ""
    return LoginResponse(
        mensaje="Inicio de sesión exitoso (token JWT pendiente en v2)",
        usuario=UsuarioSesion(
            id=usuario.id,
            nombres=usuario.nombres,
            apellidos=usuario.apellidos,
            correo=usuario.correo,
            rol=rol,
            correo_verificado=usuario.correo_verificado
        )
    )


@router.post(
    "/solicitar-verificacion",
    response_model=MensajeResponse,
    summary="HU-002: enviar token de verificación de correo"
)
def solicitar_verificacion(data: CorreoRequest, db: Session = Depends(get_db)):
    token = AuthService(db).solicitar_verificacion(data.correo)
    return MensajeResponse(
        mensaje="Si el correo existe, se envió la verificación",
        detalle=f"Token simulado: {token}" if token else None
    )


@router.post(
    "/validar-correo",
    response_model=MensajeResponse,
    summary="HU-002: confirmar correo con el token"
)
def validar_correo(data: ValidarCorreoRequest, db: Session = Depends(get_db)):
    usuario = AuthService(db).validar_correo(data.token)
    return MensajeResponse(
        mensaje=f"Correo verificado para {usuario.correo}"
    )


@router.post(
    "/recuperar-password",
    response_model=MensajeResponse,
    summary="HU-005: solicitar recuperación de contraseña"
)
def recuperar_password(data: CorreoRequest, db: Session = Depends(get_db)):
    token = AuthService(db).solicitar_recuperacion(data.correo)
    return MensajeResponse(
        mensaje="Si el correo existe, se envió la recuperación",
        detalle=f"Token simulado: {token}" if token else None
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
    usuario = AuthService(db).restablecer_password(data)
    return MensajeResponse(
        mensaje=f"Contraseña actualizada para {usuario.correo}"
    )
