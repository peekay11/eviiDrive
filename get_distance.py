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

    response = requests.get(url)
    data = response.json()

    if data.get("code") == "Ok":
        route = data["routes"][0]
        distance_m = route["distance"]   # in meters
        duration_s = route["duration"]   # in seconds

        # Convert to km and minutes
        distance_km = distance_m / 1000.0
        duration_min = duration_s / 60.0

        return distance_km, duration_min
    else:
        print("Error:", data.get("message"))
        return None, None

# Example usage: Johannesburg → Pretoria
if __name__ == "__main__":
    start = (28.0473, -26.2041)   # Johannesburg (lon, lat)
    end   = (28.2293, -25.7479)   # Pretoria (lon, lat)
    
    distance_km, duration_min = get_osrm_distance(start, end)
    print(f"Distance: {distance_km:.2f} km")
    print(f"Duration: {duration_min:.1f} minutes")
