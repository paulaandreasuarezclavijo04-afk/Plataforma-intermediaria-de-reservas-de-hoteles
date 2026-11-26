import os

path = r"C:\Users\Cristofer\Documents\PAULA\Universidad\WebServices\Plataforma intermediaria de reservas de hoteles"
files = [
    "main.py",
    "app/api/routers/hotel_router.py",
    "app/api/schemas/hotel_schema.py",
    "app/services/hotel_service.py",
    "app/repository/hotel_repository.py",
    "app/repository/database/models/hotel.py",
]
for f in files:
    full = os.path.join(path, f)
    status = "EXISTS" if os.path.exists(full) else "MISSING"
    print(f"{f}: {status}")