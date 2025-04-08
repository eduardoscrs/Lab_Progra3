import pytest
import logging
from fastapi.testclient import TestClient
from api import app
from db import init_db

# Configuración del logger
logging.basicConfig(level=logging.INFO, format="%(asctime)s - %(levelname)s - %(message)s")
logger = logging.getLogger(__name__)


#pytest -s --log-cli-level=INFO test.py (este si los muestra bien xd)
#pytest -s -o log_cli_level=INFO test.py

client = TestClient(app)

@pytest.fixture(autouse=True)
def setup():
    logger.info("🔄 Inicializando base de datos...")
    init_db()

def test_fifo_misiones():
    logger.info("🧪 Iniciando test de misiones FIFO")

    # 1. Crear personaje
    logger.info("👤 Creando personaje...")
    res = client.post("/personajes", params={"nombre": "HeroCaro"})
    personaje = res.json()
    logger.info("✅ Personaje creado: %s", personaje)
    personaje_id = personaje["id"]

    # 2. Crear misiones
    logger.info("🛠️ Creando misiones...")
    ids_misiones = []
    for nombre in ["Primera", "Segunda", "Tercera"]:
        res = client.post("/misiones", params={
            "nombre": nombre,
            "descripcion": f"Misión {nombre}",
            "experiencia": 10
        })
        mid = res.json()["id"]
        ids_misiones.append(mid)
        logger.info("  ➕ Misión '%s' creada con ID %s", nombre, mid)

    # 3. Encolar misiones al personaje
    logger.info("📥 Encolando misiones...")
    for mid in ids_misiones:
        res = client.post(f"/personajes/{personaje_id}/misiones/{mid}")
        logger.info("  🔁 Misión %s encolada - Respuesta: %s", mid, res.json())

    # 4. Verificar orden de la cola
    logger.info("🔍 Verificando orden de la cola...")
    res = client.get(f"/personajes/{personaje_id}/misiones")
    cola = res.json()
    logger.info("📋 Cola actual: %s", [m["nombre"] for m in cola])
    assert [m["nombre"] for m in cola] == ["Primera", "Segunda", "Tercera"]

    # 5. Completar una misión (debería ser la primera)
    logger.info("✅ Completando primera misión...")
    res = client.post(f"/personajes/{personaje_id}/completar")
    logger.info("📤 Respuesta: %s", res.json())
    assert res.json()["msg"].startswith("Misión completada")

    # 6. Verificar que la misión completada fue la primera
    logger.info("🔁 Verificando cola después de completar una misión...")
    res = client.get(f"/personajes/{personaje_id}/misiones")
    cola_post = res.json()
    logger.info("📋 Cola actual después: %s", [m["nombre"] for m in cola_post])
    assert [m["nombre"] for m in cola_post] == ["Segunda", "Tercera"]

    logger.info("✅ Test FIFO completado correctamente.")
