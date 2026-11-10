# ─────────────────────────────────────────────────────────────
# CAPA SERVICIO — orquesta dominio + repositorio
# Contiene las reglas de negocio complejas y el flujo.
# No importa nada de FastAPI aquí.
# ─────────────────────────────────────────────────────────────

from app.domain.producto import ProductoCreate, ProductoResponse
from app.repositories.producto_repository import ProductoRepository


class ProductoService:

    def __init__(self, repo: ProductoRepository):
        # Inyección de dependencia: recibe el repositorio desde afuera
        self.repo = repo

    def listar(self) -> list[ProductoResponse]:
        return [ProductoResponse(**p.to_response())
                for p in self.repo.obtener_todos()]

    def obtener(self, id: int) -> ProductoResponse:
        p = self.repo.obtener_por_id(id)
        if not p:
            # El servicio lanza la excepción; la API la captura
            raise ValueError(f"Producto con id {id} no encontrado")
        return ProductoResponse(**p.to_response())

    def crear(self, datos: ProductoCreate) -> ProductoResponse:
        # ProductoCreate ya validó las reglas en el dominio (Pydantic)
        # Aquí podemos agregar reglas de negocio adicionales:

        # Regla: no se puede crear producto sin stock mayor a 0
        if datos.stock == 0:
            raise ValueError("No se puede registrar un producto sin stock inicial")

        p = self.repo.crear(
            nombre    = datos.nombre,
            precio    = datos.precio,
            stock     = datos.stock,
            categoria = datos.categoria,
        )
        return ProductoResponse(**p.to_response())

    def actualizar(self, id: int, datos: ProductoCreate) -> ProductoResponse:
        p = self.repo.actualizar(
            id        = id,
            nombre    = datos.nombre,
            precio    = datos.precio,
            stock     = datos.stock,
            categoria = datos.categoria,
        )
        if not p:
            raise ValueError(f"Producto {id} no existe")
        return ProductoResponse(**p.to_response())

    def eliminar(self, id: int) -> dict:
        ok = self.repo.eliminar(id)
        if not ok:
            raise ValueError(f"Producto {id} no existe")
        return {"mensaje": f"Producto {id} eliminado correctamente"}

    def por_categoria(self, categoria: str) -> list[ProductoResponse]:
        productos = self.repo.obtener_por_categoria(categoria)
        if not productos:
            raise ValueError(f"No hay productos en la categoría '{categoria}'")
        return [ProductoResponse(**p.to_response()) for p in productos]