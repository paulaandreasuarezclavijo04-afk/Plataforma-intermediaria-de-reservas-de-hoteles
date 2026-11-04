
from fastapi import FastAPI
from contextlib import asynccontextmanager


@asynccontextmanager
async def lifespan(app: FastAPI):
    print("Iniciando aplicación...")
    yield
    print("Cerrando aplicación...")


app = FastAPI(
    title="Mi Web Service",
    description="API para la plataforma intermediaria de reservas de hoteles",
    version="1.0.0",
    debug=True,
    lifespan=lifespan
)


@app.get("/", tags=["Inicio"])
async def inicio():
    return {
        "message": "Mi Web Service está funcionando",
        "status": "online"
    }


@app.get("/health", tags=["Sistema"])
async def health():
    return {
        "status": "healthy"
    }
