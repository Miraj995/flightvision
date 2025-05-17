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
    print("📝 Rendering flight view...")
    flights = []
    for icao, data in cached_data["arrivals"].items():
        print(f"📦 Cached arrivals for {icao}: {len(data.get('data', []))} flights")
        for item in data.get("data", []):
            flight_info = {
                "flight": item.get("flight", {}).get("iata", "Unknown"),
                "departure": item.get("departure", {}).get("airport", "Unknown"),
                "arrival": item.get("arrival", {}).get("airport", "Unknown"),
                "status": item.get("flight_status", "Unknown"),
                "gate": item.get("departure", {}).get("gate") or item.get("arrival", {}).get("gate") or "N/A"
            }
            print(f"✈️ Flight data: {flight_info}")
            flights.append(flight_info)

    if not flights:
        print("⚠️ No flight data to display.")
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

    for icao in ["VABB"]:  # Extendable
        try:
            print(f"🌐 Fetching data for {icao}...")
            arrivals_url = f"{BASE_URL}/flights?access_key={KEY}&arr_icao={icao}"
            departures_url = f"{BASE_URL}/flights?access_key={KEY}&dep_icao={icao}"

            arrivals_response = requests.get(arrivals_url).json()
            departures_response = requests.get(departures_url).json()

            print(f"✅ Arrivals fetched: {len(arrivals_response.get('data', []))}")
            print(f"✅ Departures fetched: {len(departures_response.get('data', []))}")

            belt_data = []
            for flight in arrivals_response.get("data", []):
                belt = flight.get("arrival", {}).get("baggage", "N/A")
                flight_num = flight.get("flight", {}).get("iata", "Unknown")
                if belt and belt != "N/A":
                    belt_data.append({"flight": flight_num, "belt": belt})

            print(f"🎒 Belt info collected: {len(belt_data)} entries")

            cached_data["arrivals"][icao] = arrivals_response
            cached_data["departures"][icao] = departures_response
            cached_data["belt"][icao] = {"belt_info": belt_data}

        except Exception as e:
            print(f"❌ Error updating cache for {icao}: {e}")

    print("✅ Cache refresh complete.")
    return jsonify({"message": "✅ Manual cache update triggered", "time": str(datetime.now())})

if __name__ == "__main__":
    print("🚀 Starting Flask server...")
    app.run(host="0.0.0.0", port=5001, debug=True)
