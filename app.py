from flask import Flask, jsonify, render_template
import requests
import os
import threading
import time
from dotenv import load_dotenv

load_dotenv()
app = Flask(__name__)

KEY = os.getenv("AVIATIONSTACK_KEY")
BASE_URL = "http://api.aviationstack.com/v1"
UPDATE_INTERVAL = 43200  # 12 hours in seconds

# In-memory cache
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
    return render_template("flight.html")

@app.route("/arrivals/<string:icao>")
def get_arrivals(icao):
    return jsonify(cached_data["arrivals"].get(icao, {"data": []}))

@app.route("/departures/<string:icao>")
def get_departures(icao):
    return jsonify(cached_data["departures"].get(icao, {"data": []}))

@app.route("/belt/<string:icao>")
def get_belt_info(icao):
    return jsonify(cached_data["belt"].get(icao, {"belt_info": []}))


def update_cache():
    while True:
        print("🔁 Refreshing cached flight data...")

        for icao in ["VABB"]:  # Extendable: add more ICAOs here
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
                        belt_data.append({
                            "flight": flight_num,
                            "belt": belt
                        })

                cached_data["arrivals"][icao] = arrivals_response
                cached_data["departures"][icao] = departures_response
                cached_data["belt"][icao] = {"belt_info": belt_data}

                print(f"✅ Updated cache for {icao} successfully.")
            except Exception as e:
                print(f"⚠️ Failed to update cache for {icao}: {e}")

        time.sleep(UPDATE_INTERVAL)


if __name__ == "__main__":
    threading.Thread(target=update_cache, daemon=True).start()
    app.run(host="0.0.0.0", port=5001)
