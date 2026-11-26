# ─────────────────────────────────────────────────────────────
# ROUTER DE USUARIOS — HU-001 (CRUD de usuarios)
# ─────────────────────────────────────────────────────────────

from fastapi import APIRouter, Depends, status
from sqlalchemy.orm import Session

from app.api.schemas.usuario_schema import (
    ApiResponse,
    UsuarioAsignarRol,
    UsuarioCreate,
    UsuarioData,
    UsuarioUpdate,
)
from app.dependencies.auth import require_admin
from app.repository.database.session import get_db
from app.services.usuario_service import UsuarioService, usuario_a_data

router = APIRouter(prefix="/api/v1/usuarios", tags=["Usuarios"])


@router.post(
    "",
    response_model=ApiResponse[UsuarioData],
    status_code=status.HTTP_201_CREATED,
    summary="HU-001: crear usuario",
)
def crear(
    data: UsuarioCreate,
    db: Session = Depends(get_db),
    _admin=Depends(require_admin),
):
    usuario = UsuarioService(db).crear(data)
    return ApiResponse(mensaje="Usuario creado correctamente", data=usuario_a_data(usuario), success=True)


@router.get(
    "",
    response_model=ApiResponse[list[UsuarioData]],
    summary="HU-001: listar usuarios",
)
def listar(
    activo: bool | None = None,
    rol_id: int | None = None,
    limit: int = 100,
    offset: int = 0,
    db: Session = Depends(get_db),
    _admin=Depends(require_admin),
):
    usuarios = UsuarioService(db).listar(activo=activo, rol_id=rol_id, limit=limit, offset=offset)
    return ApiResponse(mensaje="Usuarios consultados correctamente", data=[usuario_a_data(u) for u in usuarios], success=True)


@router.get(
    "/{usuario_id}",
    response_model=ApiResponse[UsuarioData],
    summary="HU-001: consultar usuario",
)
def obtener(
    usuario_id: int,
    db: Session = Depends(get_db),
    _admin=Depends(require_admin),
):
    usuario = UsuarioService(db).obtener(usuario_id)
    return ApiResponse(mensaje="Usuario consultado correctamente", data=usuario_a_data(usuario), success=True)


@router.put(
    "/{usuario_id}",
    response_model=ApiResponse[UsuarioData],
    summary="HU-001: actualizar usuario",
)
def actualizar(
    usuario_id: int,
    data: UsuarioUpdate,
    db: Session = Depends(get_db),
    _admin=Depends(require_admin),
):
    usuario = UsuarioService(db).actualizar(usuario_id, data)
    return ApiResponse(mensaje="Usuario actualizado correctamente", data=usuario_a_data(usuario), success=True)


@router.put(
    "/{usuario_id}/rol",
    response_model=ApiResponse[UsuarioData],
    summary="HU-001: asignar rol a usuario",
)
def asignar_rol(
    usuario_id: int,
    data: UsuarioAsignarRol,
    db: Session = Depends(get_db),
    _admin=Depends(require_admin),
):
    usuario = UsuarioService(db).asignar_rol(usuario_id, data)
    return ApiResponse(mensaje="Rol asignado correctamente", data=usuario_a_data(usuario), success=True)


@router.delete(
    "/{usuario_id}",
    response_model=ApiResponse[dict],
    summary="HU-001: retirar usuario",
)
def eliminar(
    usuario_id: int,
    db: Session = Depends(get_db),
    _admin=Depends(require_admin),
):
    resultado = UsuarioService(db).eliminar(usuario_id)
    return ApiResponse(mensaje="Usuario retirado correctamente", data=resultado, success=True)