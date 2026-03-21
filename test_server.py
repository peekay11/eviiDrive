import pytest
from server import app

@pytest.fixture
def client():
    app.testing = True
    with app.test_client() as client:
        yield client

class TestHomeEndpoint:
    def test_home_ok(self, client):
        response = client.get("/")
        assert response.status_code == 200
        assert b"eviiDrive server is running" in response.data

class TestPriceEndpoint:
    def test_missing_coords(self, client):
        response = client.get("/price?city=Johannesburg&car_type=small&passengers=1")
        assert response.status_code == 400
        data = response.get_json()
        assert "error" in data

    def test_invalid_coords(self, client):
        response = client.get(
            "/price?city=Johannesburg&car_type=small&passengers=1&start_lon=abc&start_lat=xyz&end_lon=28.1&end_lat=-26.3"
        )
        assert response.status_code == 400
        data = response.get_json()
        assert "error" in data

    def test_invalid_car_type(self, client):
        response = client.get(
            "/price?city=Johannesburg&car_type=spaceship&passengers=1&start_lon=28.0&start_lat=-26.2&end_lon=28.1&end_lat=-26.3"
        )
        assert response.status_code == 400
        data = response.get_json()
        assert "error" in data

    def test_negative_passengers(self, client):
        response = client.get(
            "/price?city=Johannesburg&car_type=small&passengers=-2&start_lon=28.0&start_lat=-26.2&end_lon=28.1&end_lat=-26.3"
        )
        assert response.status_code == 400
        data = response.get_json()
        assert "error" in data

    def test_valid_coords_with_mocks(self, monkeypatch, client):
        def fake_weather(city):
            return None, None, None, "clear"

        def fake_distance(start, end):
            return 10.0, 15.0

        def fake_price_info(distance, duration, condition, car_type, passengers):
            return {
                "scaled_distance": distance,
                "weather_multiplier": 1.0,
                "distance_multiplier": 1.0,
                "duration_multiplier": 1.0,
                "car_multiplier": 1.0,
                "passenger_multiplier": 1.0,
                "time_multiplier": 1.0,
                "final_fare": 100.0,
            }

        monkeypatch.setattr("server.get_weather", fake_weather)
        monkeypatch.setattr("server.get_osrm_distance", fake_distance)
        monkeypatch.setattr("server.get_price_info", fake_price_info)

        response = client.get(
            "/price?city=Johannesburg&car_type=small&passengers=1&start_lon=28.0&start_lat=-26.2&end_lon=28.1&end_lat=-26.3"
        )
        assert response.status_code == 200
        data = response.get_json()
        assert data["final_fare"] == 100.0
        assert data["scaled_distance"] == 10.0
