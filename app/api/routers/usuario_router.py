# ─────────────────────────────────────────────────────────────
# ROUTER DE USUARIOS — HU-001 (CRUD de usuarios)
# ─────────────────────────────────────────────────────────────

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session

from app.api.schemas.usuario_schema import UsuarioCreate, UsuarioUpdate, UsuarioResponse, UsuarioAsignarRol
from app.repository.database.session import get_db
from app.services.usuario_service import UsuarioService

router = APIRouter(prefix="/api/usuarios", tags=["Usuarios"])


@router.post(
    "",
    response_model=UsuarioResponse,
    status_code=status.HTTP_201_CREATED,
    summary="HU-001: crear usuario"
)
def crear(data: UsuarioCreate, db: Session = Depends(get_db)):
    return UsuarioService(db).crear(data)


@router.get(
    "",
    response_model=list[UsuarioResponse],
    summary="HU-001: listar usuarios"
)
def listar(
    activo: bool | None = None,
    rol_id: int | None = None,
    limit: int = 100,
    offset: int = 0,
    db: Session = Depends(get_db)
):
    return UsuarioService(db).listar(activo=activo, rol_id=rol_id, limit=limit, offset=offset)


@router.get(
    "/{usuario_id}",
    response_model=UsuarioResponse,
    summary="HU-001: consultar usuario"
)
def obtener(usuario_id: int, db: Session = Depends(get_db)):
    return UsuarioService(db).obtener(usuario_id)


@router.put(
    "/{usuario_id}",
    response_model=UsuarioResponse,
    summary="HU-001: actualizar usuario"
)
def actualizar(usuario_id: int, data: UsuarioUpdate, db: Session = Depends(get_db)):
    return UsuarioService(db).actualizar(usuario_id, data)


@router.put(
    "/{usuario_id}/rol",
    response_model=UsuarioResponse,
    summary="HU-001: asignar rol a usuario"
)
def asignar_rol(usuario_id: int, data: UsuarioAsignarRol, db: Session = Depends(get_db)):
    return UsuarioService(db).asignar_rol(usuario_id, data)


@router.delete(
    "/{usuario_id}",
    summary="HU-001: desactivar usuario",
    response_model=dict
)
def eliminar(usuario_id: int, db: Session = Depends(get_db)):
    return UsuarioService(db).eliminar(usuario_id)