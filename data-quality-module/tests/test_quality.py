from fastapi.testclient import TestClient
from app.main import app

client = TestClient(app)


def test_health():
    r = client.get("/quality/health")
    assert r.status_code == 200
    assert r.json()["status"] == "ok"


def test_summary_uses_mock_fallback():
    # inventory-service no corre en tests → usa datos mock automáticamente
    r = client.get("/quality/summary")
    assert r.status_code == 200
    data = r.json()
    assert "total_batches" in data
    assert data["total_batches"] > 0
    assert isinstance(data["batches"], list)


def test_list_batches_fallback():
    r = client.get("/quality/batches")
    assert r.status_code == 200
    batches = r.json()
    assert isinstance(batches, list)
    assert len(batches) > 0
    assert "batch_id" in batches[0]
    assert "error_rate" in batches[0]


def test_batch_report_fallback():
    r = client.get("/quality/batches/1/report")
    assert r.status_code == 200
    data = r.json()
    assert data["batch_id"] == 1
    assert "errors" in data
    assert isinstance(data["errors"], list)
    assert len(data["errors"]) > 0


def test_batch_not_found():
    r = client.get("/quality/batches/9999/report")
    assert r.status_code == 404
    assert "detail" in r.json()
