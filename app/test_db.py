
from datetime import date
from decimal import Decimal

from app.repository.database.session import SessionLocal

from app.repository.database.models import (
    Rol,
    Usuario,
    Hotel,
    TipoHabitacion,
    Habitacion,
    Tarifa,
    Reserva,
    Pago
)


def probar_base_datos():

    db = SessionLocal()

    try:
        # 1. Crear roles
        rol = Rol(nombre="propietario")
        db.add(rol)
        db.flush()

        rol_huesped = Rol(nombre="huesped")
        db.add(rol_huesped)
        db.flush()

        # 2. Crear usuarios
        propietario = Usuario(
            nombres="Carlos",
            apellidos="Rodriguez",
            correo="carlos@test.com",
            password_hash="hash_de_prueba",
            rol_id=rol.id
        )

        huesped = Usuario(
            nombres="Maria",
            apellidos="Gonzalez",
            correo="maria@test.com",
            password_hash="hash_de_prueba",
            rol_id=rol_huesped.id
        )

        db.add_all([propietario, huesped])
        db.flush()

        # 3. Crear hotel
        hotel = Hotel(
            nombre="Hotel Central",
            descripcion="Hotel de prueba",
            direccion="Calle 10",
            ciudad="Bucaramanga",
            pais="Colombia",
            propietario_id=propietario.id
        )

        db.add(hotel)
        db.flush()

        # 4. Crear tipo de habitación
        tipo = TipoHabitacion(
            nombre="Doble",
            descripcion="Habitación para dos personas"
        )

        db.add(tipo)
        db.flush()

        # 5. Crear habitación
        habitacion = Habitacion(
            numero="101",
            capacidad=2,
            precio_base=Decimal("150000.00"),
            hotel_id=hotel.id,
            tipo_id=tipo.id
        )

        db.add(habitacion)
        db.flush()

        # 6. Crear tarifa
        tarifa = Tarifa(
            nombre="Temporada normal",
            precio_noche=Decimal("150000.00"),
            moneda="COP",
            fecha_inicio=date(2026, 12, 1),
            fecha_fin=date(2026, 12, 31),
            habitacion_id=habitacion.id
        )

        db.add(tarifa)
        db.flush()

        # 7. Crear reserva
        reserva = Reserva(
            fecha_entrada=date(2026, 12, 5),
            fecha_salida=date(2026, 12, 7),
            huespedes=2,
            total=Decimal("300000.00"),
            usuario_id=huesped.id,
            habitacion_id=habitacion.id
        )

        db.add(reserva)
        db.flush()

        # 8. Crear pago
        pago = Pago(
            monto=Decimal("300000.00"),
            moneda="COP",
            metodo="simulado",
            reserva_id=reserva.id
        )

        db.add(pago)
        db.flush()

        # Comprobar relaciones
        print("\nBASE DE DATOS FUNCIONANDO")
        print("-------------------------")

        print("Hotel:", hotel.nombre)
        print("Propietario:", hotel.propietario.nombres)
        print("Habitación:", habitacion.numero)
        print("Tipo:", habitacion.tipo.nombre)
        print("Tarifa:", habitacion.tarifas[0].precio_noche)
        print("Huésped:", reserva.usuario.nombres)
        print("Reserva:", reserva.id)
        print("Pago:", reserva.pagos[0].monto)

        print("\nTodas las inserciones y relaciones funcionaron.")

        # No conservar los datos de prueba
        db.rollback()

    except Exception as error:
        db.rollback()
        print("Error durante la prueba:", error)
        raise

    finally:
        db.close()


if __name__ == "__main__":
    probar_base_datos()
