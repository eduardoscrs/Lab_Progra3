# db.py
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from base_rpg import Base  #? Trae los modelos de base_rpg.py

DATABASE_URL = "sqlite:///./rpg.db"  # Archivo .db local

engine = create_engine(
    DATABASE_URL, connect_args={"check_same_thread": False}
)

SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

# Crear las tablas si no existen
def init_db():
    Base.metadata.create_all(bind=engine)


# Crear la base de datos y las tablas si no existen
# así como la sesión de la base de datos
# para que no de error al importar el módulo