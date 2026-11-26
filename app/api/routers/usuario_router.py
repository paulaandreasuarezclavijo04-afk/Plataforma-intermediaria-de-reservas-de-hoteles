# ─────────────────────────────────────────────────────────────
# ROUTER DE USUARIOS — HU-001 (CRUD de usuarios)
# ─────────────────────────────────────────────────────────────

from fastapi import APIRouter, Depends, Query, status
from sqlalchemy.orm import Session

from app.api.schemas.usuario_schema import (
    UsuarioCreate,
    UsuarioResponse,
    UsuarioUpdate
)
from app.repository.database.session import get_db
from app.services.usuario_service import UsuarioService

router = APIRouter(prefix="/api/usuarios", tags=["Usuarios"])


@router.get(
    "",
    response_model=list[UsuarioResponse],
    summary="HU-001: listar usuarios"
)
def listar(
    activo: bool | None = Query(None),
    rol: str | None = Query(None),
    db: Session = Depends(get_db)
):
    return UsuarioService(db).listar(activo=activo, rol=rol)


@router.get(
    "/{usuario_id}",
    response_model=UsuarioResponse,
    summary="HU-001: consultar usuario"
)
def obtener(usuario_id: int, db: Session = Depends(get_db)):
    return UsuarioService(db).obtener(usuario_id)


@router.post(
    "",
    response_model=UsuarioResponse,
    status_code=status.HTTP_201_CREATED,
    summary="HU-001: crear usuario"
)
def crear(data: UsuarioCreate, db: Session = Depends(get_db)):
    return UsuarioService(db).crear(data)


@router.put(
    "/{usuario_id}",
    response_model=UsuarioResponse,
    summary="HU-001: actualizar usuario"
)
def actualizar(
    usuario_id: int,
    data: UsuarioUpdate,
    db: Session = Depends(get_db)
):
    return UsuarioService(db).actualizar(usuario_id, data)


@router.delete(
    "/{usuario_id}",
    response_model=UsuarioResponse,
    summary="HU-001: desactivar usuario (borrado lógico)"
)
def eliminar(usuario_id: int, db: Session = Depends(get_db)):
    return UsuarioService(db).eliminar(usuario_id)
