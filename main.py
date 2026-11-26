# ─────────────────────────────────────────────────────────────
# PUNTO DE ENTRADA — crea la app FastAPI y registra los routers
# Capas: api (routers/schemas) → services → repository → models
# HU-016: CRUD de hoteles / HU-001: CRUD de usuarios / HU-021: CRUD de habitaciones / HU-076: CRUD de evaluaciones / HU-036: Crear reserva / HU-039: Consultar reserva / HU-068: Enviar confirmación de reserva
# ─────────────────────────────────────────────────────────────

from fastapi import FastAPI, Depends, HTTPException, Request, status
from fastapi.exceptions import RequestValidationError
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
from sqlalchemy.orm import Session

from app.repository.database.session import get_db

from app.api.routers.auth_router import router as auth_router
from app.api.routers.hotel_router import router as hotel_router, v1_router as hotel_v1_router
from app.api.routers.usuario_router import router as usuario_router
from app.api.routers.habitacion_router import router as habitacion_router
from app.api.routers.evaluacion_router import router as evaluacion_router
from app.api.routers.notificacion_router import router as notificacion_router
from app.api.routers.reserva_router import router as reserva_router

app = FastAPI(
    title="API Plataforma Intermediaria de Reservas de Hoteles",
    description="CRUD de hoteles (HU-016), usuarios (HU-001), habitaciones (HU-021), evaluaciones (HU-076) y reservas (HU-036, HU-039, HU-068) con FastAPI + SQLAlchemy + SQLite",
    version="1.0.0",
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["*"],
    allow_headers=["*"],
)

# ── Registro de routers ─────────────────────────────────────
app.include_router(auth_router)
app.include_router(hotel_router)
app.include_router(hotel_v1_router)
app.include_router(usuario_router)
app.include_router(habitacion_router)
app.include_router(evaluacion_router)
app.include_router(notificacion_router)
app.include_router(reserva_router)


# ── Manejo de errores consistente (HU-001) ───────────────────
@app.exception_handler(HTTPException)
async def http_exception_handler(request: Request, exc: HTTPException):
    return JSONResponse(
        status_code=exc.status_code,
        content={"mensaje": exc.detail, "data": None, "success": False},
    )


@app.exception_handler(RequestValidationError)
async def validation_exception_handler(request: Request, exc: RequestValidationError):
    errores = exc.errors()
    detalle = "; ".join([f"{'.'.join(map(str, e.get('loc', [])))}: {e.get('msg', 'inválido')}" for e in errores[:3]])
    return JSONResponse(
        status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
        content={"mensaje": f"Error de validación: {detalle}", "data": None, "success": False},
    )


@app.exception_handler(Exception)
async def unhandled_exception_handler(request: Request, exc: Exception):
    return JSONResponse(
        status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
        content={"mensaje": "Error interno del servicio. Intente más tarde.", "data": None, "success": False},
    )


# ── Health check (público) ──────────────────────────────────
@app.get("/health", tags=["Sistema"])
def health():
    return {"status": "healthy"}


# ── Para correr directamente con: python main.py ────────────
if __name__ == "__main__":
    import uvicorn

    uvicorn.run("main:app", host="0.0.0.0", port=8000, reload=True)