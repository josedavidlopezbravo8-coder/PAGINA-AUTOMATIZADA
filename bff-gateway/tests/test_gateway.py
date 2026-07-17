from fastapi.testclient import TestClient
from app.main import app

client = TestClient(app)


def test_health():
    r = client.get("/health")
    assert r.status_code == 200
    data = r.json()
    assert data["status"] == "ok"
    assert "routes" in data
    assert "quality" in data["routes"]


def test_unknown_service_returns_404():
    r = client.get("/api/servicio-inexistente/ruta")
    assert r.status_code == 404
    assert "no registrado" in r.json()["detail"]


def test_unavailable_service_returns_503():
    # catalog-service no está en este proyecto → 503 controlado
    r = client.get("/api/catalog/books/")
    assert r.status_code == 503
    assert "no disponible" in r.json()["detail"]


def test_unavailable_inventory_returns_503():
    r = client.get("/api/inventory/")
    assert r.status_code == 503
