# ─────────────────────────────────────────────────────────────
# REPOSITORIO DE HOTELES — HU-016
# ─────────────────────────────────────────────────────────────

from sqlalchemy import select
from sqlalchemy.orm import Session

from app.repository.base_repository import BaseRepository
from app.repository.database.models import Hotel, Usuario


class HotelRepository(BaseRepository[Hotel]):

    def __init__(self, session: Session):
        super().__init__(session, Hotel)

    def list_filtrado(
        self,
        ciudad: str | None = None,
        pais: str | None = None,
        nombre: str | None = None,
        incluir_inactivos: bool = False,
        limit: int = 100,
        offset: int = 0
    ) -> list[Hotel]:
        stmt = select(Hotel)

        if not incluir_inactivos:
            stmt = stmt.where(Hotel.activo == True)

        if ciudad:
            stmt = stmt.where(Hotel.ciudad.ilike(f"%{ciudad}%"))
        if pais:
            stmt = stmt.where(Hotel.pais.ilike(f"%{pais}%"))
        if nombre:
            stmt = stmt.where(Hotel.nombre.ilike(f"%{nombre}%"))

        stmt = stmt.order_by(Hotel.nombre).limit(limit).offset(offset)
        return list(self.session.scalars(stmt).all())

    def get_propietario(self, usuario_id: int) -> Usuario | None:
        return self.session.get(Usuario, usuario_id)
