# ─────────────────────────────────────────────────────────────
# SERVICIO DE AUTENTICACIÓN CON JWT — HU-011
# Login que devuelve token JWT + validación en los endpoints
# ─────────────────────────────────────────────────────────────

import json
import uuid
from datetime import datetime, timedelta

import jwt  # pyjwt

from fastapi import HTTPException, status
from sqlalchemy.orm import Session

from app.api.schemas.auth_schema import LoginRequest, RegistroRequest, UsuarioSesion
from app.domain.password import hash_password, verify_password
from app.repository.database.models import Rol, Usuario
from app.repository.usuario_repository import UsuarioRepository

# Configuración del JWT
SECRET_KEY = "cambia-este-valor-en-produccion-clave-secreta-muy-larga"
ALGORITHM = "HS256"
ACCESS_TOKEN_EXPIRE_MINUTES = 30


def _jwt_encode(subject: str, extra: dict | None = None) -> str:
    """Codifica un payload JWT."""
    now = datetime.utcnow()
    exp = now + timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)
    to_encode: dict = {"sub": subject, "iat": now, "exp": exp, "jti": str(uuid.uuid4())}
    to_encode = {**to_encode, **(extra or {})}
    encoded_jwt = jwt.encode(to_encode, SECRET_KEY, algorithm=ALGORITHM)
    return encoded_jwt


def _jwt_decode(token: str) -> dict:
    """Decodifica y valida un payload JWT. Lanza HTTPException si es inválido."""
    try:
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        return payload
    except jwt.ExpiredSignatureError:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="El token ha expirado",
        )
    except jwt.InvalidTokenError:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Token inválido",
        )


class AuthService:

    def __init__(self, db: Session):
        self.db = db
        self.usuarios = UsuarioRepository(db)

    # ── HU-002: registrar usuario ────────────────────────────
    def registrar(self, data: RegistroRequest) -> Usuario:
        correo = data.correo.strip().lower()
        existente = self.usuarios.get_by_correo(correo)
        if existente:
            raise HTTPException(
                status_code=status.HTTP_409_CONFLICT,
                detail="El correo electrónico ya está registrado",
            )

        rol_nombre = str(data.rol).strip().lower()
        mapa_roles = {"admin": 1, "propietario": 2, "huesped": 3}
        rol_id = mapa_roles.get(rol_nombre)
        if rol_id is None:
            rol_obj = self.db.query(Rol).filter(Rol.nombre.ilike(rol_nombre)).first()
            if not rol_obj:
                raise HTTPException(
                    status_code=status.HTTP_400_BAD_REQUEST,
                    detail=f"El rol '{data.rol}' no existe",
                )
            rol_id = rol_obj.id
        else:
            rol_obj = self.db.query(Rol).filter(Rol.id == rol_id).first()
            if not rol_obj:
                raise HTTPException(
                    status_code=status.HTTP_400_BAD_REQUEST,
                    detail=f"El rol '{data.rol}' no existe",
                )

        usuario = Usuario(
            nombres=data.nombres.strip(),
            apellidos=data.apellidos.strip(),
            correo=correo,
            telefono=data.telefono,
            rol_id=rol_id,
            password_hash=hash_password(data.password),
            activo=True,
            correo_verificado=False,
        )
        self.db.add(usuario)
        self.db.commit()
        self.db.refresh(usuario)
        return usuario

    # ── HU-011: iniciar sesión (devuelve JWT) ────────────────
    def login(self, data: LoginRequest) -> dict:
        usuario = self.usuarios.get_by_correo(data.correo)

        if not usuario or not verify_password(data.password, usuario.password_hash):
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Correo o contraseña incorrectos",
            )
        if not usuario.activo:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="La cuenta está desactivada",
            )

        # Payload: sub = correo (o id, como prefieras)
        access_token = _jwt_encode(subject=usuario.correo, extra={
            "id": usuario.id,
            "rol": usuario.rol.nombre if usuario.rol else "huesped",
            "correo_verificado": usuario.correo_verificado,
        })

        return {
            "access_token": access_token,
            "token_type": "bearer",
            "usuario": {
                "id": usuario.id,
                "nombres": usuario.nombres,
                "apellidos": usuario.apellidos,
                "correo": usuario.correo,
                "rol": usuario.rol.nombre if usuario.rol else "huesped",
                "correo_verificado": usuario.correo_verificado,
            }
        }

    # ── Validar quién es el usuario actual ──────────────────
    def get_current_user(self, token: str) -> Usuario:
        payload = _jwt_decode(token)
        correo: str | None = payload.get("sub")
        if correo is None:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Token inválido: no tiene 'sub'",
            )
        usuario = self.usuarios.get_by_correo(correo)
        if not usuario:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Usuario asociado al token no encontrado",
            )
        if not usuario.activo:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="La cuenta está desactivada",
            )
        return usuario