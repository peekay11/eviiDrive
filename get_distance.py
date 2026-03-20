import requests

def get_osrm_distance(start, end):
    """
    start and end are tuples of (longitude, latitude)
    Example: start = (28.0473, -26.2041)  # Johannesburg
             end   = (28.2293, -25.7479)  # Pretoria
    """
    base_url = "http://router.project-osrm.org/route/v1/driving/"
    coords = f"{start[0]},{start[1]};{end[0]},{end[1]}"
    url = f"{base_url}{coords}?overview=false"

    try:
        response = requests.get(url, timeout=10)
        response.raise_for_status()
        data = response.json()
    except Exception as e:
        print("Error contacting OSRM:", e)
        return None, None

    if data.get("code") == "Ok" and "routes" in data and data["routes"]:
        route = data["routes"][0]
        distance_m = route.get("distance")
        duration_s = route.get("duration")

        if distance_m is None or duration_s is None:
            return None, None

        # Convert to km and minutes
        distance_km = distance_m / 1000.0
        duration_min = duration_s / 60.0

        return distance_km, duration_min
    else:
        print("OSRM error:", data.get("message"))
        return None, None

# Example usage: Johannesburg → Pretoria
if __name__ == "__main__":
    start = (28.0473, -26.2041)   # Johannesburg (lon, lat)
    end   = (28.2293, -25.7479)   # Pretoria (lon, lat)

    distance_km, duration_min = get_osrm_distance(start, end)

    if distance_km is not None and duration_min is not None:
        print(f"Distance: {distance_km:.2f} km")
        print(f"Duration: {duration_min:.1f} minutes")
    else:
        print("Could not calculate distance/duration.")
