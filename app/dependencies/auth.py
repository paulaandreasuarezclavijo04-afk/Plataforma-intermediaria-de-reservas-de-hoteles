# ─────────────────────────────────────────────────────────────
# DEPENDENCIA — Obtener el usuario actual del token JWT
# ─────────────────────────────────────────────────────────────

from fastapi import Depends, HTTPException, security
from fastapi.security import HTTPAuthorizationCredentials, HTTPBearer
from sqlalchemy.orm import Session

from app.repository.database.session import get_db
from app.services.auth_service import AuthService, _jwt_decode

reusable_bearer = HTTPBearer(auto_error=False)


def get_current_user(
    credentials: HTTPAuthorizationCredentials = Depends(reusable_bearer),
    db: Session = Depends(get_db)
) -> object:
    """
    Dependency que:
    1. Extrae el token del header Authorization: Bearer <token>
    2. Decodifica y valida el JWT
    3. Devuelve el objeto Usuario
    4. Si no hay token o es inválido, lanza 401
    """
    if not credentials:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Falta el token de autorización",
            headers={"WWW-Authenticate": "Bearer"},
        )

    token = credentials.credentials
    try:
        payload = _jwt_decode(token)
        correo: str | None = payload.get("sub")
        if correo is None:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Token inválido: payload sin 'sub'",
            )
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail=f"Error al decodificar token: {e}",
        )

    usuario = AuthService(db).get_current_user(token)
    return usuario