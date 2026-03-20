# eviiDrive 🚗💨

A ride pricing calculator for drivers.  
eviiDrive helps drivers estimate fares based on **distance, car type, passenger load, weather, and time of day**.  
It integrates with **WeatherAPI** and **OSRM** (Open Source Routing Machine) to fetch real‑time conditions and route distances.

---

## ✨ Features
- **Distance scaling**: Converts kilometers into scaled units (e.g., 21 km → 217).
- **Car type multipliers**: Different rates for small cars, sedans, SUVs, vans, pickups, EVs, and luxury vehicles.
- **Passenger load multipliers**: Adjusts fares based on the number of passengers.
- **Weather multipliers**: Rain, storms, fog, snow, etc. affect pricing.
- **Time of day multipliers**: Morning, day, evening, and night rates.
- **Duration multipliers**: Longer trips cost more depending on travel time.
- **Modular design**: Easy to extend with new rules or APIs.

---

## 🛠️ Installation
Clone the repository:
```bash
git clone https://github.com/peekay11/eviiDrive.git
cd eviiDrive
