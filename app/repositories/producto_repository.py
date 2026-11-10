# ─────────────────────────────────────────────────────────────
# CAPA REPOSITORIO — única responsabilidad: guardar y recuperar
# Solo manipula datos. Sin lógica de negocio aquí.
# ─────────────────────────────────────────────────────────────

from app.domain.producto import Producto
from typing import Optional


class ProductoRepository:

    def __init__(self):
        # Almacén en memoria: lista de objetos Producto
        self._datos: list[Producto] = []
        self._siguiente_id: int = 1

        # Datos de ejemplo para arrancar el sistema
        self._seed()

    def _seed(self):
        """Carga datos iniciales de ejemplo."""
        iniciales = [
            Producto(1, "Laptop",      3_500_000, 10, "Tecnología"),
            Producto(2, "Mouse Inalámbrico", 85_000, 25, "Tecnología"),
            Producto(3, "Cuaderno",    8_500,  0,  "Papelería"),
        ]
        self._datos = iniciales
        self._siguiente_id = 4

    # ── CRUD básico ───────────────────────────────────────────

    def obtener_todos(self) -> list[Producto]:
        return self._datos.copy()

    def obtener_por_id(self, id: int) -> Optional[Producto]:
        return next((p for p in self._datos if p.id == id), None)

    def crear(self, nombre: str, precio: float,
              stock: int, categoria: str) -> Producto:
        nuevo = Producto(
            id        = self._siguiente_id,
            nombre    = nombre,
            precio    = precio,
            stock     = stock,
            categoria = categoria,
        )
        self._datos.append(nuevo)
        self._siguiente_id += 1
        return nuevo

    def actualizar(self, id: int, nombre: str, precio: float,
                   stock: int, categoria: str) -> Optional[Producto]:
        producto = self.obtener_por_id(id)
        if not producto:
            return None
        producto.nombre    = nombre
        producto.precio    = precio
        producto.stock     = stock
        producto.categoria = categoria
        return producto

    def eliminar(self, id: int) -> bool:
        producto = self.obtener_por_id(id)
        if not producto:
            return False
        self._datos.remove(producto)
        return True

    def obtener_por_categoria(self, categoria: str) -> list[Producto]:
        return [p for p in self._datos
                if p.categoria.lower() == categoria.lower()]


# Instancia única compartida (Singleton simple)
producto_repository = ProductoRepository()