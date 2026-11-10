# ─────────────────────────────────────────────────────────────
# CAPA API — rutas HTTP con FastAPI
# Solo recibe peticiones y llama al servicio.
# Aquí NO hay lógica de negocio.
# ─────────────────────────────────────────────────────────────

from fastapi import APIRouter, HTTPException, status
from app.domain.producto import ProductoCreate, ProductoResponse
from app.services.producto_service import ProductoService
from app.repositories.producto_repository import producto_repository

# Crear el router con prefijo y etiqueta para la documentación
router = APIRouter(
    prefix="/productos",
    tags=["Productos"],
)

# Instanciar el servicio con inyección del repositorio
service = ProductoService(repo=producto_repository)


# ── GET /productos ────────────────────────────────────────────
@router.get("/", response_model=list[ProductoResponse])
def listar_productos():
    """Retorna todos los productos registrados."""
    return service.listar()


# ── GET /productos/{id} ───────────────────────────────────────
@router.get("/{id}", response_model=ProductoResponse)
def obtener_producto(id: int):
    """Retorna un producto por su ID."""
    try:
        return service.obtener(id)
    except ValueError as e:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=str(e)
        )


# ── POST /productos ───────────────────────────────────────────
@router.post("/", response_model=ProductoResponse,
             status_code=status.HTTP_201_CREATED)
def crear_producto(datos: ProductoCreate):
    """Crea un nuevo producto. El cuerpo se valida automáticamente."""
    try:
        return service.crear(datos)
    except ValueError as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(e)
        )


# ── PUT /productos/{id} ───────────────────────────────────────
@router.put("/{id}", response_model=ProductoResponse)
def actualizar_producto(id: int, datos: ProductoCreate):
    """Actualiza todos los campos de un producto."""
    try:
        return service.actualizar(id, datos)
    except ValueError as e:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=str(e)
        )


# ── DELETE /productos/{id} ────────────────────────────────────
@router.delete("/{id}")
def eliminar_producto(id: int):
    """Elimina un producto por ID."""
    try:
        return service.eliminar(id)
    except ValueError as e:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=str(e)
        )


# ── GET /productos/categoria/{cat} ────────────────────────────
@router.get("/categoria/{categoria}",
            response_model=list[ProductoResponse])
def por_categoria(categoria: str):
    """Filtra productos por categoría."""
    try:
        return service.por_categoria(categoria)
    except ValueError as e:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=str(e)
        )