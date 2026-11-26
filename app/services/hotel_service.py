# ─────────────────────────────────────────────────────────────
# SERVICIO DE HOTELES — HU-016 (CRUD de hoteles)
# ─────────────────────────────────────────────────────────────

from datetime import date

from fastapi import HTTPException, status
from sqlalchemy.orm import Session

from app.api.schemas.hotel_schema import HotelCreate, HotelUpdate
from app.domain.disponibilidad import hay_conflicto
from app.repository.database.models import Hotel, Usuario
from app.repository.habitacion_repository import HabitacionRepository
from app.repository.hotel_repository import HotelRepository
from app.repository.usuario_repository import UsuarioRepository


class HotelService:

    def __init__(self, db: Session):
        self.db = db
        self.repo = HotelRepository(db)
        self.usuarios = UsuarioRepository(db)
        self.habitaciones = HabitacionRepository(db)

    # ── Consultas ───────────────────────────────────────────
    def listar(
        self,
        ciudad: str | None = None,
        pais: str | None = None,
        nombre: str | None = None,
        incluir_inactivos: bool = False
    ) -> list[Hotel]:
        return self.repo.list_filtrado(
            ciudad=ciudad,
            pais=pais,
            nombre=nombre,
            incluir_inactivos=incluir_inactivos
        )

    def obtener(self, hotel_id: int, incluir_inactivo: bool = False) -> Hotel:
        hotel = self.repo.get_by_id(hotel_id)
        if not hotel or (not hotel.activo and not incluir_inactivo):
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Hotel no encontrado"
            )
        return hotel

    # ── Crear ───────────────────────────────────────────────
    def crear(self, data: HotelCreate) -> Hotel:
        # Validar y resolver el propietario
        propietario = self._resolver_propietario(data.propietario_id)

        hotel = Hotel(
            nombre=data.nombre.strip(),
            descripcion=data.descripcion,
            direccion=data.direccion.strip(),
            ciudad=data.ciudad.strip().title(),
            pais=data.pais.strip().title(),
            telefono=data.telefono,
            activo=True,
            propietario_id=propietario.id
        )
        self.repo.add(hotel)
        self.repo.commit()
        self.repo.flush()
        return hotel

    # ── Actualizar ──────────────────────────────────────────
    def actualizar(self, hotel_id: int, data: HotelUpdate) -> Hotel:
        hotel = self.obtener(hotel_id, incluir_inactivo=True)
        cambios = data.model_dump(exclude_unset=True)

        # Si se está cambiando el propietario, validar el nuevo propietario
        if "propietario_id" in cambios and cambios["propietario_id"] is not None:
            nuevo_propietario = self._resolver_propietario(cambios["propietario_id"])
            # Si el propietario_id cambió, lo removemos de los cambios para que no se establezca como atributo directo
            # ya que el modelo Hotel tiene propietario_id como columna, pero la lógica de negocio
            # ya se encargó de validarlo y asignarlo
            cambios.pop("propietario_id")

        for campo, valor in cambios.items():
            if valor is None and campo != "descripcion":
                continue
            if isinstance(valor, str):
                valor = valor.strip()
                if campo in ("nombre", "ciudad", "pais"):
                    valor = valor.title()
            setattr(hotel, campo, valor)

        self.repo.commit()
        self.repo.flush()
        return hotel

    # ── Eliminar (borrado lógico) ───────────────────────────
    def eliminar(self, hotel_id: int) -> Hotel:
        hotel = self.obtener(hotel_id, incluir_inactivo=True)
        if not hotel.activo:
            raise HTTPException(
                status_code=status.HTTP_409_CONFLICT,
                detail="El hotel ya está desactivado"
            )
        hotel.activo = False
        self.repo.commit()
        self.repo.flush()
        return hotel

    # ── Auxiliares ──────────────────────────────────────────
    def _resolver_propietario(self, propietario_id: int | None) -> Usuario:
        if propietario_id:
            propietario = self.usuarios.get_by_id(propietario_id)
            if not propietario:
                raise HTTPException(
                    status_code=status.HTTP_404_NOT_FOUND,
                    detail="El propietario indicado no existe"
                )
            # Validar que el usuario tenga rol de propietario y esté activo
            if propietario.rol.nombre != "propietario" or not propietario.activo:
                raise HTTPException(
                    status_code=status.HTTP_400_BAD_REQUEST,
                    detail="El usuario indicado no tiene rol de propietario o está inactivo"
                )
            return propietario
        else:
            # Si no se envía propietario_id, obtener el primero activo
            propietarios = self.usuarios.list_all(
                activo=True, rol="propietario", limit=1
            )
            if not propietarios:
                raise HTTPException(
                    status_code=status.HTTP_400_BAD_REQUEST,
                    detail=(
                        "No hay usuarios con rol 'propietario' activo; "
                        "crea uno primero o envía propietario_id"
                    )
                )
            return propietarios[0]

    # ── HU-031: buscar alojamiento ──────────────────────────
    def buscar_hoteles(
        self,
        destino: str,
        fecha_entrada: date | None = None,
        fecha_salida: date | None = None,
        huespedes: int = 1,
        page: int = 1,
        page_size: int = 10,
    ) -> tuple[list[Hotel], int]:
        destino = (destino or "").strip()
        if not destino:
            raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="El parámetro destino es obligatorio")

        if huespedes < 1:
            raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="El número de huéspedes debe ser un entero positivo")

        if (fecha_entrada is None) != (fecha_salida is None):
            raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Debe enviar fecha_entrada y fecha_salida juntas")

        if fecha_entrada and fecha_salida and fecha_salida <= fecha_entrada:
            raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="La fecha de salida debe ser posterior a la fecha de entrada")

        if page < 1:
            raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="La página debe ser mayor o igual a 1")
        if page_size < 1 or page_size > 100:
            raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="page_size debe estar entre 1 y 100")

        q = self.db.query(Hotel).filter(Hotel.activo == True)
        like = f"%{destino}%"
        q = q.filter((Hotel.ciudad.ilike(like)) | (Hotel.nombre.ilike(like)) | (Hotel.pais.ilike(like)))

        total = q.count()
        items = q.order_by(Hotel.id.asc()).offset((page - 1) * page_size).limit(page_size).all()
        return items, total

    # ── HU-033: consultar disponibilidad por hotel ──────────
    def consultar_disponibilidad(
        self,
        hotel_id: int,
        fecha_entrada: date,
        fecha_salida: date,
        huespedes: int,
    ) -> list[dict]:
        if fecha_salida <= fecha_entrada:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="La fecha de salida debe ser posterior a la fecha de entrada",
            )
        if huespedes < 1:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="El número de huéspedes debe ser mayor a 0",
            )

        hotel = self.repo.get_by_id(hotel_id)
        if not hotel or not hotel.activo:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Hotel no encontrado",
            )

        habitaciones = self.habitaciones.list_by_hotel(hotel_id, incluir_todos=False)
        if not any(hab.capacidad >= huespedes for hab in habitaciones):
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Cupo inválido: ninguna habitación del hotel admite la cantidad de huéspedes solicitada",
            )

        disponibles = []
        for hab in habitaciones:
            if hab.estado != "disponible":
                continue
            if hab.capacidad < huespedes:
                continue
            solapadas = self.habitaciones.reservas_solapadas(hab.id, fecha_entrada, fecha_salida)
            if hay_conflicto(fecha_entrada, fecha_salida, solapadas):
                continue
            disponibles.append(
                {
                    "id": hab.id,
                    "tipo": hab.tipo.nombre if hab.tipo else "",
                    "capacidad": hab.capacidad,
                    "tarifa_noche": hab.precio_base,
                }
            )
        if not disponibles:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="No hay habitaciones disponibles para las fechas y huéspedes solicitados",
            )
        return disponibles