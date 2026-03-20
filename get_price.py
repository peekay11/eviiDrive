from get_weather import get_weather   # your weather module
from get_distance import get_osrm_distance  # import the function, not variables
import datetime

#===========================================================
# Dictionaries for multipliers
#===========================================================
weather_multiplier_map = {
    "thunder": 1.60,
    "storm": 1.60,
    "heavy": 1.50,
    "torrential": 1.50,
    "rain": 1.25,
    "drizzle": 1.25,
    "showers": 1.25,
    "mist": 1.10,
    "fog": 1.10,
    "overcast": 1.10,
    "snow": 1.80,
    "sleet": 1.80
}

distance_multiplier_map = {
    "long": 1.60,       # > 100 km
    "medium": 1.30,     # 50–100 km
    "short": 1.10,      # 10–50 km
    "very_short": 1.00  # < 10 km
}

car_multiplier_map = {
    "small": 1.0,
    "sedan": 1.2,
    "suv": 1.4,
    "luxury": 1.6,
    "van": 1.8,
    "pickup": 2.0,
    "ev": 1.3
}

passenger_multiplier_map = {
    1: 1.0,
    2: 1.1,
    3: 1.2,
    4: 1.3,
    5: 1.4,
    6: 1.5
}

time_multiplier_map = {
    "morning": 1.1,   # 5am–11am
    "day": 1.0,       # 11am–5pm
    "evening": 1.2,   # 5pm–10pm
    "night": 1.3      # 10pm–5am
}

duration_multiplier_map = {
    "very_long": 1.5,   # > 180 min
    "long": 1.3,        # 120–180 min
    "medium": 1.2,      # 60–120 min
    "short": 1.1,       # 30–60 min
    "very_short": 1.0   # < 30 min
}

# Per‑km rate dictionary (scaling factor)
per_km_rate = {
    "default": 10.33,   # 21 km → 217, 59.32 km → ~614
    "premium": 12.0,
    "economy": 8.0
}

#===========================================================
# Main fare calculation function
#===========================================================
def get_price_info(distance_km, duration_min, weather_cond, car_type="small", passengers=1, ride_time=None):
    cond = (weather_cond or "").lower()

    # Weather multiplier lookup
    weather_multiplier = 1.0
    for key, mult in weather_multiplier_map.items():
        if key in cond:
            weather_multiplier = mult
            break

    # Distance multiplier lookup
    if distance_km > 100:
        distance_multiplier = distance_multiplier_map["long"]
    elif distance_km > 50:
        distance_multiplier = distance_multiplier_map["medium"]
    elif distance_km > 10:
        distance_multiplier = distance_multiplier_map["short"]
    else:
        distance_multiplier = distance_multiplier_map["very_short"]

    # Duration multiplier lookup
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

    # Car multiplier lookup
    car_mult = car_multiplier_map.get(car_type.lower(), 1.0)

    # Passenger multiplier lookup
    passenger_mult = passenger_multiplier_map.get(passengers, 1.5)

    # Time multiplier lookup
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
    rate = per_km_rate.get("default")
    scaled_distance = distance_km * rate

    # Final fare calculation
    base_fare = 10000  # ₦100 in kobo
    final_fare = base_fare * weather_multiplier * distance_multiplier * duration_multiplier * car_mult * passenger_mult * time_mult

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
    # Get weather info from your get_weather.py
    city, country, temp_c, condition = get_weather("Johannesburg")


    start = (28.0473, -26.2041)   # Johannesburg CBD
    end   = (27.9770, -26.1450)   # Randburg area (~21 km away by road)
    distance_km, duration_min = get_osrm_distance(start, end)


    # Calculate price info
    result = get_price_info(distance_km, duration_min, condition, "SUV", passengers=2)
    print(result)
