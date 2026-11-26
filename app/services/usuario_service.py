# ─────────────────────────────────────────────────────────────
# SERVICIO DE USUARIOS — HU-001 (CRUD de usuarios)
# ─────────────────────────────────────────────────────────────

import logging

from fastapi import HTTPException, status
from sqlalchemy.orm import Session

from app.api.schemas.usuario_schema import UsuarioCreate, UsuarioUpdate, UsuarioAsignarRol, UsuarioData
from app.domain.password import hash_password
from app.repository.database.models import Usuario, Rol
from app.repository.usuario_repository import UsuarioRepository
from app.repository.reserva_repository import ReservaRepository
from app.repository.evaluacion_repository import EvaluacionRepository
from app.repository.asistencia_repository import AsistenciaRepository

logger = logging.getLogger("auditoria.usuarios")


def _rol_a_id(db: Session, rol: str | int) -> int:
    if isinstance(rol, int):
        return rol
    nombre = str(rol).strip().lower()
    mapa = {"admin": 1, "propietario": 2, "huesped": 3}
    if nombre in mapa:
        return mapa[nombre]
    obj = db.query(Rol).filter(Rol.nombre.ilike(nombre)).first()
    if not obj:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=f"El rol '{rol}' no existe")
    return obj.id


def _nombre_partes(data_nombre: str | None, nombres: str | None, apellidos: str | None) -> tuple[str, str]:
    if nombres or apellidos:
        return (nombres or "").strip(), (apellidos or "").strip()
    if data_nombre:
        partes = data_nombre.strip().split(None, 1)
        if len(partes) == 1:
            return partes[0], ""
        return partes[0], partes[1]
    return "", ""


def usuario_a_data(usuario: Usuario) -> UsuarioData:
    nombre = f"{usuario.nombres} {usuario.apellidos}".strip()
    rol = usuario.rol.nombre.upper() if usuario.rol and usuario.rol.nombre else "HUESPED"
    return UsuarioData(
        id=usuario.id,
        nombre=nombre,
        correo=usuario.correo,
        rol=rol,
        activo=usuario.activo,
        telefono=usuario.telefono,
    )


class UsuarioService:

    def __init__(self, db: Session):
        self.db = db
        self.repo = UsuarioRepository(db)
        self.reserva_repo = ReservaRepository(db)
        self.evaluacion_repo = EvaluacionRepository(db)
        self.asistencia_repo = AsistenciaRepository(db)

    def crear(self, data: UsuarioCreate) -> Usuario:
        existente = self.repo.get_by_correo(data.correo)
        if existente:
            raise HTTPException(status_code=status.HTTP_409_CONFLICT, detail="El correo electrónico ya está registrado")

        rol_id = _rol_a_id(self.db, data.rol)
        rol = self.db.query(Rol).filter(Rol.id == rol_id).first()
        if not rol:
            raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=f"El rol ID {rol_id} no existe")

        nombres, apellidos = _nombre_partes(data.nombre, data.nombres, data.apellidos)
        if not nombres:
            raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="El nombre es obligatorio")

        usuario = Usuario(
            nombres=nombres,
            apellidos=apellidos,
            correo=data.correo.strip().lower(),
            telefono=data.telefono,
            rol_id=rol_id,
            password_hash=hash_password(data.password),
            activo=True,
        )
        self.repo.add(usuario)
        self.repo.commit()
        self.repo.flush()
        self.db.refresh(usuario)
        logger.info("AUDIT crear_usuario id=%s correo=%s rol=%s", usuario.id, usuario.correo, rol.nombre)
        return usuario

    def listar(self, activo: bool | None = None, rol_id: int | None = None, limit: int = 100, offset: int = 0) -> list[Usuario]:
        return self.repo.list_all(activo=activo, rol=None, limit=limit, offset=offset)

    def obtener(self, usuario_id: int) -> Usuario:
        usuario = self.repo.get_by_id(usuario_id)
        if not usuario:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Usuario no encontrado")
        return usuario

    def actualizar(self, usuario_id: int, data: UsuarioUpdate) -> Usuario:
        usuario = self.obtener(usuario_id)
        cambios = data.model_dump(exclude_unset=True)

        if "correo" in cambios and cambios["correo"] is not None:
            correo_existente = self.repo.get_by_correo(cambios["correo"])
            if correo_existente and correo_existente.id != usuario.id:
                raise HTTPException(status_code=status.HTTP_409_CONFLICT, detail="El correo electrónico ya está registrado por otro usuario")

        nombres, apellidos = _nombre_partes(cambios.get("nombre"), cambios.get("nombres"), cambios.get("apellidos"))
        if nombres:
            usuario.nombres = nombres
        if apellidos is not None and ("apellidos" in cambios or "nombre" in cambios):
            usuario.apellidos = apellidos
        if "correo" in cambios and cambios["correo"] is not None:
            usuario.correo = cambios["correo"].strip().lower()
        if "telefono" in cambios:
            usuario.telefono = cambios["telefono"]
        if "activo" in cambios and cambios["activo"] is not None:
            usuario.activo = cambios["activo"]

        self.repo.commit()
        self.repo.flush()
        self.db.refresh(usuario)
        logger.info("AUDIT actualizar_usuario id=%s correo=%s", usuario.id, usuario.correo)
        return usuario

    def eliminar(self, usuario_id: int) -> dict:
        usuario = self.obtener(usuario_id)

        reservas_activas = self.reserva_repo.list_filtrado(usuario_id=usuario_id, estado="pendiente")
        if reservas_activas:
            raise HTTPException(status_code=status.HTTP_409_CONFLICT, detail="No se puede desactivar usuario con reservas pendientes. Cancela o completa primero las reservas.")

        evaluaciones_publicas = self.evaluacion_repo.list_all(usuario_id=usuario_id)
        if evaluaciones_publicas:
            raise HTTPException(status_code=status.HTTP_409_CONFLICT, detail="No se puede desactivar usuario con evaluaciones públicas. Retira o responde primero.")

        solicitudes = self.asistencia_repo.list_filtrado(usuario_id=usuario_id)
        if solicitudes:
            raise HTTPException(status_code=status.HTTP_409_CONFLICT, detail="No se puede desactivar usuario con solicitudes de asistencia abiertas. Cierra o responde primero.")

        usuario.activo = False
        self.repo.commit()
        self.repo.flush()
        logger.info("AUDIT retirar_usuario id=%s correo=%s", usuario.id, usuario.correo)
        return {"id": usuario.id, "correo": usuario.correo, "activo": usuario.activo}

    def asignar_rol(self, usuario_id: int, data: UsuarioAsignarRol) -> Usuario:
        usuario = self.obtener(usuario_id)
        rol_id = _rol_a_id(self.db, data.rol)
        rol = self.db.query(Rol).filter(Rol.id == rol_id).first()
        if not rol:
            raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=f"El rol ID {rol_id} no existe")

        usuario.rol_id = rol_id
        usuario.rol = rol
        self.db.commit()
        self.db.refresh(usuario)
        logger.info("AUDIT asignar_rol id=%s rol=%s", usuario.id, rol.nombre)
        return usuario