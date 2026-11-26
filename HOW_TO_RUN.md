# HU-016 Hotel CRUD - How to Run

## Prerequisites
- Python 3.13 installed
- Virtual environment activated (`.\\venv\\Scripts\\activate`)

## Step 1: Start the Server

Open a Command Prompt (cmd) and run:

```cmd
cd C:\Users\Cristofer\Documents\PAULA\Universidad\WebServices\Plataforma intermediaria de reservas de hoteles
python main.py
```

Or alternatively:
```cmd
python -m uvicorn main:app --reload --host 0.0.0.0 --port 8000
```

You should see:
```
INFO:     Will watch for changes in these directories: ['...']
INFO:     Uvicorn running on http://127.0.0.1:8000 (Press CTRL+C to quit)
```

## Step 2: Test the Endpoints

Once the server is running (you see the message above), test these URLs in your browser or with curl:

### Health Check
```
GET http://127.0.0.1:8000/health
# Expected: {"status":"healthy"}
```

### List Hotels (HU-016)
```
GET http://127.0.0.1:8000/api/hoteles
# Expected: Array of hotels (empty initially, or with seed data)
```

### Create Hotel
```
POST http://127.0.0.1:8000/api/hoteles
# Body (JSON): {"nombre":"Hotel Test","ciudad":"Bogotá","pais":"Colombia"}
# Expected: 201 Created with hotel object
```

### Get Hotel by ID
```
GET http://127.0.0.1:8000/api/hoteles/1
# Expected: Hotel object or 404 if not found
```

### Update Hotel
```
PUT http://127.0.0.1:8000/api/hoteles/1
# Body (JSON): {"nombre":"Hotel Actualizado"}
# Expected: Updated hotel object
```

### Soft Delete Hotel
```
DELETE http://127.0.0.1:8000/api/hoteles/1
# Expected: Deactivated hotel object (activo=False)
```

## Step 3: Verify Endpoints Work

Test sequentially:

1. **Start server**: `python main.py`
2. **Check health**: `curl http://127.0.0.1:8000/health`
   - Should return: `{"status":"healthy"}`
3. **List hotels**: `curl http://127.0.0.1:8000/api/hoteles`
   - Should return: `[]` (empty list initially)
4. **Create hotel**: 
   ```cmd
   curl -X POST http://127.0.0.1:8000/api/hoteles ^
      -H "Content-Type: application/json" ^
      -d "{\"nombre\":\"Hotel Test\",\"ciudad\":\"Bogotá\",\"pais\":\"Colombia\"}"
   ```
   - Should return: Hotel object with id, 201 status
5. **List again**: `curl http://127.0.0.1:8000/api/hoteles?nombre=Hotel%20Test`
   - Should return: The hotel you just created
6. **Get by ID**: `curl http://127.0.0.1:8000/api/hoteles/1`
   - Should return: The created hotel
7. **Update**: `curl -X PUT http://127.0.0.1:8000/api/hoteles/1 -H "Content-Type: application/json" -d "{\"nombre\":\"Hotel Actualizado\"}"`
   - Should return: Updated hotel
8. **Delete**: `curl -X DELETE http://127.0.0.1:8000/api/hoteles/1`
   - Should return: Hotel with activo=False

## Common Issues & fixes

### Issue: "ModuleNotFoundError: No module named 'fastapi'"
**Fix**: Make sure your virtual environment is activated:
```cmd
.\venv\Scripts\activate
```

### Issue: "NameError: name 'get_db' is not defined"
**Fix**: This was fixed in main.py - ensure you're using the updated main.py that only includes hotel_router.

### Issue: Port 8000 already in use
**Fix**: Kill any existing process on port 8000, or change the port in main.py.

### Issue: CORS errors
**Fix**: The main.py includes `CORSMiddleware` with `allow_origins=["*"]`, so this should not be an issue.

## Project Structure (HU-016 only)

```
main.py                          → Entry point (only hotel router)
app/api/routers/hotel_router.py  → CRUD endpoints (GET, POST, PUT, DELETE)
app/api/schemas/hotel_schema.py  → HotelCreate, HotelUpdate, HotelResponse
app/services/hotel_service.py    → Business logic
app/repository/hotel_repository.py→ Data access
app/repository/database/models/hotel.py → SQLAlchemy model
```

## What's NOT Included (HU-016 only)

- ❌ Authentication (auth, JWT, login)
- ❌ User management (usuarios)
- ❌ Rooms/habitaciones
- ❌ Reservations (reservas)
- ❌ Payments (pagos)
- ❌ Evaluations (evaluaciones)
- ❌ Assistance (asistencias)
- ❌ Graphical interface (interface.html)
- ❌ Search/alojamientos
- ❌ Other routers, schemas, services, repositories

The project is now focused exclusively on HU-016: CRUD de Hoteles.