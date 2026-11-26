# ─────────────────────────────────────────────────────────────
# SERVICIO DE HOTELES — HU-016 (CRUD de hoteles)
# ─────────────────────────────────────────────────────────────

from fastapi import HTTPException, status
from sqlalchemy.orm import Session

from app.api.schemas.hotel_schema import HotelCreate, HotelUpdate
from app.repository.database.models import Hotel, Usuario
from app.repository.hotel_repository import HotelRepository
from app.repository.usuario_repository import UsuarioRepository


class HotelService:

    def __init__(self, db: Session):
        self.db = db
        self.repo = HotelRepository(db)
        self.usuarios = UsuarioRepository(db)

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