# Plataforma-intermediaria-de-reservas-de-hoteles

API REST de una plataforma intermediaria de reservas de hoteles (huéspedes ↔ hoteles).
Desarrollada con **FastAPI + SQLAlchemy + SQLite** siguiendo una **arquitectura de capas**.

Proyecto de la asignatura **Web Services** — Parcial 2 (15 historias de usuario).

---

## Arquitectura de capas

```
main.py                     → Punto de entrada: crea la app y registra los routers
app/
├── api/
│   ├── routers/            → Endpoints (HTTP) por módulo
│   ├── schemas/            → Contratos de entrada/salida (Pydantic)
│   └── dependencies/       → Dependencias transversales
├── services/               → Lógica de negocio (reglas, validaciones, estados)
├── repository/             → Acceso a datos (SQLAlchemy)
│   └── database/models/    → Modelos/entidades de la BD
└── domain/                 → Reglas puras: disponibilidad, tarifas, contraseñas
```

Flujo de una petición: **router → service → repository → model**, y de vuelta
**model → schema → respuesta**.

---

## Puesta en marcha

```bash
# 1. Crear la base de datos (12 tablas)
python app/init_db.py

# 2. Cargar datos de prueba
python app/seed.py

# 3. Arrancar el servidor
python main.py            # o: python -m uvicorn main:app --reload
```

Documentación interactiva: <http://127.0.0.1:8000/docs>

### Datos de prueba (contraseña: `demo123`)

| Correo | Rol |
|---|---|
| `admin@demo.com` | admin |
| `propietario@demo.com` | propietario (Hotel Central) |
| `huesped@demo.com` | huésped (con reserva completada y reserva pendiente) |

---

## Endpoints por historia de usuario

| HU | Método | Endpoint | Descripción |
|---|---|---|---|
| **HU-001** | GET/POST | `/api/usuarios` | Listar / crear usuarios |
| | GET/PUT/DELETE | `/api/usuarios/{id}` | Consultar / actualizar / desactivar |
| **HU-011** | POST | `/api/auth/login` | Iniciar sesión |
| **HU-001/002** | POST | `/api/auth/registro` | Registro + token de verificación |
| **HU-002** | POST | `/api/auth/solicitar-verificacion` | Enviar token de verificación |
| | POST | `/api/auth/validar-correo` | Confirmar correo con el token |
| **HU-005** | POST | `/api/auth/recuperar-password` | Solicitar recuperación |
| | POST | `/api/auth/restablecer-password` | Cambiar contraseña con token |
| **HU-016** | GET/POST | `/api/hoteles` | Buscar / crear hoteles |
| | GET/PUT/DELETE | `/api/hoteles/{id}` | Consultar / actualizar / desactivar |
| **HU-021** | GET/POST | `/api/habitaciones?hotel_id=` | Listar / crear habitaciones |
| | GET/PUT/DELETE | `/api/habitaciones/{id}` | Consultar / actualizar / eliminar |
| | GET/POST | `/api/habitaciones/tipos` | Tipos de habitación |
| | GET/POST | `/api/habitaciones/{id}/tarifas` | Tarifas de una habitación |
| | PUT/DELETE | `/api/habitaciones/tarifas/{id}` | Modificar / eliminar tarifa |
| **HU-031** | GET | `/api/alojamientos/buscar` | Buscar por ciudad, fechas, huéspedes, precio, tipo |
| **HU-033** | GET | `/api/alojamientos/disponibilidad/{id}` | Disponibilidad + desglose del precio |
| **HU-036** | POST | `/api/reservas` | Crear reserva (con control de doble reserva) |
| **HU-039** | GET | `/api/reservas` | Filtrar por usuario, hotel o estado |
| | GET | `/api/reservas/{id}` | Detalle con pagos y confirmación |
| **HU-068** | POST | `/api/reservas/{id}/confirmar` | Confirmar y notificar |
| | GET | `/api/reservas/{id}/confirmacion` | Consultar confirmación enviada |
| | POST | `/api/reservas/{id}/cancelar` | Cancelar (reembolso automático) |
| | POST | `/api/reservas/{id}/completar` | Marcar estancia completada |
| **HU-062** | POST | `/api/pagos` | Solicitud de pago de una reserva |
| **HU-052** | POST | `/api/pagos/{id}/procesar` | Procesar pago (pasarela simulada) |
| | POST | `/api/pagos/{id}/reembolso` | Reembolsar pago de reserva cancelada |
| | GET | `/api/pagos?reserva_id=` | Pagos de una reserva |
| **HU-076** | GET/POST | `/api/evaluaciones` | Listar / crear evaluaciones |
| | GET/PUT/DELETE | `/api/evaluaciones/{id}` | Consultar / actualizar / eliminar |
| | GET | `/api/evaluaciones/hotel/{id}` | Evaluaciones de un hotel |
| | GET | `/api/evaluaciones/hotel/{id}/resumen` | Promedio y distribución |
| | POST | `/api/evaluaciones/{id}/respuesta` | Respuesta del hotel |
| **HU-092** | GET/POST | `/api/asistencias` | Listar / crear solicitudes |
| | GET | `/api/asistencias/{id}` | Consultar solicitud |
| | PATCH | `/api/asistencias/{id}/estado` | Responder / cerrar solicitud |

---

## Reglas de negocio implementadas

1. **Disponibilidad (HU-033/036):** dos estancias se solapan si comparten al menos
   una noche (`[entrada, salida)`). La verificación y el alta de la reserva ocurren en
   la **misma transacción con lock**, para impedir que dos usuarios reserven la misma
   habitación en las mismas fechas → `409 Conflict`.
2. **Tarifas:** el total se calcula **noche a noche**: si hay tarifa activa que cubre
   la fecha se usa la tarifa; si no, el `precio_base`. Redondeo a 2 decimales.
3. **Estados de reserva:** `pendiente → confirmada → completada` o `cancelada`.
   - Confirmar se hace al pagar o con `POST /reservas/{id}/confirmar` (HU-068).
   - `completar` exige que ya pasó la fecha de salida → habilita la evaluación.
   - Al cancelar, los pagos realizados pasan a `reembolsado` automáticamente.
4. **Pagos (HU-052):** pasarela **simulada**; tarjeta terminada en `0000` → `402`.
   Un pago exitoso confirma la reserva y genera la notificación de confirmación.
5. **Evaluaciones (HU-076):** solo reservas **completadas**, **una por reserva**,
   puntuación 1–5, con promedio público y respuesta del hotel.
6. **Asistencia (HU-092):** ciclo `abierta → en_proceso → respondida → cerrada`;
   responder exige el texto de respuesta; cerrar registra la fecha.
7. **Usuarios:** correo único e inválido → `409/422`, contraseñas con **PBKDF2 + salt**,
   borrado lógico (`activo = false`).
8. **Hoteles:** borrado lógico; una habitación solo se elimina si no tiene reservas.

---

## Notas

- **Autorización pendiente (v2):** por ahora todos los endpoints están abiertos y las
  operaciones que requieren usuario envían `usuario_id` / `propietario_id` en el
  cuerpo. La capa **JWT + roles** se agregará en una segunda pasada.
- **Correos simulados:** no se envían correos reales; cada mensaje (verificación,
  recuperación, confirmación) queda registrado en la tabla `notificaciones`.
- **Pasarela de pagos:** simulada, sin integración real de terceros.
