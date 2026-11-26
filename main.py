# ─────────────────────────────────────────────────────────────
# PUNTO DE ENTRADA — crea la app FastAPI y registra los routers
# Capas: api (routers/schemas) → services → repository → models
# ─────────────────────────────────────────────────────────────

from fastapi import FastAPI, Depends, HTTPException, status
from fastapi.middleware.cors import CORSMiddleware
from fastapi.security import HTTPAuthorizationCredentials, HTTPBearer
from fastapi.staticfiles import StaticFiles
from fastapi.responses import FileResponse
from sqlalchemy.orm import Session

from app.repository.database.session import get_db

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
from app.dependencies.auth import get_current_user, reusable_bearer

app = FastAPI(
    title="API Plataforma Intermediaria de Reservas de Hoteles",
    description=(
        "API REST con arquitectura de capas — FastAPI + SQLAlchemy. "
        "Cubre las 15 historias de usuario del Parcial 2 con JWT activo."
    ),
    version="1.0.0",
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["*"],
    allow_headers=["*"],
)

# ── Dependencia HTTP Bearer (usada por los endpoints protegidos) ──
app.dependency_overrides = {}

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


# ── Health check (público) ──────────────────────────────────
@app.get("/health", tags=["Sistema"])
def health():
    return {"status": "healthy"}


# Montar archivos estáticos desde el directorio actual
app.mount("/", StaticFiles(directory=".", html=True), name="static")

# ── Ruta para servir la interfaz gráfica ──────────────────────
@app.get("/interface", include_in_schema=False)
def interface():
    return FileResponse("interface.html")


# ── Función auxiliar: obtener usuario desde header Authorization ─
def obtener_usuario_actual(
    credentials: HTTPAuthorizationCredentials = Depends(reusable_bearer),
    db = Depends(get_db)  # type: ignore
):
    """
    Dependency reusable: valida el JWT y devuelve el usuario.
    Cualquier router puede usar: `Depends(obtener_usuario_actual)`.
    """
    if not credentials:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Falta el token de autorización",
            headers={"WWW-Authenticate": "Bearer"},
        )
    token = credentials.credentials
    try:
        payload = jwt_decode(token)
        correo: str | None = payload.get("sub")
        if correo is None:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Token inválido: payload sin 'sub'",
            )
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail=f"Error al decodificar token: {e}",
        )

    from app.services.auth_service import AuthService
    auth_service = AuthService(db)
    return auth_service.get_current_user(token)


# ── Ruta de prueba protegida ────────────────────────────────
@app.get("/api/usuario-me", tags=["Auth"])
def usuario_actual(usuario = Depends(obtener_usuario_actual)):
    """Devuelve los datos del usuario que tenga un token JWT válido."""
    return {
        "mensaje": "Acceso concedido 🔐",
        "usuario": {
            "id": usuario.id,
            "nombres": usuario.nombres,
            "apellidos": usuario.apellidos,
            "correo": usuario.correo,
            "rol": usuario.rol.nombre if usuario.rol else "huesped",
        }
    }


# ── Para correr directamente con: python main.py ────────────
if __name__ == "__main__":
    import uvicorn

    uvicorn.run("main:app", host="0.0.0.0", port=8000, reload=True)