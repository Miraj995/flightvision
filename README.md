# ✈️ FlightVision

**FlightVision** is a Flask-based web application that fetches and displays live flight arrival, departure, and baggage belt information for airports using the [AviationStack API](https://aviationstack.com/). The project includes both a REST API and a basic HTML interface.

---

## 📦 Features

- ✅ Fetch live **arrivals**, **departures**, and **baggage belt** info by airport ICAO code.
- ✅ Clean HTML interface for browser display (`flight.html`)
- ✅ JSON API output for developers.
- ✅ Environment-based config via `.env`.
- ✅ Socket + Scheduler + Automation Ready
- ✅ Compatible with local LAN + Ngrok/Render deployment

---

## 🧰 Technologies

- Python 3
- Flask
- Gunicorn (for deployment)
- Dotenv
- Requests

---

## 🚀 Getting Started

### 1. Clone the repository
```bash
git clone https://github.com/your-username/flightvision.git
cd flightvision
