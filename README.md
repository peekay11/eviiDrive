# EviiDrive - Smart Ride Fare Engine

EviiDrive is a comprehensive live fare calculation engine built to provide instant, transparent pricing across multiple cities. It prevents surge surprises by calculating real-time fares to the cent, combining distance, expected duration, vehicle type, and even live weather conditions.

## Features

- **Dynamic Fare Calculation**: Factors in distance (km charge), time (minute charge), base fares, and vehicle-specific minimum fares.
- **Real-Time Weather Integration**: Integrates with the Open-Meteo API to adjust pricing multipliers dynamically based on real-time weather conditions in the selected city.
- **Address Autocomplete**: Fast location searching and geocoding using the Nominatim (OpenStreetMap) API.
- **Intelligent Routing**: Uses the OSRM (Open Source Routing Machine) API to fetch accurate driving distances and ETAs between pickup and drop-off coordinates.
- **Rich UI**: A beautifully designed, responsive, dark-mode frontend featuring micro-animations, glassmorphism, and dynamic layout handling.

## Tech Stack

- **Frontend**: Vanilla HTML5, CSS3, JavaScript (No heavy frameworks).
- **Backend**: Python 3.12, Flask, Flask-CORS.
- **Containerization**: Docker & Docker Compose (with Nginx as a reverse proxy).
- **APIs**:
  - [OSRM API](https://project-osrm.org/) for routing.
  - [Nominatim](https://nominatim.openstreetmap.org/) for geocoding.
  - [Open-Meteo](https://open-meteo.com/) for weather data.

## Supported Cities
- Johannesburg
- Cape Town
- Durban
- Pretoria

## Supported Vehicle Types
We support 13 distinct vehicle configurations, each with its own base fare, per-km rate, per-minute rate, and minimum fare:
*Small, Sedan, SUV, Luxury, Van, Pickup, EV, Motorbike, Minibus, Convertible, Limousine, Truck, Shuttle*

## Project Structure

```
eviiDrive/
├── frontend/
│   ├── index.html        # Main SPA interface
│   └── Dockerfile        # Frontend container configuration
├── backend/
│   ├── server.py         # Flask API Gateway and static file server
│   ├── get_price.py      # Core pricing algorithms and base mappings
│   ├── get_weather.py    # Open-Meteo integration logic
│   ├── get_distance.py   # OSRM routing and parsing
│   ├── requirements.txt  # Python dependencies
│   └── Dockerfile        # Backend container configuration
├── nginx/
│   └── default.conf      # Nginx routing configuration for Docker
├── docker-compose.yml    # Orchestrates frontend, backend, and nginx
└── README.md             # Project documentation
```

## Running the Project

### Using Docker Compose (Recommended)

1. Ensure you have Docker and Docker Compose installed.
2. Run the application:
   ```bash
   docker-compose up -d --build
   ```
3. Visit `http://localhost:8080` in your web browser.

### Running Locally (Without Docker)

1. Set up a Python virtual environment:
   ```bash
   python3 -m venv venv
   source venv/bin/activate
   ```
2. Install the backend dependencies:
   ```bash
   pip install -r backend/requirements.txt
   ```
3. Start the Flask server (which also serves the frontend):
   ```bash
   cd backend
   python server.py
   ```
4. Access the web app at `http://localhost:8000`.

## API Endpoints

- `GET /api/price`: Returns the full fare breakdown including multipliers and coordinates.
- `GET /api/price/summary`: Returns a simplified, frontend-friendly fare summary object.
- `GET /api/vehicles`: Returns the list of all supported vehicle types and their pricing structures.
- `GET /api/suggest?q=<query>`: Proxies autocomplete location suggestions from Nominatim.

## License

© 2025 Eviidrive. All rights reserved.
