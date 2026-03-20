from get_weather import get_weather
from get_distance import get_osrm_distance
import datetime

#===========================================================
# Dictionaries for multipliers
#===========================================================
weather_multiplier_map = {
    "thunder": 1.60, "storm": 1.60, "heavy": 1.50, "torrential": 1.50,
    "rain": 1.25, "drizzle": 1.25, "showers": 1.25,
    "mist": 1.10, "fog": 1.10, "overcast": 1.10,
    "snow": 1.80, "sleet": 1.80
}

distance_multiplier_map = {
    "long": 1.60, "medium": 1.30, "short": 1.10, "very_short": 1.00
}

car_multiplier_map = {
    "small": 1.0, "sedan": 1.2, "suv": 1.4, "luxury": 1.6,
    "van": 1.8, "pickup": 2.0, "ev": 1.3
}

passenger_multiplier_map = {1: 1.0, 2: 1.1, 3: 1.2, 4: 1.3, 5: 1.4, 6: 1.5}

time_multiplier_map = {"morning": 1.1, "day": 1.0, "evening": 1.2, "night": 1.3}

duration_multiplier_map = {
    "very_long": 1.5, "long": 1.3, "medium": 1.2,
    "short": 1.1, "very_short": 1.0
}

per_km_rate = {"default": 10.33, "premium": 12.0, "economy": 8.0}

#===========================================================
# Main fare calculation function
#===========================================================
def get_price_info(distance_km, duration_min, weather_cond,
                   car_type="small", passengers=1, ride_time=None):
    # Guard against None values
    if distance_km is None or duration_min is None:
        return {"error": "Distance or duration could not be calculated. Check coordinates or OSRM server."}

    cond = (weather_cond or "").lower()

    # Weather multiplier
    weather_multiplier = 1.0
    for key, mult in weather_multiplier_map.items():
        if key in cond:
            weather_multiplier = mult
            break

    # Distance multiplier
    if distance_km > 100:
        distance_multiplier = distance_multiplier_map["long"]
    elif distance_km > 50:
        distance_multiplier = distance_multiplier_map["medium"]
    elif distance_km > 10:
        distance_multiplier = distance_multiplier_map["short"]
    else:
        distance_multiplier = distance_multiplier_map["very_short"]

    # Duration multiplier
    if duration_min > 180:
        duration_multiplier = duration_multiplier_map["very_long"]
    elif duration_min > 120:
        duration_multiplier = duration_multiplier_map["long"]
    elif duration_min > 60:
        duration_multiplier = duration_multiplier_map["medium"]
    elif duration_min > 30:
        duration_multiplier = duration_multiplier_map["short"]
    else:
        duration_multiplier = duration_multiplier_map["very_short"]

    # Car multiplier
    car_mult = car_multiplier_map.get(car_type.lower(), 1.0)

    # Passenger multiplier
    passenger_mult = passenger_multiplier_map.get(passengers, 1.5)

    # Time multiplier
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

    # Per‑km scaling
    rate = per_km_rate["default"]
    scaled_distance = distance_km * rate

    # Final fare
    base_fare = 10000  # ₦100 in kobo
    final_fare = (base_fare * weather_multiplier * distance_multiplier *
                  duration_multiplier * car_mult * passenger_mult * time_mult)

    return {
        "scaled_distance": scaled_distance,
        "weather_multiplier": weather_multiplier,
        "distance_multiplier": distance_multiplier,
        "duration_multiplier": duration_multiplier,
        "car_multiplier": car_mult,
        "passenger_multiplier": passenger_mult,
        "time_multiplier": time_mult,
        "final_fare": final_fare
    }

#===========================================================
# Usage
#===========================================================
if __name__ == "__main__":
    city, country, temp_c, condition = get_weather("Johannesburg")
    start = (28.0473, -26.2041)   # Johannesburg CBD
    end   = (27.9770, -26.1450)   # Randburg (~21 km away)
    distance_km, duration_min = get_osrm_distance(start, end)

    result = get_price_info(distance_km, duration_min, condition, "SUV", passengers=2)
    print(result)
