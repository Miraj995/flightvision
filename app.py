from flask import Flask, jsonify, render_template
import requests
import os
from dotenv import load_dotenv
from datetime import datetime

load_dotenv()
app = Flask(__name__)

KEY = os.getenv("AVIATIONSTACK_KEY")
BASE_URL = "http://api.aviationstack.com/v1"

cached_data = {
    "arrivals": {},
    "departures": {},
    "belt": {}
}

@app.route("/")
def hello():
    return "✅ Flask API is running!"

@app.route("/view")
def homepage():
    flights = []
    for icao, data in cached_data["arrivals"].items():
        for item in data.get("data", []):
            flights.append({
                "flight": item.get("flight", {}).get("iata", "Unknown"),
                "departure": item.get("departure", {}).get("airport", "Unknown"),
                "arrival": item.get("arrival", {}).get("airport", "Unknown"),
                "status": item.get("flight_status", "Unknown"),
                "gate": item.get("arrival", {}).get("gate", "N/A")
            })
    return render_template("flight.html", flights=flights)


@app.route("/arrivals/<string:icao>")
def get_arrivals(icao):
    return jsonify(cached_data["arrivals"].get(icao, {"data": []}))

@app.route("/departures/<string:icao>")
def get_departures(icao):
    return jsonify(cached_data["departures"].get(icao, {"data": []}))

@app.route("/belt/<string:icao>")
def get_belt_info(icao):
    return jsonify(cached_data["belt"].get(icao, {"belt_info": []}))

@app.route("/refresh")
def manual_refresh():
    print("🔄 Starting cache refresh...")

    for icao in ["VABB"]:  # Extend this list if needed
        try:
            arrivals_url = f"{BASE_URL}/flights?access_key={KEY}&arr_icao={icao}"
            departures_url = f"{BASE_URL}/flights?access_key={KEY}&dep_icao={icao}"

            arrivals_response = requests.get(arrivals_url).json()
            departures_response = requests.get(departures_url).json()

            belt_data = []
            for flight in arrivals_response.get("data", []):
                belt = flight.get("arrival", {}).get("baggage", "N/A")
                flight_num = flight.get("flight", {}).get("iata", "Unknown")
                if belt and belt != "N/A":
                    belt_data.append({"flight": flight_num, "belt": belt})

            cached_data["arrivals"][icao] = arrivals_response
            cached_data["departures"][icao] = departures_response
            cached_data["belt"][icao] = {"belt_info": belt_data}

        except Exception as e:
            print(f"❌ Error updating cache for {icao}: {e}")

    return jsonify({"message": "✅ Manual cache update triggered", "time": str(datetime.now())})

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5001)
