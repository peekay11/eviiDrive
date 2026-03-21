import datetime
from get_weather import get_weather
from get_distance import get_osrm_distance

# ===========================================================
# Uber SA–aligned pricing model
# Formula: (base_fare + per_km * distance + per_min * duration)
#          * weather * distance * duration * car * passenger * time
#          → then enforce minimum fare
# ===========================================================

# --- Weather multipliers (unchanged — sensible) ---
weather_multiplier_map = {
    "thunder": 1.60, "storm": 1.60, "heavy": 1.50, "torrential": 1.50,
    "rain": 1.25, "drizzle": 1.25, "showers": 1.25,
    "mist": 1.10, "fog": 1.10, "overcast": 1.10,
    "snow": 1.80, "sleet": 1.80
}

# --- Distance-band multipliers (unchanged) ---
distance_multiplier_map = {
    "long": 1.60, "medium": 1.30, "short": 1.10, "very_short": 1.00
}

# --- Car-type multipliers (unchanged) ---
car_multiplier_map = {
    "small": 1.0, "sedan": 1.2, "suv": 1.4, "luxury": 1.6,
    "van": 1.8, "pickup": 2.0, "ev": 1.3, "motorbike": 0.8,
    "minibus": 2.2, "convertible": 1.7, "limousine": 2.5,
    "truck": 2.8, "shuttle": 1.9
}

# --- Passenger multipliers (unchanged) ---
passenger_multiplier_map = {1: 1.0, 2: 1.1, 3: 1.2, 4: 1.3, 5: 1.4, 6: 1.5}

# --- Time-of-day multipliers (unchanged) ---
time_multiplier_map = {
    "morning": 1.1, "day": 1.0, "evening": 1.2, "night": 1.3
}

# --- Duration multipliers (unchanged) ---
duration_multiplier_map = {
    "very_long": 1.5, "long": 1.3, "medium": 1.2,
    "short": 1.1, "very_short": 1.0
}

# ===========================================================
# BASE FARE per car type  (Uber SA: R5 for UberX / "small")
# Scaled up proportionally for premium categories
# ===========================================================
base_fare_map = {
    "small":       5.00,   # UberX — keep at SA baseline (already minimum)
    "sedan":       6.00,   # was 7.00
    "suv":         7.50,   # was 10.00
    "luxury":     10.00,   # was 15.00
    "van":        10.00,   # was 18.00
    "pickup":     10.00,   # was 20.00
    "ev":          5.50,   # was 6.00
    "motorbike":   3.50,   # was 4.00 — cheapest entry point
    "minibus":    20.00,   # was 40.00
    "convertible": 10.00,  # was 18.00
    "limousine":  25.00,   # was 50.00
    "truck":      30.00,   # was 60.00
    "shuttle":    10.00,   # was 20.00
    "default":     5.00
}

# ===========================================================
# PER-KM RATE  (Uber SA: R7.50/km for UberX / "small")
# ===========================================================
per_km_rate = {
    "small":       7.50,   # UberX baseline ← was 8.50
    "sedan":       9.00,   # ← was 9.50
    "suv":        11.50,
    "luxury":     15.00,   # ← was 14.00
    "van":        14.00,   # ← was 13.50
    "pickup":     13.00,
    "ev":          8.50,   # slightly below small (lower running cost)
    "motorbike":   5.50,   # UberMoto — cheapest per km
    "minibus":    16.00,
    "convertible": 14.00,
    "limousine":  20.00,
    "truck":      22.00,
    "shuttle":    12.00,
    "default":     7.50
}

# ===========================================================
# PER-MINUTE RATE  ← NEW: Uber SA charges R0.75/min for UberX
# ===========================================================
per_min_rate = {
    "small":       0.75,   # UberX baseline
    "sedan":       0.90,
    "suv":         1.10,
    "luxury":      1.50,
    "van":         1.30,
    "pickup":      1.20,
    "ev":          0.80,
    "motorbike":   0.50,
    "minibus":     1.80,
    "convertible": 1.40,
    "limousine":   2.20,
    "truck":       2.50,
    "shuttle":     1.10,
    "default":     0.75
}

# ===========================================================
# MINIMUM FARES per car type  (Uber SA: R20 for UberX)
# ===========================================================
minimum_fare_map = {
    "small":       20.00,
    "sedan":       25.00,
    "suv":         35.00,
    "luxury":      60.00,
    "van":         55.00,
    "pickup":      50.00,
    "ev":          22.00,
    "motorbike":   15.00,
    "minibus":     80.00,
    "convertible": 55.00,
    "limousine":  120.00,
    "truck":      150.00,
    "shuttle":     50.00,
    "default":     20.00
}

# ===========================================================
# Main fare calculation function
# ===========================================================
def get_price_info(distance_km, duration_min, weather_cond,
                   car_type="small", passengers=1, ride_time=None):
    try:
        # --- Input validation ---
        if distance_km is None or duration_min is None:
            return {"error": "Distance or duration missing."}
        if not isinstance(distance_km, (int, float)) or not isinstance(duration_min, (int, float)):
            return {"error": "Distance and duration must be numbers."}
        if passengers < 1:
            return {"error": "Passengers must be >= 1."}

        car = car_type.lower()
        if car not in car_multiplier_map:
            return {"error": f"Invalid car type '{car_type}'. "
                             f"Allowed: {', '.join(car_multiplier_map.keys())}"}

        cond = (weather_cond or "clear").lower()

        # --- Weather multiplier ---
        weather_mult = 1.0
        for key, mult in weather_multiplier_map.items():
            if key in cond:
                weather_mult = mult
                break

        # --- Distance-band multiplier ---
        if distance_km > 100:
            dist_mult = distance_multiplier_map["long"]
        elif distance_km > 50:
            dist_mult = distance_multiplier_map["medium"]
        elif distance_km > 10:
            dist_mult = distance_multiplier_map["short"]
        else:
            dist_mult = distance_multiplier_map["very_short"]

        # --- Duration multiplier ---
        if duration_min > 180:
            dur_mult = duration_multiplier_map["very_long"]
        elif duration_min > 120:
            dur_mult = duration_multiplier_map["long"]
        elif duration_min > 60:
            dur_mult = duration_multiplier_map["medium"]
        elif duration_min > 30:
            dur_mult = duration_multiplier_map["short"]
        else:
            dur_mult = duration_multiplier_map["very_short"]

        # --- Car multiplier ---
        car_mult = car_multiplier_map[car]

        # --- Passenger multiplier ---
        passenger_mult = passenger_multiplier_map.get(passengers, 1.5)
        if car in ["truck", "minibus"]:
            passenger_mult = max(passenger_mult, 2.0)

        # --- Time-of-day multiplier ---
        if ride_time is None:
            ride_time = datetime.datetime.now()
        hour = ride_time.hour
        if 5 <= hour < 11:
            time_mult = time_multiplier_map["morning"]
        elif 11 <= hour < 17:
            time_mult = time_multiplier_map["day"]
        elif 17 <= hour < 22:
            time_mult = time_multiplier_map["evening"]
        else:
            time_mult = time_multiplier_map["night"]

        # --- Long-distance surcharge ---
        long_trip_mult = 1 + (distance_km / 5000) if distance_km > 200 else 1.0

        # --- Core fare components (Uber SA formula) ---
        base_fare    = base_fare_map.get(car, base_fare_map["default"])
        km_charge    = distance_km * per_km_rate.get(car, per_km_rate["default"])
        minute_charge = duration_min * per_min_rate.get(car, per_min_rate["default"])
        raw_fare     = base_fare + km_charge + minute_charge

        # --- Apply all multipliers ---
        final_fare = (raw_fare * weather_mult * dist_mult * dur_mult
                      * car_mult * passenger_mult * time_mult * long_trip_mult)

        # --- Enforce minimum fare ---
        min_fare   = minimum_fare_map.get(car, minimum_fare_map["default"])
        final_fare = max(final_fare, min_fare)

        return {
            "base_fare":           base_fare,
            "km_charge":           round(km_charge, 2),
            "minute_charge":       round(minute_charge, 2),
            "raw_fare":            round(raw_fare, 2),
            "weather_multiplier":  weather_mult,
            "distance_multiplier": dist_mult,
            "duration_multiplier": dur_mult,
            "car_multiplier":      car_mult,
            "passenger_multiplier": passenger_mult,
            "time_multiplier":     time_mult,
            "long_trip_multiplier": round(long_trip_mult, 4),
            "minimum_fare":        min_fare,
            "final_fare":          round(final_fare, 2)
        }

    except Exception as e:
        return {"error": f"Unexpected error: {str(e)}"}


# ===========================================================
# Usage Example
# ===========================================================
if __name__ == "__main__":
    city, country, temp_c, condition = get_weather("Johannesburg")
    start = (28.0473, -26.2041)   # Johannesburg CBD
    end   = (27.9770, -26.1450)   # Randburg (~21 km away)
    distance_km, duration_min = get_osrm_distance(start, end)

    result = get_price_info(distance_km, duration_min, condition, "small", passengers=1)
    print(result)