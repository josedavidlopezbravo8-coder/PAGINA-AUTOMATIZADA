import os
import tempfile

from fastapi.testclient import TestClient

# Configurar un archivo temporal antes de importar la app
config_file = tempfile.NamedTemporaryFile(delete=False)
os.environ["CONFIG_FILE_PATH"] = config_file.name
config_file.close()

from app.main import app

client = TestClient(app)


def test_read_all_config():
    response = client.get("/config")
    assert response.status_code == 200
    data = response.json()
    assert data["porcentaje_descuento_base"] == 0.05
    assert data["porcentaje_comision"] == 0.1
    assert data["limite_stock_minimo"] == 10
    assert data["error_rate_threshold"] == 0.15


def test_read_specific_parameter():
    response = client.get("/config/porcentaje_comision")
    assert response.status_code == 200
    assert response.json() == {"key": "porcentaje_comision", "value": 0.1}


def test_update_parameter():
    response = client.put("/config/porcentaje_comision", json={"value": 0.12})
    assert response.status_code == 200
    assert response.json() == {"key": "porcentaje_comision", "value": 0.12}

    response = client.get("/config/porcentaje_comision")
    assert response.status_code == 200
    assert response.json()["value"] == 0.12


def test_invalid_parameter_name():
    response = client.put("/config/parametro_inexistente", json={"value": 123})
    assert response.status_code == 404
    assert "Parámetro 'parametro_inexistente' no encontrado" in response.json()["detail"]


def test_invalid_parameter_value():
    response = client.put("/config/porcentaje_comision", json={"value": -0.1})
    assert response.status_code == 400
    assert "Valor inválido" in response.json()["detail"]

    response = client.put("/config/limite_stock_minimo", json={"value": -1})
    assert response.status_code == 400
    assert "Valor inválido" in response.json()["detail"]
