from fastapi import FastAPI, HTTPException, Depends
from sqlalchemy.orm import Session
from base_rpg import Personaje, Mision, MisionPersonaje, ColaMisiones
from db import SessionLocal, init_db
from contextlib import asynccontextmanager

#? para iniciar la API:
#*uvicorn api:app --reload


@asynccontextmanager
async def lifespan(app: FastAPI):
    init_db()  # Inicializa la DB en el arranque
    yield

app = FastAPI(lifespan=lifespan)

def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

@app.post("/personajes")
def crear_personaje(nombre: str, db: Session = Depends(get_db)):
    nuevo = Personaje(nombre=nombre)
    db.add(nuevo)
    db.commit()
    db.refresh(nuevo)
    return nuevo

@app.post("/misiones")
def crear_mision(nombre: str, descripcion: str, experiencia: int, db: Session = Depends(get_db)):
    nueva = Mision(
        nombre=nombre,
        descripcion=descripcion,
        experiencia_otorgada=experiencia,
        estado="pendiente"
    )
    db.add(nueva)
    db.commit()
    db.refresh(nueva)
    return nueva

@app.post("/personajes/{personaje_id}/misiones/{mision_id}")
def aceptar_mision(personaje_id: int, mision_id: int, db: Session = Depends(get_db)):
    personaje = db.get(Personaje, personaje_id)
    if not personaje:
        raise HTTPException(status_code=404, detail="Personaje no encontrado")

    cola = ColaMisiones(personaje)
    nueva = cola.enqueue(mision_id)

    db.add(nueva)
    db.commit()
    return {"msg": "Misión encolada"}

@app.post("/personajes/{personaje_id}/completar")
def completar_mision(personaje_id: int, db: Session = Depends(get_db)):
    personaje = db.get(Personaje, personaje_id)
    if not personaje:
        raise HTTPException(status_code=404, detail="Personaje no encontrado")

    cola = ColaMisiones(personaje)
    primera = cola.dequeue()

    if not primera:
        raise HTTPException(status_code=400, detail="No hay misiones")

    mision = db.get(Mision, primera.mision_id)
    mision.estado = "completada"
    personaje.experiencia += mision.experiencia_otorgada

    db.delete(primera)
    db.commit()

    return {"msg": f"Misión completada. XP ganada: {mision.experiencia_otorgada}"}

@app.get("/personajes/{personaje_id}/misiones")
def listar_misiones(personaje_id: int, db: Session = Depends(get_db)):
    personaje = db.get(Personaje, personaje_id)
    if not personaje:
        raise HTTPException(status_code=404, detail="Personaje no encontrado")

    misiones = sorted(personaje.misiones, key=lambda mp: mp.orden)
    resultado = [{"id": mp.mision.id, "nombre": mp.mision.nombre, "orden": mp.orden} for mp in misiones]

    return resultado

@app.get("/misiones")
def listar_misiones(db: Session = Depends(get_db)):
    misiones = db.query(Mision).all()
    resultado = [{"id": m.id, "nombre": m.nombre, "descripcion": m.descripcion, "experiencia_otorgada": m.experiencia_otorgada, "estado": m.estado} for m in misiones]
    return resultado