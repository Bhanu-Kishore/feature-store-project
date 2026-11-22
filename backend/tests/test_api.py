import pytest
from fastapi.testclient import TestClient

from app import app

KNOWN_CUSTOMER = "7590-VHVEG"
KNOWN_FEATURES = {
    "tenure": 1,
    "monthly_charges": 29.85,
    "total_charges": 29.85,
    "senior_citizen": 0,
}


@pytest.fixture(scope="session")
def client():
    with TestClient(app) as test_client:
        yield test_client


def test_root(client):
    response = client.get("/")
    assert response.status_code == 200
    assert "running" in response.json()["message"]


def test_health(client):
    response = client.get("/health")
    assert response.status_code == 200
    assert response.json()["status"] == "ok"


def test_docs_available(client):
    assert client.get("/docs").status_code == 200
    schema = client.get("/openapi.json").json()
    assert schema["info"]["title"] == "Customer Churn Prediction API"
    assert "/predict" in schema["paths"]


def test_prediction_uses_feast_online_features(client):
    response = client.post("/predict", json={"customer_id": KNOWN_CUSTOMER})
    assert response.status_code == 200

    body = response.json()
    assert body["customer_id"] == KNOWN_CUSTOMER
    assert body["features"] == KNOWN_FEATURES
    assert body["prediction"] in (0, 1)
    assert 0.0 <= body["churn_probability"] <= 1.0
    assert body["prediction_label"] == (
        "Churn — customer left" if body["prediction"] == 1 else "No churn — customer stayed"
    )


def test_unknown_customer_returns_404(client):
    response = client.post("/predict", json={"customer_id": "NOPE-0000"})
    assert response.status_code == 404
    assert "not found" in response.json()["detail"].lower()


def test_blank_customer_id_returns_422(client):
    response = client.post("/predict", json={"customer_id": "   "})
    assert response.status_code == 422


def test_cors_headers_are_returned(client):
    response = client.get("/health", headers={"Origin": "http://localhost:8080"})
    assert response.status_code == 200
    assert response.headers["access-control-allow-origin"]
