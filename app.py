from flask import Flask, jsonify, render_template
import requests
import os
from dotenv import load_dotenv

load_dotenv()
app = Flask(__name__)

KEY = os.getenv("AVIATIONSTACK_KEY")
BASE_URL = "http://api.aviationstack.com/v1"

@app.route("/")
def hello():
    return "✅ Flask API is running!"

  @app.route("/")
def homepage():
    return render_template("flight.html")
  

# Generic arrival route
@app.route("/arrivals/<string:icao>")
def get_arrivals(icao):
    url = f"{BASE_URL}/flights?access_key={KEY}&arr_icao={icao}"
    r = requests.get(url)
    return jsonify(r.json())

# Generic departure route
@app.route("/departures/<string:icao>")
def get_departures(icao):
    url = f"{BASE_URL}/flights?access_key={KEY}&dep_icao={icao}"
    r = requests.get(url)
    return jsonify(r.json())

# Baggage belt info route
@app.route("/belt/<string:icao>")
def get_belt_info(icao):
    url = f"{BASE_URL}/flights?access_key={KEY}&arr_icao={icao}"
    r = requests.get(url)
    data = r.json()

    belt_data = []
    for flight in data.get("data", []):
        belt = flight.get("arrival", {}).get("baggage", "N/A")
        flight_num = flight.get("flight", {}).get("iata", "Unknown")
        if belt and belt != "N/A":
            belt_data.append({
                "flight": flight_num,
                "belt": belt
            })

    return jsonify({"belt_info": belt_data})

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5001)
