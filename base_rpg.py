from sqlalchemy import Column, Integer, String, Text, Enum, DateTime, ForeignKey
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func


#! Módulo para el juego de rol
#! Contiene las clases de los modelos y la cola de misiones
#! para el manejo FIFO de las misiones de los personajes

Base = declarative_base()

class Mision(Base): 
    "Representa una misión en el juego"
    __tablename__ = "misiones"
    id = Column(Integer, primary_key=True)
    nombre = Column(String(50), nullable=False)
    descripcion = Column(Text, nullable=True)
    experiencia_otorgada = Column(Integer, nullable=False)  
    estado = Column(Enum('pendiente', 'completada', name='estados'), nullable=False)
    fecha_creacion = Column(DateTime, default=func.now())

    personajes = relationship("MisionPersonaje", back_populates="mision")

class Personaje(Base):
    "Representa un personaje en el juego"
    __tablename__ = "personajes"
    id = Column(Integer, primary_key=True)
    nombre = Column(String(50), nullable=False)
    nivel = Column(Integer, default=1)
    experiencia = Column(Integer, default=0)

    misiones = relationship("MisionPersonaje", back_populates="personaje")

class MisionPersonaje(Base):
    "Tabla intermedia entre misiones y personajes (manejo FIFO)"
    __tablename__ = "misiones_personajes"
    personaje_id = Column(Integer, ForeignKey("personajes.id"), primary_key=True)
    mision_id = Column(Integer, ForeignKey("misiones.id"), primary_key=True)
    orden = Column(Integer)

    personaje = relationship("Personaje", back_populates="misiones")
    mision = relationship("Mision", back_populates="personajes") 

class ColaMisiones:
    def __init__(self, personaje):
        self.personaje = personaje
        self.misiones = sorted(personaje.misiones, key=lambda mp: mp.orden)

    def enqueue(self, mision_id):
        orden_max = max((mp.orden for mp in self.personaje.misiones), default=0)
        nueva_mision = MisionPersonaje(
            personaje_id=self.personaje.id,
            mision_id=mision_id,
            orden=orden_max + 1
        )
        self.misiones.append(nueva_mision) 
        return nueva_mision

    def dequeue(self):
        if self.is_empty():
            return None
        return self.misiones.pop(0)

    def first(self):
        return None if self.is_empty() else self.misiones[0]

    def is_empty(self):
        return len(self.misiones) == 0

    def size(self):
        return len(self.misiones)


if __name__ == "__main__":
    from db import engine
    Base.metadata.create_all(bind=engine)
    print("Tablas creadas correctamente.")
