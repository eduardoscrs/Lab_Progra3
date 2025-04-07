from fastapi import FastAPI, HTTPException, Depends
from sqlalchemy.orm import Session
from base_rpg import Personaje, Mision, MisionPersonaje, ColaMisiones
from db import SessionLocal, init_db


#api para el juego de rol
# Inicializa la base de datos y las tablas


app = FastAPI()

@app.on_event("startup")
def on_startup():
    init_db()


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
    personaje = db.query(Personaje).get(personaje_id)
    if not personaje:
        raise HTTPException(status_code=404, detail="Personaje no encontrado")

    cola = ColaMisiones(personaje)
    nueva = cola.enqueue(mision_id)

    db.add(nueva)
    db.commit()
    return {"msg": "Misión encolada"}

@app.post("/personajes/{personaje_id}/completar")
def completar_mision(personaje_id: int, db: Session = Depends(get_db)):
    personaje = db.query(Personaje).get(personaje_id)
    if not personaje:
        raise HTTPException(status_code=404, detail="Personaje no encontrado")

    cola = ColaMisiones(personaje)
    primera = cola.dequeue()

    if not primera:
        raise HTTPException(status_code=400, detail="No hay misiones")

    mision = db.query(Mision).get(primera.mision_id)
    mision.estado = "completada"
    personaje.experiencia += mision.experiencia_otorgada  

    db.delete(primera)  
    db.commit()

    return {"msg": f"Misión completada. XP ganada: {mision.experiencia_otorgada}"}

@app.get("/personajes/{personaje_id}/misiones")
def listar_misiones(personaje_id: int, db: Session = Depends(get_db)):
    personaje = db.query(Personaje).get(personaje_id)
    if not personaje:
        raise HTTPException(status_code=404, detail="Personaje no encontrado")

    misiones = sorted(personaje.misiones, key=lambda mp: mp.orden)
    resultado = [{"id": mp.mision.id, "nombre": mp.mision.nombre, "orden": mp.orden} for mp in misiones]

    return resultado


@app.get("/personajes")
def listar_personajes(db: Session = Depends(get_db)):
    personajes = db.query(Personaje).all()
    return personajes

