# ─────────────────────────────────────────────────────────────
# DATOS INICIALES — roles, usuarios de prueba, hotel, habitaciones,
# tarifas y reservas de ejemplo (pasada completada y futura).
#
# Ejecutar desde la raíz del proyecto:
#     python app/seed.py
# ─────────────────────────────────────────────────────────────

import sys
from datetime import date, timedelta
from decimal import Decimal
from pathlib import Path

# Permite ejecutar el archivo directamente: python app/seed.py
sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

# Consolas Windows (cp1252) no soportan emojis/flechas: salida UTF-8
if hasattr(sys.stdout, "reconfigure"):
    sys.stdout.reconfigure(encoding="utf-8", errors="replace")

from app.domain.password import hash_password
from app.repository.database.base import Base
from app.repository.database.models import (
    Habitacion,
    Hotel,
    Pago,
    Reserva,
    Rol,
    Tarifa,
    TipoHabitacion,
    Usuario
)
from app.repository.database.session import SessionLocal, engine


def seed():
    Base.metadata.create_all(bind=engine)
    db = SessionLocal()

    try:
        if db.query(Rol).first():
            print("La base ya tiene datos. Ejecuta 'python app/init_db.py' tras borrar dev.db si quieres regenerarla.")
            return

        # ── Roles ───────────────────────────────────────────
        roles = {
            nombre: Rol(nombre=nombre)
            for nombre in ("admin", "propietario", "huesped")
        }
        db.add_all(roles.values())
        db.flush()

        # ── Usuarios de prueba (password: demo123) ──────────
        admin = Usuario(
            nombres="Ana",
            apellidos="Admin",
            correo="admin@demo.com",
            password_hash=hash_password("demo123"),
            correo_verificado=True,
            activo=True,
            rol_id=roles["admin"].id
        )
        dueno = Usuario(
            nombres="Carlos",
            apellidos="Rodriguez",
            correo="propietario@demo.com",
            password_hash=hash_password("demo123"),
            correo_verificado=True,
            activo=True,
            rol_id=roles["propietario"].id
        )
        huesped = Usuario(
            nombres="Maria",
            apellidos="Gonzalez",
            correo="huesped@demo.com",
            password_hash=hash_password("demo123"),
            correo_verificado=True,
            activo=True,
            rol_id=roles["huesped"].id
        )
        db.add_all([admin, dueno, huesped])
        db.flush()

        # ── Hotel ───────────────────────────────────────────
        hotel = Hotel(
            nombre="Hotel Central",
            descripcion="Hotel de prueba en el centro de Bucaramanga",
            direccion="Calle 10 # 5-20",
            ciudad="Bucaramanga",
            pais="Colombia",
            telefono="6071234567",
            activo=True,
            propietario_id=dueno.id
        )
        db.add(hotel)
        db.flush()

        # ── Tipos y habitaciones ────────────────────────────
        tipo_doble = TipoHabitacion(
            nombre="Doble",
            descripcion="Habitación para dos personas"
        )
        tipo_suite = TipoHabitacion(
            nombre="Suite",
            descripcion="Habitación amplia con sala"
        )
        db.add_all([tipo_doble, tipo_suite])
        db.flush()

        hab_101 = Habitacion(
            numero="101",
            capacidad=2,
            precio_base=Decimal("150000.00"),
            estado="disponible",
            hotel_id=hotel.id,
            tipo_id=tipo_doble.id
        )
        hab_102 = Habitacion(
            numero="102",
            capacidad=4,
            precio_base=Decimal("280000.00"),
            estado="disponible",
            hotel_id=hotel.id,
            tipo_id=tipo_suite.id
        )
        db.add_all([hab_101, hab_102])
        db.flush()

        # ── Tarifas ─────────────────────────────────────────
        hoy = date.today()
        db.add_all([
            Tarifa(
                nombre="Temporada alta",
                precio_noche=Decimal("180000.00"),
                moneda="COP",
                fecha_inicio=hoy + timedelta(days=30),
                fecha_fin=hoy + timedelta(days=90),
                activa=True,
                habitacion_id=hab_101.id
            ),
            Tarifa(
                nombre="Fin de semana",
                precio_noche=Decimal("170000.00"),
                moneda="COP",
                fecha_inicio=hoy,
                fecha_fin=hoy + timedelta(days=29),
                activa=True,
                habitacion_id=hab_101.id
            ),
        ])
        db.flush()

        # ── Reserva PASADA completada (para HU-076) ─────────
        reserva_pasada = Reserva(
            fecha_entrada=hoy - timedelta(days=10),
            fecha_salida=hoy - timedelta(days=7),
            huespedes=2,
            total=Decimal("450000.00"),
            estado="completada",
            usuario_id=huesped.id,
            habitacion_id=hab_101.id
        )
        db.add(reserva_pasada)
        db.flush()

        # ── Reserva FUTURA pendiente (para HU-052 / HU-062) ─
        reserva_futura = Reserva(
            fecha_entrada=hoy + timedelta(days=15),
            fecha_salida=hoy + timedelta(days=18),
            huespedes=2,
            total=Decimal("510000.00"),
            estado="pendiente",
            usuario_id=huesped.id,
            habitacion_id=hab_101.id
        )
        db.add(reserva_futura)
        db.flush()

        # ── Pago pendiente de la reserva futura (HU-062) ────
        db.add(Pago(
            monto=reserva_futura.total,
            moneda="COP",
            metodo="tarjeta",
            estado="pendiente",
            reserva_id=reserva_futura.id
        ))
        db.commit()

        print("Datos iniciales creados correctamente (OK)")
        print("-----------------------------------------")
        print("Usuarios (password: demo123)")
        print("  admin@demo.com       -> admin")
        print("  propietario@demo.com -> propietario")
        print("  huesped@demo.com     -> huesped")
        print(f"Hotel: {hotel.nombre} (id {hotel.id})")
        print(f"Habitaciones: 101 (id {hab_101.id}), 102 (id {hab_102.id})")
        print(f"Reserva completada: id {reserva_pasada.id}")
        print(f"Reserva pendiente:  id {reserva_futura.id}")

    finally:
        db.close()


if __name__ == "__main__":
    seed()
