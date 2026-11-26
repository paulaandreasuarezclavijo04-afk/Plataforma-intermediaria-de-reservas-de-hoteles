# ─────────────────────────────────────────────────────────────
# REPOSITORIO DE USUARIOS — HU-001
# ─────────────────────────────────────────────────────────────

from sqlalchemy import select
from sqlalchemy.orm import Session

from app.repository.base_repository import BaseRepository
from app.repository.database.models import Rol, Usuario


class UsuarioRepository(BaseRepository[Usuario]):

    def __init__(self, session: Session):
        super().__init__(session, Usuario)

    def get_by_correo(self, correo: str) -> Usuario | None:
        stmt = select(Usuario).where(Usuario.correo == correo)
        return self.session.scalars(stmt).first()

    def list_all(
        self,
        activo: bool | None = None,
        rol: str | None = None,
        limit: int = 100,
        offset: int = 0
    ) -> list[Usuario]:
        stmt = select(Usuario)

        if activo is not None:
            stmt = stmt.where(Usuario.activo == activo)

        if rol is not None:
            stmt = stmt.join(Rol).where(Rol.nombre == rol)

        stmt = stmt.order_by(Usuario.id).limit(limit).offset(offset)
        return list(self.session.scalars(stmt).all())

    def get_rol(self, nombre: str) -> Rol | None:
        stmt = select(Rol).where(Rol.nombre == nombre)
        return self.session.scalars(stmt).first()
