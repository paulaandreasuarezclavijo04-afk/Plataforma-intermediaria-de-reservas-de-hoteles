# ─────────────────────────────────────────────────────────────
# CAPA DOMINIO — hash de contraseñas (PBKDF2 + salt)
# Sin dependencias externas: usa solo hashlib de la librería estándar.
# ─────────────────────────────────────────────────────────────

import hashlib
import hmac
import os

ITERACIONES = 120_000


def hash_password(password: str) -> str:
    """Genera un hash con salt aleatorio. Formato: pbkdf2$salt$hash"""
    salt = os.urandom(16)
    digest = hashlib.pbkdf2_hmac(
        "sha256",
        password.encode("utf-8"),
        salt,
        ITERACIONES
    )
    return f"pbkdf2${salt.hex()}${digest.hex()}"


def verify_password(password: str, password_hash: str) -> bool:
    """Compara una contraseña en claro contra el hash almacenado."""
    try:
        _, salt_hex, digest_hex = password_hash.split("$")
        salt = bytes.fromhex(salt_hex)
        digest = hashlib.pbkdf2_hmac(
            "sha256",
            password.encode("utf-8"),
            salt,
            ITERACIONES
        )
        return hmac.compare_digest(digest.hex(), digest_hex)
    except (ValueError, TypeError):
        return False
