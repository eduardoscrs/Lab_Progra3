import pytest
from fastapi.testclient import TestClient
from api import app
from db import init_db

#* Ejecutar el test para ver cómo funciona el FIFO:
#* pytest -s test.py

client = TestClient(app)

@pytest.fixture(autouse=True)
def setup():
    print("🔄 Inicializando base de datos...")
    init_db()

def test_fifo_misiones():
    print("🧪 Iniciando test de misiones FIFO")

    # 1. Crear personaje
    print("👤 Creando personaje...")
    res = client.post("/personajes", params={"nombre": "TestHero"})
    personaje = res.json()
    print("✅ Personaje creado:", personaje)
    personaje_id = personaje["id"]

    # 2. Crear misiones
    print("🛠️ Creando misiones...")
    ids_misiones = []
    for nombre in ["Primera", "Segunda", "Tercera"]:
        res = client.post("/misiones", params={
            "nombre": nombre,
            "descripcion": f"Misión {nombre}",
            "experiencia": 10
        })
        mid = res.json()["id"]
        ids_misiones.append(mid)
        print(f"  ➕ Misión '{nombre}' creada con ID {mid}")

    # 3. Encolar misiones al personaje
    print("📥 Encolando misiones...")
    for mid in ids_misiones:
        res = client.post(f"/personajes/{personaje_id}/misiones/{mid}")
        print(f"  🔁 Misión {mid} encolada - Respuesta: {res.json()}")

    # 4. Verificar orden de la cola
    print("🔍 Verificando orden de la cola...")
    res = client.get(f"/personajes/{personaje_id}/misiones")
    cola = res.json()
    print("📋 Cola actual:", [m["nombre"] for m in cola])
    assert [m["nombre"] for m in cola] == ["Primera", "Segunda", "Tercera"]

    # 5. Completar una misión (debería ser la primera)
    print("✅ Completando primera misión...")
    res = client.post(f"/personajes/{personaje_id}/completar")
    print("📤 Respuesta:", res.json())
    assert res.json()["msg"].startswith("Misión completada")

    # 6. Verificar que la misión completada fue la primera
    print("🔁 Verificando cola después de completar una misión...")
    res = client.get(f"/personajes/{personaje_id}/misiones")
    cola_post = res.json()
    print("📋 Cola actual después:", [m["nombre"] for m in cola_post])
    assert [m["nombre"] for m in cola_post] == ["Segunda", "Tercera"]

    print("✅ Test FIFO completado correctamente.")
