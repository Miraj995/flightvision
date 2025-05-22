from flask import Flask, jsonify, render_template, request, redirect, url_for
from flask_sqlalchemy import SQLAlchemy
from flask_migrate import Migrate
from datetime import datetime
import os
import requests
from dotenv import load_dotenv

from config import Config
from models.db_models import db, Flight, Advertisement

# --- INIT APP ---
app = Flask(__name__)
app.config.from_object(Config)

# --- LOAD .env (for local only) ---
load_dotenv()

# --- Grab API Key securely ---
KEY = os.getenv("AVIATIONSTACK_KEY")
BASE_URL = "http://api.aviationstack.com/v1"

if not KEY:
    print("\n❌ API key not found. Make sure it's set in environment variables.")
else:
    print("\n✅ API key loaded successfully.")

# --- DB Setup ---
db.init_app(app)
migrate = Migrate(app, db)

# --- Flight Cache ---
cached_data = {
    "arrivals": {},
    "departures": {},
    "belt": {}
}

# ========================
#          ROUTES
# ========================

@app.route("/")
def hello():
    return "✅ FlightVision Flask API is live!"

@app.route("/view")
def homepage():
    flights = []
    for icao, data in cached_data["arrivals"].items():
        for item in data.get("data", []):
            flight_info = {
                "flight": item.get("flight", {}).get("iata", "Unknown"),
                "departure": item.get("departure", {}).get("airport", "Unknown"),
                "arrival": item.get("arrival", {}).get("airport", "Unknown"),
                "status": item.get("flight_status", "Unknown"),
                "gate": item.get("departure", {}).get("gate") or item.get("arrival", {}).get("gate") or "N/A"
            }
            flights.append(flight_info)
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
    if not KEY:
        return jsonify({"error": "API key not found"}), 500

    print("\n🔄 Refresh triggered.")
    for icao in ["VABB"]:
        try:
            arr_url = f"{BASE_URL}/flights?access_key={KEY}&arr_icao={icao}"
            dep_url = f"{BASE_URL}/flights?access_key={KEY}&dep_icao={icao}"

            arrivals = requests.get(arr_url).json()
            departures = requests.get(dep_url).json()

            belt_data = []
            for flight in arrivals.get("data", []):
                belt = flight.get("arrival", {}).get("baggage")
                flight_num = flight.get("flight", {}).get("iata", "Unknown")
                if belt and belt != "N/A":
                    belt_data.append({"flight": flight_num, "belt": belt})

            cached_data["arrivals"][icao] = arrivals
            cached_data["departures"][icao] = departures
            cached_data["belt"][icao] = {"belt_info": belt_data}

            print(f"✅ Refreshed {icao}: {len(arrivals.get('data', []))} arrivals")

        except Exception as e:
            print(f"❌ Error refreshing {icao}: {e}")
    return jsonify({"message": "✅ Manual refresh complete", "time": str(datetime.now())})


# ========================
#        ADMIN PANEL
# ========================

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


# ========================
#         RUN
# ========================

if __name__ == "__main__":
    print("\n🚀 Running FlightVision locally...")
    app.run(host="0.0.0.0", port=5001, debug=True)

# For gunicorn deployment (Render expects 'application')
application = app
