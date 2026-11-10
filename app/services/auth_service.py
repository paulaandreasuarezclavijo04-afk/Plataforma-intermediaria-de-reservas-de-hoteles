# ─────────────────────────────────────────────────────────────
# SERVICIO DE AUTENTICACIÓN — HU-011 (iniciar sesión),
# HU-002 (validar correo) y HU-005 (recuperar contraseña)
#
# NOTA: la capa de autorización (JWT + roles) quedará en una
# segunda pasada; por ahora los endpoints están abiertos.
# ─────────────────────────────────────────────────────────────

from datetime import datetime, timedelta

from fastapi import HTTPException, status
from sqlalchemy.orm import Session

from app.api.schemas.auth_schema import (
    LoginRequest,
    RecuperarPasswordRequest,
    RegistroRequest
)
from app.domain.password import hash_password, verify_password
from app.repository.database.models import Usuario
from app.repository.notificacion_repository import NotificacionRepository
from app.repository.token_repository import TokenRepository
from app.repository.usuario_repository import UsuarioRepository

TIEMPO_VIDA_TOKEN = timedelta(minutes=30)


class AuthService:

    def __init__(self, db: Session):
        self.db = db
        self.usuarios = UsuarioRepository(db)
        self.tokens = TokenRepository(db)
        self.notificaciones = NotificacionRepository(db)

    # ── HU-001 + HU-002: registro y verificación de correo ─
    def registrar(self, data: RegistroRequest) -> tuple[Usuario, str]:
        if self.usuarios.get_by_correo(data.correo):
            raise HTTPException(
                status_code=status.HTTP_409_CONFLICT,
                detail="Ya existe un usuario con ese correo"
            )

        rol = self.usuarios.get_rol(data.rol)
        if not rol:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Rol inválido: admin | propietario | huesped"
            )

        usuario = Usuario(
            nombres=data.nombres.strip().title(),
            apellidos=data.apellidos.strip().title(),
            correo=data.correo,
            telefono=data.telefono,
            password_hash=hash_password(data.password),
            correo_verificado=False,
            activo=True,
            rol_id=rol.id
        )
        self.usuarios.add(usuario)
        self.db.flush()

        token = self._emitir_token(usuario, "verificacion")
        self.notificaciones.crear(
            usuario_id=usuario.id,
            tipo="verificacion_correo",
            asunto="Confirma tu correo electrónico",
            contenido=(
                f"Hola {usuario.nombres}, usa el token {token.token} "
                f"para validar tu correo antes de {token.expira:%Y-%m-%d %H:%M}."
            )
        )
        self.db.commit()
        self.db.flush()
        return usuario, token.token

    def solicitar_verificacion(self, correo: str) -> str | None:
        """HU-002: genera un token de verificación y lo notifica."""
        usuario = self._usuario_activo(correo)
        if not usuario:
            return None

        self.tokens.invalidar_tokens(usuario.id, "verificacion")
        token = self._emitir_token(usuario, "verificacion")
        self.notificaciones.crear(
            usuario_id=usuario.id,
            tipo="verificacion_correo",
            asunto="Confirma tu correo electrónico",
            contenido=f"Token de verificación: {token.token}"
        )
        self.db.commit()
        self.db.flush()
        return token.token

    def validar_correo(self, token_str: str) -> Usuario:
        """HU-002: marca el correo como verificado."""
        token = self.tokens.get_by_token(token_str)
        if not token or token.tipo != "verificacion":
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Token no encontrado"
            )
        if token.usado:
            raise HTTPException(
                status_code=status.HTTP_409_CONFLICT,
                detail="El token ya fue utilizado"
            )
        if token.expira < datetime.utcnow():
            raise HTTPException(
                status_code=status.HTTP_410_GONE,
                detail="El token expiró"
            )

        usuario = self.usuarios.get_by_id(token.usuario_id)
        if not usuario:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Usuario no encontrado"
            )

        usuario.correo_verificado = True
        token.usado = True
        self.db.commit()
        self.db.flush()
        return usuario

    # ── HU-011: iniciar sesión ──────────────────────────────
    def login(self, data: LoginRequest) -> Usuario:
        usuario = self.usuarios.get_by_correo(data.correo)

        if not usuario or not verify_password(data.password, usuario.password_hash):
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Correo o contraseña incorrectos"
            )
        if not usuario.activo:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="La cuenta está desactivada"
            )
        return usuario

    # ── HU-005: recuperar contraseña ────────────────────────
    def solicitar_recuperacion(self, correo: str) -> str | None:
        usuario = self._usuario_activo(correo)
        if not usuario:
            return None

        self.tokens.invalidar_tokens(usuario.id, "recuperacion")
        token = self._emitir_token(usuario, "recuperacion")
        self.notificaciones.crear(
            usuario_id=usuario.id,
            tipo="recuperacion_password",
            asunto="Recuperación de contraseña",
            contenido=f"Token para recuperar tu contraseña: {token.token}"
        )
        self.db.commit()
        self.db.flush()
        return token.token

    def restablecer_password(self, data: RecuperarPasswordRequest) -> Usuario:
        token = self.tokens.get_by_token(data.token)
        if not token or token.tipo != "recuperacion":
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Token no encontrado"
            )
        if token.usado:
            raise HTTPException(
                status_code=status.HTTP_409_CONFLICT,
                detail="El token ya fue utilizado"
            )
        if token.expira < datetime.utcnow():
            raise HTTPException(
                status_code=status.HTTP_410_GONE,
                detail="El token expiró"
            )

        usuario = self.usuarios.get_by_id(token.usuario_id)
        if not usuario:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Usuario no encontrado"
            )

        usuario.password_hash = hash_password(data.nueva_password)
        token.usado = True
        self.db.commit()
        self.db.flush()
        return usuario

    # ── Auxiliares ──────────────────────────────────────────
    def _usuario_activo(self, correo: str) -> Usuario | None:
        usuario = self.usuarios.get_by_correo(correo)
        if usuario and usuario.activo:
            return usuario
        return None

    def _emitir_token(self, usuario: Usuario, tipo: str):
        return self.tokens.crear(
            usuario_id=usuario.id,
            tipo=tipo,
            expira=datetime.utcnow() + TIEMPO_VIDA_TOKEN
        )
