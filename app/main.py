# ─────────────────────────────────────────────────────────────
# Punto de entrada alternativo: uvicorn app.main:app
# Simplemente reutiliza la aplicación definida en la raíz.
# ─────────────────────────────────────────────────────────────

from main import app  # noqa: F401

__all__ = ["app"]
