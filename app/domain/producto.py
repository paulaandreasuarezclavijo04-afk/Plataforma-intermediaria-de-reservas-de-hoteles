# ─────────────────────────────────────────────────────────────
# CAPA DOMINIO — define la entidad y sus reglas de negocio
# No importa nada de FastAPI ni de base de datos aquí.
# ─────────────────────────────────────────────────────────────

from pydantic import BaseModel, Field, field_validator
from typing import Optional


# ── Schema de ENTRADA (lo que recibe la API del cliente) ──────
class ProductoCreate(BaseModel):
    nombre:      str   = Field(..., min_length=2, description="Nombre del producto")
    precio:      float = Field(..., gt=0,        description="Precio mayor a 0")
    stock:       int   = Field(..., ge=0,        description="Stock no negativo")
    categoria:   str   = Field(..., min_length=2)

    # ── REGLA DE NEGOCIO: nombre no puede tener números ──────
    @field_validator("nombre")
    @classmethod
    def nombre_sin_numeros(cls, v):
        if any(c.isdigit() for c in v):
            raise ValueError("El nombre no puede contener números")
        return v.strip().title()

    # ── REGLA DE NEGOCIO: precio con dos decimales máximo ────
    @field_validator("precio")
    @classmethod
    def precio_valido(cls, v):
        return round(v, 2)


# ── Schema de SALIDA (lo que devuelve la API al cliente) ──────
class ProductoResponse(BaseModel):
    id:          int
    nombre:      str
    precio:      float
    stock:       int
    categoria:   str
    disponible:  bool  # calculado: stock > 0

    class Config:
        from_attributes = True


# ── Modelo interno del dominio (la "entidad real") ────────────
class Producto:
    def __init__(self, id: int, nombre: str, precio: float,
                 stock: int, categoria: str):
        self.id        = id
        self.nombre    = nombre
        self.precio    = precio
        self.stock     = stock
        self.categoria = categoria

    # REGLA DE NEGOCIO: ¿hay stock suficiente?
    def tiene_stock(self, cantidad: int = 1) -> bool:
        return self.stock >= cantidad

    # REGLA DE NEGOCIO: descuento solo si precio > 50.000
    def aplicar_descuento(self, porcentaje: float) -> float:
        if self.precio < 50_000:
            raise ValueError("Descuento solo aplica a precios mayores a $50.000")
        return round(self.precio * (1 - porcentaje / 100), 2)

    def to_response(self) -> dict:
        return {
            "id":         self.id,
            "nombre":     self.nombre,
            "precio":     self.precio,
            "stock":      self.stock,
            "categoria":  self.categoria,
            "disponible": self.stock > 0,
        }