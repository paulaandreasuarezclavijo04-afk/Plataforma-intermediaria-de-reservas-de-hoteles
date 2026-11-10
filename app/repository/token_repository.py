# ─────────────────────────────────────────────────────────────
# REPOSITORIO DE TOKENS DE UN SOLO USO
# Soporta HU-002 (validar correo) y HU-005 (recuperar contraseña)
# ─────────────────────────────────────────────────────────────

from datetime import datetime

from sqlalchemy import select
from sqlalchemy.orm import Session

from app.repository.base_repository import BaseRepository
from app.repository.database.models import TokenSeguro


class TokenRepository(BaseRepository[TokenSeguro]):

    def __init__(self, session: Session):
        super().__init__(session, TokenSeguro)

    def crear(
        self,
        usuario_id: int,
        tipo: str,
        expira: datetime
    ) -> TokenSeguro:
        import secrets

        token = TokenSeguro(
            token=secrets.token_hex(24),
            tipo=tipo,
            expira=expira,
            usado=False,
            usuario_id=usuario_id
        )
        return self.add(token)

    def get_by_token(self, token: str) -> TokenSeguro | None:
        stmt = select(TokenSeguro).where(TokenSeguro.token == token)
        return self.session.scalars(stmt).first()

    def invalidar_tokens(self, usuario_id: int, tipo: str) -> None:
        """Marca como usados los tokens activos de un usuario."""
        stmt = select(TokenSeguro).where(
            TokenSeguro.usuario_id == usuario_id,
            TokenSeguro.tipo == tipo,
            TokenSeguro.usado == False
        )
        for token in self.session.scalars(stmt).all():
            token.usado = True
