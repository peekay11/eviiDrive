from flask import Flask, request, jsonify
from flask_cors import CORS
from get_weather import get_weather
from get_distance import get_osrm_distance
from get_price import get_price_info, minimum_fare_map, per_km_rate, per_min_rate, base_fare_map
from typing import Any
import requests

app = Flask(__name__)
CORS(app)

# ===========================================================
# Helpers
# ===========================================================
def _parse_coords(args: Any) -> tuple[dict[str, float], None] | tuple[None, tuple[dict, int]]:
    """Extract and validate all four coordinate params. Returns (coords_dict, None) or (None, error)."""
    coords: dict[str, float] = {}
    for key in ["start_lon", "start_lat", "end_lon", "end_lat"]:
        val = args.get(key)
        if val is None:
            return None, ({"error": f"Missing coordinate: {key}"}, 400)
        try:
            coords[key] = float(val)
        except ValueError:
            return None, ({"error": f"Invalid coordinate: {key} must be a number"}, 400)
    return coords, None


def _parse_passengers(args: Any) -> tuple[int, None] | tuple[None, tuple[dict, int]]:
    """Parse and validate passengers param. Returns (int, None) or (None, error)."""
    try:
        val = args.get("passengers", "1")
        return int(val), None
    except (TypeError, ValueError):
        return None, ({"error": "Invalid passengers value — must be an integer."}, 400)


# ===========================================================
# Routes
# ===========================================================
@app.route("/")
def home() -> str:
    return "eviiDrive server is running. Use /price or /price/summary endpoints."


@app.route("/price")
def price():
    """
    Returns the full fare breakdown including all multipliers.
    Query params: city, car_type, passengers, start_lon, start_lat, end_lon, end_lat
    """
    try:
        city     = request.args.get("city", "Johannesburg")
        car_type = request.args.get("car_type", "small")

        passengers, p_err = _parse_passengers(request.args)
        if p_err is not None:
            return jsonify(p_err[0]), p_err[1]
        assert passengers is not None  # narrows type for Pylance

        coords, c_err = _parse_coords(request.args)
        if c_err is not None:
            return jsonify(c_err[0]), c_err[1]
        assert coords is not None  # narrows type for Pylance

        _, _, _, condition = get_weather(city)

        raw = get_osrm_distance(
            (coords["start_lon"], coords["start_lat"]),
            (coords["end_lon"],   coords["end_lat"])
        )

        # Guard against get_osrm_distance returning None
        if raw is None or raw[0] is None or raw[1] is None:
            return jsonify({"error": "Could not calculate route distance."}), 502

        distance_km: float = float(raw[0])
        duration_min: float = float(raw[1])

        result = get_price_info(distance_km, duration_min, condition, car_type, passengers)

        if "error" in result:
            return jsonify(result), 400

        result["distance_km"]  = round(distance_km, 2)
        result["duration_min"] = round(duration_min, 2)
        result["weather"]      = condition
        result["car_type"]     = car_type
        result["passengers"]   = passengers

        return jsonify(result), 200

    except Exception as e:
        return jsonify({"error": f"Unexpected server error: {str(e)}"}), 500


@app.route("/price/summary")
def price_summary():
    """
    Returns a simplified, frontend-friendly fare summary.
    Same query params as /price.
    """
    try:
        city     = request.args.get("city", "Johannesburg")
        car_type = request.args.get("car_type", "small")

        passengers, p_err = _parse_passengers(request.args)
        if p_err is not None:
            return jsonify(p_err[0]), p_err[1]
        assert passengers is not None

        coords, c_err = _parse_coords(request.args)
        if c_err is not None:
            return jsonify(c_err[0]), c_err[1]
        assert coords is not None

        _, _, _, condition = get_weather(city)

        raw = get_osrm_distance(
            (coords["start_lon"], coords["start_lat"]),
            (coords["end_lon"],   coords["end_lat"])
        )

        if raw is None or raw[0] is None or raw[1] is None:
            return jsonify({"error": "Could not calculate route distance."}), 502

        distance_km: float = float(raw[0])
        duration_min: float = float(raw[1])

        result = get_price_info(distance_km, duration_min, condition, car_type, passengers)

        if "error" in result:
            return jsonify(result), 400

        summary: dict[str, Any] = {
            "car_type":      car_type,
            "passengers":    passengers,
            "distance_km":   round(distance_km, 2),
            "duration_min":  round(duration_min, 2),
            "weather":       condition,
            "base_fare":     result["base_fare"],
            "km_charge":     result["km_charge"],
            "minute_charge": result["minute_charge"],
            "raw_fare":      result["raw_fare"],
            "minimum_fare":  result["minimum_fare"],
            "final_fare":    result["final_fare"],
            "currency":      "ZAR",
            "price_label":   f"R{result['final_fare']:.2f}",
        }

        return jsonify(summary), 200

    except Exception as e:
        return jsonify({"error": f"Unexpected server error: {str(e)}"}), 500


@app.route("/vehicles")
def vehicles():
    """Returns available vehicle types with their base rates."""

    # dict[str, Any] so floats can be assigned alongside strings — fixes lines 161-164
    vehicle_list: list[dict[str, Any]] = [
        {"value": "small",       "label": "Small",       "icon": "🚗"},
        {"value": "sedan",       "label": "Sedan",       "icon": "🚙"},
        {"value": "suv",         "label": "SUV",         "icon": "🛻"},
        {"value": "luxury",      "label": "Luxury",      "icon": "🏎️"},
        {"value": "van",         "label": "Van",         "icon": "🚐"},
        {"value": "pickup",      "label": "Pickup",      "icon": "🛻"},
        {"value": "ev",          "label": "EV",          "icon": "⚡"},
        {"value": "motorbike",   "label": "Motorbike",   "icon": "🏍️"},
        {"value": "minibus",     "label": "Minibus",     "icon": "🚌"},
        {"value": "convertible", "label": "Convertible", "icon": "🚘"},
        {"value": "limousine",   "label": "Limousine",   "icon": "🚖"},
        {"value": "truck",       "label": "Truck",       "icon": "🚛"},
        {"value": "shuttle",     "label": "Shuttle",     "icon": "🚍"},
    ]

    for v in vehicle_list:
        key: str = v["value"]
        v["base_fare"]    = base_fare_map.get(key, base_fare_map["default"])
        v["per_km"]       = per_km_rate.get(key, per_km_rate["default"])
        v["per_min"]      = per_min_rate.get(key, per_min_rate["default"])
        v["minimum_fare"] = minimum_fare_map.get(key, minimum_fare_map["default"])

    return jsonify(vehicle_list), 200


@app.route("/suggest")
def suggest():
    """Autocomplete location suggestions via Nominatim."""
    query = request.args.get("q")
    if not query:
        return jsonify({"error": "Missing query parameter: q"}), 400

    url = "https://nominatim.openstreetmap.org/search"
    params = {
        "q":              query,
        "format":         "json",
        "addressdetails": 1,
        "limit":          5
    }
    headers = {"User-Agent": "eviiDriveApp"}

    try:
        response = requests.get(url, params=params, headers=headers, timeout=5)
        response.raise_for_status()
        return jsonify(response.json()), 200
    except requests.exceptions.Timeout:
        return jsonify({"error": "Location service timed out."}), 504
    except requests.exceptions.RequestException as e:
        return jsonify({"error": f"Location service error: {str(e)}"}), 502


if __name__ == "__main__":
    app.run(host="0.0.0.0", port=8000, debug=True)