# ─────────────────────────────────────────────────────────────
# SERVICIO DE USUARIOS — HU-001 (CRUD de usuarios)
# ─────────────────────────────────────────────────────────────

from fastapi import HTTPException, status
from sqlalchemy.orm import Session

from app.api.schemas.usuario_schema import UsuarioCreate, UsuarioUpdate
from app.domain.password import hash_password
from app.repository.database.models import Usuario
from app.repository.usuario_repository import UsuarioRepository

ROLES_VALIDOS = ("admin", "propietario", "huesped")


class UsuarioService:

    def __init__(self, db: Session):
        self.repo = UsuarioRepository(db)

    # ── Consultas ───────────────────────────────────────────
    def listar(
        self,
        activo: bool | None = None,
        rol: str | None = None
    ) -> list[Usuario]:
        return self.repo.list_all(activo=activo, rol=rol)

    def obtener(self, usuario_id: int) -> Usuario:
        usuario = self.repo.get_by_id(usuario_id)
        if not usuario:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Usuario no encontrado"
            )
        return usuario

    # ── Crear ───────────────────────────────────────────────
    def crear(self, data: UsuarioCreate) -> Usuario:
        if self.repo.get_by_correo(data.correo):
            raise HTTPException(
                status_code=status.HTTP_409_CONFLICT,
                detail="Ya existe un usuario con ese correo"
            )

        rol = self.repo.get_rol(data.rol)
        if not rol:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=f"Rol inválido: {' | '.join(ROLES_VALIDOS)}"
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
        self.repo.add(usuario)
        self.repo.commit()
        self.repo.flush()
        return usuario

    # ── Actualizar ──────────────────────────────────────────
    def actualizar(self, usuario_id: int, data: UsuarioUpdate) -> Usuario:
        usuario = self.obtener(usuario_id)
        cambios = data.model_dump(exclude_unset=True)

        if "correo" in cambios and cambios["correo"]:
            existente = self.repo.get_by_correo(cambios["correo"])
            if existente and existente.id != usuario_id:
                raise HTTPException(
                    status_code=status.HTTP_409_CONFLICT,
                    detail="Ya existe un usuario con ese correo"
                )
            usuario.correo = cambios["correo"]

        if cambios.get("rol"):
            rol = self.repo.get_rol(cambios["rol"])
            if not rol:
                raise HTTPException(
                    status_code=status.HTTP_400_BAD_REQUEST,
                    detail=f"Rol inválido: {' | '.join(ROLES_VALIDOS)}"
                )
            usuario.rol_id = rol.id

        if cambios.get("password"):
            usuario.password_hash = hash_password(cambios["password"])

        for campo in ("nombres", "apellidos", "telefono", "activo"):
            if campo in cambios and cambios[campo] is not None:
                valor = cambios[campo]
                setattr(usuario, campo, valor.strip().title()
                        if isinstance(valor, str) and campo in ("nombres", "apellidos")
                        else valor)

        self.repo.commit()
        self.repo.flush()
        return usuario

    # ── Eliminar (borrado lógico) ───────────────────────────
    def eliminar(self, usuario_id: int) -> Usuario:
        usuario = self.obtener(usuario_id)
        if not usuario.activo:
            raise HTTPException(
                status_code=status.HTTP_409_CONFLICT,
                detail="El usuario ya está desactivado"
            )
        usuario.activo = False
        self.repo.commit()
        self.repo.flush()
        return usuario
