# ─────────────────────────────────────────────────────────────
# SERVICIO DE USUARIOS — HU-001 (CRUD de usuarios)
# ─────────────────────────────────────────────────────────────

from fastapi import HTTPException, status
from sqlalchemy.orm import Session

from app.api.schemas.usuario_schema import UsuarioCreate, UsuarioUpdate, UsuarioResponse, UsuarioAsignarRol
from app.domain.password import hash_password
from app.repository.database.models import Usuario, Rol
from app.repository.usuario_repository import UsuarioRepository
from app.repository.reserva_repository import ReservaRepository
from app.repository.evaluacion_repository import EvaluacionRepository
from app.repository.asistencia_repository import AsistenciaRepository


class UsuarioService:

    def __init__(self, db: Session):
        self.db = db
        self.repo = UsuarioRepository(db)
        self.reserva_repo = ReservaRepository(db)
        self.evaluacion_repo = EvaluacionRepository(db)
        self.asistencia_repo = AsistenciaRepository(db)

    # ── Crear ───────────────────────────────────────────────
    def crear(self, data: UsuarioCreate) -> Usuario:
        # Validar que el correo no exista ya
        existente = self.repo.get_by_correo(data.correo)
        if existente:
            raise HTTPException(
                status_code=status.HTTP_409_CONFLICT,
                detail="El correo electrónico ya está registrado"
            )

        # Validar que el rol existe
        rol = self.db.query(Rol).filter(Rol.id == data.rol_id).first()
        if not rol:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=f"El rol ID {data.rol_id} no existe"
            )

        # Hashear contraseña
        password_hash = hash_password(data.password)

        # Crear usuario
        usuario = Usuario(
            nombres=data.nombres.strip(),
            apellidos=data.apellidos.strip(),
            correo=data.correo.strip().lower(),
            telefono=data.telefono,
            rol_id=data.rol_id,
            password_hash=password_hash,
            activo=True
        )
        self.repo.add(usuario)
        self.repo.commit()
        self.repo.flush()
        return usuario

    # ── Listar ───────────────────────────────────────────────
    def listar(self, activo: bool | None = None, rol_id: int | None = None, limit: int = 100, offset: int = 0) -> list[Usuario]:
        return self.repo.list_all(activo=activo, rol=None, limit=limit, offset=offset)

    # ── Obtener uno ───────────────────────────────────────────
    def obtener(self, usuario_id: int) -> Usuario:
        usuario = self.repo.get_by_id(usuario_id)
        if not usuario:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Usuario no encontrado"
            )
        return usuario

    # ── Actualizar ────────────────────────────────────────────
    def actualizar(self, usuario_id: int, data: UsuarioUpdate) -> Usuario:
        usuario = self.obtener(usuario_id)
        cambios = data.model_dump(exclude_unset=True)

        # Validar correo si se está cambiando
        if "correo" in cambios and cambios["correo"] is not None:
            correo_existente = self.repo.get_by_correo(cambios["correo"])
            if correo_existente and correo_existente.id != usuario.id:
                raise HTTPException(
                    status_code=status.HTTP_409_CONFLICT,
                    detail="El correo electrónico ya está registrado por otro usuario"
                )

        # Aplicar cambios
        if "nombres" in cambios and cambios["nombres"] is not None:
            usuario.nombres = cambios["nombres"].strip()
        if "apellidos" in cambios and cambios["apellidos"] is not None:
            usuario.apellidos = cambios["apellidos"].strip()
        if "correo" in cambios and cambios["correo"] is not None:
            usuario.correo = cambios["correo"].strip().lower()
        if "telefono" in cambios and cambios["telefono"] is not None:
            usuario.telefono = cambios["telefono"]
        if "activo" in cambios:
            usuario.activo = cambios["activo"]

        # No se permite actualizar la contraseña directamente desde aquí;
        # se usaría un endpoint separado de recuperación/restablecimiento

        self.repo.commit()
        self.repo.flush()
        return usuario

    # ── Eliminar (desactivar) ────────────────────────────────
    def eliminar(self, usuario_id: int) -> dict:
        usuario = self.obtener(usuario_id)
        
        # No se puede desactivar si tiene reservas, evaluaciones, asistencias, etc.
        
        # Verificar reservas activas usando list_filtrado
        reservas_activas = self.reserva_repo.list_filtrado(
            usuario_id=usuario_id, 
            estado="pendiente"
        )
        if reservas_activas:
            raise HTTPException(
                status_code=status.HTTP_409_CONFLICT,
                detail="No se puede desactivar usuario con reservas pendientes. Cancela o completa primero las reservas."
            )
        
        # Verificar evaluaciones públicas usando list_all
        evaluaciones_publicas = self.evaluacion_repo.list_all(usuario_id=usuario_id)
        if evaluaciones_publicas:
            raise HTTPException(
                status_code=status.HTTP_409_CONFLICT,
                detail="No se puede desactivar usuario con evaluaciones públicas. Retira o responde primero."
            )
        
        # Verificar solicitudes de asistencia
        solicitudes = self.asistencia_repo.list_filtrado(usuario_id=usuario_id)
        if solicitudes:
            raise HTTPException(
                status_code=status.HTTP_409_CONFLICT,
                detail="No se puede desactivar usuario con solicitudes de asistencia abiertas. Cierra o responde primero."
            )
        
        usuario.activo = False
        self.repo.commit()
        self.repo.flush()
        return {"mensaje": "Usuario desactivado exitosamente", "usuario_id": usuario.id}

    # ── Asignar Rol ──────────────────────────────────────────
    def asignar_rol(self, usuario_id: int, data: UsuarioAsignarRol) -> Usuario:
        usuario = self.obtener(usuario_id)
        
        # Validar que el rol existe
        rol = self.db.query(Rol).filter(Rol.id == data.rol_id).first()
        if not rol:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=f"El rol ID {data.rol_id} no existe"
            )
        
        usuario.rol_id = data.rol_id
        usuario.rol = rol  # ← CRITICAL: actualiza la relación para que rol_nombre se muestre
        self.db.commit()
        return usuario