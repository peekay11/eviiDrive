import requests
from secrets_ import api_key



# Configuration
API_KEY = api_key
BASE_URL = "http://api.weatherapi.com/v1/current.json"

def get_weather(location):
    """
    Fetches current weather data for a specific location.
    Returns: city, country, temp_c, condition
    """
    params = {
        "key": API_KEY,
        "q": location,
        "aqi": "no"
    }
    
    try:
        response = requests.get(BASE_URL, params=params)
        data = response.json()
        
        if "error" in data:
            # Return Nones so the calling code can handle the failure gracefully
            return None, None, None, None
            
        # Extracting raw values for reference
        city = data["location"]["name"]
        country = data["location"]["country"]
        temp_c = data["current"]["temp_c"]
        condition = data["current"]["condition"]["text"]
        
        return city, country, temp_c, condition

    except Exception:
        # Network or Request errors
        return None, None, None, None


city, country, temp_c, condition = get_weather("johannesburg")
