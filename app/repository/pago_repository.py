# ─────────────────────────────────────────────────────────────
# REPOSITORIO DE PAGOS — HU-052 / HU-062
# ─────────────────────────────────────────────────────────────

from sqlalchemy import select
from sqlalchemy.orm import Session

from app.repository.base_repository import BaseRepository
from app.repository.database.models import Pago


class PagoRepository(BaseRepository[Pago]):

    def __init__(self, session: Session):
        super().__init__(session, Pago)

    def list_by_reserva(self, reserva_id: int) -> list[Pago]:
        stmt = (
            select(Pago)
            .where(Pago.reserva_id == reserva_id)
            .order_by(Pago.id)
        )
        return list(self.session.scalars(stmt).all())

    def get_activo(self, reserva_id: int) -> Pago | None:
        """Pago pendiente o pagado de una reserva (el más reciente)."""
        stmt = (
            select(Pago)
            .where(
                Pago.reserva_id == reserva_id,
                Pago.estado.in_(("pendiente", "pagado"))
            )
            .order_by(Pago.id.desc())
        )
        return self.session.scalars(stmt).first()
