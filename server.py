from flask import Flask, request, jsonify
from flask_cors import CORS
from get_weather import get_weather
from get_distance import get_osrm_distance
from get_price import get_price_info

app = Flask(__name__)
CORS(app)  # allow cross-origin requests

@app.route("/")
def home():
    return "eviiDrive server is running. Use /price endpoint with query parameters."

@app.route("/price", methods=["GET"])
def calculate_price():
    city = request.args.get("city", "Johannesburg")
    car_type = request.args.get("car_type", "small")
    passengers = int(request.args.get("passengers", 1))

    def safe_float(value, default=0.0):
        try:
            return float(value)
        except (TypeError, ValueError):
            return default

    start_lon = safe_float(request.args.get("start_lon"))
    start_lat = safe_float(request.args.get("start_lat"))
    end_lon   = safe_float(request.args.get("end_lon"))
    end_lat   = safe_float(request.args.get("end_lat"))

    _, _, _, condition = get_weather(city)
    distance_km, duration_min = get_osrm_distance((start_lon, start_lat), (end_lon, end_lat))

    if distance_km is None or duration_min is None:
        return jsonify({"error": "Could not calculate distance. Check coordinates or OSRM server."}), 400

    result = get_price_info(distance_km, duration_min, condition, car_type, passengers)
    return jsonify(result)

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000, debug=True)
