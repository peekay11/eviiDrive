# server.py
from flask import Flask, request, jsonify
from flask_cors import CORS
from get_weather import get_weather
from get_distance import get_osrm_distance
from get_price import get_price_info

app = Flask(__name__)
CORS(app)

@app.route("/")
def home():
    return "eviiDrive server is running. Use /price endpoint with query parameters."

@app.route("/price")
def price():
    try:
        city = request.args.get("city", "Johannesburg")
        car_type = request.args.get("car_type", "small")

        # Passengers validation
        try:
            passengers_str = request.args.get("passengers", "1")
            passengers = int(passengers_str)
        except (TypeError, ValueError):
            return jsonify({"error": "Invalid passengers value."}), 400

        # Coordinates validation
        coords = {}
        for key in ["start_lon", "start_lat", "end_lon", "end_lat"]:
            val = request.args.get(key)
            if val is None:
                return jsonify({"error": f"Missing coordinate: {key}"}), 400
            try:
                coords[key] = float(val)
            except ValueError:
                return jsonify({"error": f"Invalid coordinate: {key} must be a number"}), 400

        # Weather
        _, _, _, condition = get_weather(city)

        # Distance
        distance_km, duration_min = get_osrm_distance(
            (coords["start_lon"], coords["start_lat"]),
            (coords["end_lon"], coords["end_lat"])
        )

        # Fare calculation
        result = get_price_info(distance_km, duration_min, condition, car_type, passengers)

        if "error" in result:
            return jsonify(result), 400

        return jsonify(result), 200

    except Exception as e:
        return jsonify({"error": f"Unexpected server error: {str(e)}"}), 500

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000, debug=True)
