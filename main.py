# ─────────────────────────────────────────────────────────────
# PUNTO DE ENTRADA — crea la app FastAPI y registra los routers
# Capas: api (routers/schemas) → services → repository → models
# ─────────────────────────────────────────────────────────────

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from app.api.routers import (
    alojamiento_router,
    asistencia_router,
    auth_router,
    evaluacion_router,
    habitacion_router,
    hotel_router,
    pago_router,
    reserva_router,
    usuario_router
)

app = FastAPI(
    title="API Plataforma Intermediaria de Reservas de Hoteles",
    description=(
        "API REST con arquitectura de capas — FastAPI + SQLAlchemy. "
        "Cubre las 15 historias de usuario del Parcial 2: "
        "usuarios, autenticación, hoteles, habitaciones, búsqueda, "
        "disponibilidad, reservas, pagos, evaluaciones y asistencia."
    ),
    version="1.0.0",
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["*"],
    allow_headers=["*"],
)

# ── Registro de routers ─────────────────────────────────────
ROUTERS = (
    auth_router,
    usuario_router,
    hotel_router,
    habitacion_router,
    alojamiento_router,
    reserva_router,
    pago_router,
    evaluacion_router,
    asistencia_router,
)

for router_module in ROUTERS:
    app.include_router(router_module.router)


# ── Ruta raíz — bienvenida ──────────────────────────────────
@app.get("/", tags=["Root"])
def root():
    return {
        "mensaje": "API corriendo correctamente",
        "docs": "http://127.0.0.1:8000/docs",
        "version": "1.0.0",
    }


@app.get("/health", tags=["Sistema"])
def health():
    return {"status": "healthy"}


# ── Para correr directamente con: python main.py ────────────
if __name__ == "__main__":
    import uvicorn

    uvicorn.run("main:app", host="0.0.0.0", port=8000, reload=True)
