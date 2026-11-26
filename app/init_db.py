import sys
from pathlib import Path

# Permite ejecutar el archivo directamente: python app/init_db.py
sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

from app.repository.database.base import Base
from app.repository.database.session import engine

# Importamos los modelos para registrarlos en SQLAlchemy
import app.repository.database.models

def init_db():
    Base.metadata.create_all(bind=engine)

    print("Base de datos creada correctamente.")

    print("\nTablas registradas:")

    for tabla in Base.metadata.sorted_tables:
        print(f"- {tabla.name}")


if __name__ == "__main__":
    init_db()
