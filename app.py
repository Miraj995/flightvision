from flask import Flask, jsonify, render_template, request, redirect, url_for
import requests
import os
from dotenv import load_dotenv
from datetime import datetime
from config import Config
from models.db_models import db, Flight, Advertisement
from flask_migrate import Migrate

load_dotenv()

app = Flask(__name__)
app.config.from_object(Config)

# DB Setup
db.init_app(app)
migrate = Migrate(app, db)

# API Setup
KEY = app.config.get("AVIATIONSTACK_KEY")
BASE_URL = "http://api.aviationstack.com/v1"

# In-memory Cache
dcached_data = {
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
    for icao, data in dcached_data["arrivals"].items():
        for item in data.get("data", []):
            flights.append({
                "flight": item.get("flight", {}).get("iata", "Unknown"),
                "departure": item.get("departure", {}).get("airport", "Unknown"),
                "arrival": item.get("arrival", {}).get("airport", "Unknown"),
                "status": item.get("flight_status", "Unknown"),
                "gate": item.get("departure", {}).get("gate") or item.get("arrival", {}).get("gate") or "N/A"
            })
    return render_template("flight.html", flights=flights)

@app.route("/refresh")
def manual_refresh():
    print("🔁 Manual refresh triggered")

    if not KEY:
        print("❌ API Key not found.")
        return jsonify({"error": "API key not configured"}), 500

    for icao in ["VABB"]:
        try:
            arrivals_url = f"{BASE_URL}/flights?access_key={KEY}&arr_icao={icao}"
            departures_url = f"{BASE_URL}/flights?access_key={KEY}&dep_icao={icao}"

            arrivals_response = requests.get(arrivals_url)
            departures_response = requests.get(departures_url)

            arrivals_json = arrivals_response.json()
            departures_json = departures_response.json()

            print(f"✅ Arrivals: {len(arrivals_json.get('data', []))}")
            print(f"✅ Departures: {len(departures_json.get('data', []))}")

            belt_data = []
            for flight in arrivals_json.get("data", []):
                belt = flight.get("arrival", {}).get("baggage", "N/A")
                flight_num = flight.get("flight", {}).get("iata", "Unknown")
                if belt and belt != "N/A":
                    belt_data.append({"flight": flight_num, "belt": belt})

            dcached_data["arrivals"][icao] = arrivals_json
            dcached_data["departures"][icao] = departures_json
            dcached_data["belt"][icao] = {"belt_info": belt_data}

        except Exception as e:
            print(f"❌ Error for {icao}: {e}")
            return jsonify({"error": str(e)}), 500

    print("✅ Cache refresh complete.")
    return jsonify({"message": "Manual cache updated", "timestamp": str(datetime.now())})

@app.route("/admin/flights")
def flight_list():
    flights = Flight.query.all()
    return render_template("admin/flight_list.html", flights=flights)

@app.route("/admin/flights/new", methods=["GET", "POST"])
def flight_form():
    if request.method == "POST":
        new_flight = Flight(
            flight_number=request.form["flight_number"],
            status=request.form["status"],
            arrival=request.form["arrival"],
            departure=request.form["departure"],
            gate=request.form.get("gate"),
            baggage_belt=request.form.get("baggage_belt")
        )
        db.session.add(new_flight)
        db.session.commit()
        return redirect(url_for("flight_list"))
    return render_template("admin/flight_form.html")

@app.route("/admin/ads")
def ad_list():
    ads = Advertisement.query.all()
    return render_template("admin/ad_list.html", ads=ads)

@app.route("/admin/ads/new", methods=["GET", "POST"])
def ad_form():
    if request.method == "POST":
        new_ad = Advertisement(
            title=request.form["title"],
            media_url=request.form["media_url"],
            media_type=request.form["media_type"]
        )
        db.session.add(new_ad)
        db.session.commit()
        return redirect(url_for("ad_list"))
    return render_template("admin/ad_form.html")

@app.route("/arrivals/<string:icao>")
def get_arrivals(icao):
    return jsonify(dcached_data["arrivals"].get(icao, {"data": []}))

@app.route("/departures/<string:icao>")
def get_departures(icao):
    return jsonify(dcached_data["departures"].get(icao, {"data": []}))

@app.route("/belt/<string:icao>")
def get_belt_info(icao):
    return jsonify(dcached_data["belt"].get(icao, {"belt_info": []}))

if __name__ == "__main__":
    print("🚀 Starting Flask server...")
    app.run(host="0.0.0.0", port=5001, debug=True)
