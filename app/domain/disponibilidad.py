# ─────────────────────────────────────────────────────────────
# CAPA DOMINIO — reglas puras de disponibilidad y tarifas
# No importa FastAPI ni SQLAlchemy: solo fechas y números.
# ─────────────────────────────────────────────────────────────

from datetime import date, timedelta
from decimal import Decimal, ROUND_HALF_UP
from typing import Iterable, Sequence


# Estados de reserva que OCUPAN una habitación
ESTADOS_QUE_OCUPAN = ("pendiente", "confirmada", "pagada")


def noches(entrada: date, salida: date) -> int:
    """Cantidad de noches entre dos fechas (entrada, salida)."""
    return (salida - entrada).days


def hay_solape(
    inicio_a: date, fin_a: date,
    inicio_b: date, fin_b: date
) -> bool:
    """
    Dos estancias se solapan si comparten al menos una noche.
    Las estancias se tratan como intervalos semiabiertos [entrada, salida):
    una reserva que sale el día X permite entrar otro ese mismo día X.
    """
    return inicio_a < fin_b and inicio_b < fin_a


def hay_conflicto(
    entrada: date,
    salida: date,
    reservas_existentes: Iterable[tuple[date, date]]
) -> bool:
    """¿Existe alguna reserva previa que solape con las fechas dadas?"""
    for otra_entrada, otra_salida in reservas_existentes:
        if hay_solape(entrada, salida, otra_entrada, otra_salida):
            return True
    return False


def precio_de_noche(
    precio_base,
    tarifas: Sequence,
    dia: date
) -> Decimal:
    """
    Precio de una noche: si hay tarifa ACTIVA que cubre la fecha,
    se usa la tarifa; si no, el precio_base de la habitación.
    """
    for tarifa in tarifas:
        if not tarifa.activa:
            continue
        if tarifa.fecha_inicio <= dia <= tarifa.fecha_fin:
            return Decimal(tarifa.precio_noche)
    return Decimal(precio_base)


def calcular_total(
    precio_base,
    tarifas: Sequence,
    entrada: date,
    salida: date
) -> tuple[Decimal, list[dict]]:
    """
    Total de la estancia noche a noche + desglose por fecha.
    REGLA DE NEGOCIO: el total siempre se redondea a 2 decimales.
    """
    total = Decimal("0.00")
    desglose: list[dict] = []

    dia = entrada
    while dia < salida:
        precio = precio_de_noche(precio_base, tarifas, dia)
        total += precio
        desglose.append({
            "fecha": dia.isoformat(),
            "precio": str(precio),
        })
        dia = dia + timedelta(days=1)

    total = total.quantize(Decimal("0.01"), rounding=ROUND_HALF_UP)
    return total, desglose
