# ─────────────────────────────────────────────────────────────
# PUNTO DE ENTRADA — crea la app FastAPI y registra los routers
# Capas: api (routers/schemas) → services → repository → models
# HU-016: CRUD de hoteles / HU-001: CRUD de usuarios / HU-021: CRUD de habitaciones
# ─────────────────────────────────────────────────────────────

from fastapi import FastAPI, Depends, HTTPException, status
from fastapi.middleware.cors import CORSMiddleware
from sqlalchemy.orm import Session

from app.repository.database.session import get_db

from app.api.routers.hotel_router import router as hotel_router
from app.api.routers.usuario_router import router as usuario_router
from app.api.routers.habitacion_router import router as habitacion_router

app = FastAPI(
    title="API Plataforma Intermediaria de Reservas de Hoteles",
    description="CRUD de hoteles (HU-016), usuarios (HU-001) y habitaciones (HU-021) con FastAPI + SQLAlchemy + SQLite",
    version="1.0.0",
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["*"],
    allow_headers=["*"],
)

# ── Registro de routers ─────────────────────────────────────
app.include_router(hotel_router)
app.include_router(usuario_router)
app.include_router(habitacion_router)


# ── Health check (público) ──────────────────────────────────
@app.get("/health", tags=["Sistema"])
def health():
    return {"status": "healthy"}


# ── Para correr directamente con: python main.py ────────────
if __name__ == "__main__":
    import uvicorn

    uvicorn.run("main:app", host="0.0.0.0", port=8000, reload=True)