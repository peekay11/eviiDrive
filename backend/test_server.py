# test_server.py — eviiDrive backend tests
# Date: 21 March 2026

import pytest
from backend import server   # import server as a package module

@pytest.fixture
def client():
    app = server.app
    app.config["TESTING"] = True
    return app.test_client()

def test_home_route(client):
    response = client.get("/")
    assert response.status_code == 200
    assert b"eviiDrive backend is running" in response.data

def test_price_missing_coords(client):
    # No coordinates provided → should return error
    response = client.get("/api/price?city=Johannesburg&car_type=small&passengers=1")
    assert response.status_code in (400, 502)
    data = response.get_json()
    assert "error" in data

def test_price_summary_missing_coords(client):
    response = client.get("/api/price/summary?city=Johannesburg&car_type=small&passengers=1")
    assert response.status_code in (400, 502)
    data = response.get_json()
    assert "error" in data

def test_vehicles(client):
    response = client.get("/api/vehicles")
    assert response.status_code == 200
    data = response.get_json()
    assert isinstance(data, list)
    assert any(v["value"] == "small" for v in data)

def test_suggest_missing_query(client):
    response = client.get("/api/suggest")
    assert response.status_code == 400
    data = response.get_json()
    assert "error" in data
