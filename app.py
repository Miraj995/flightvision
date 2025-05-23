from flask import Flask, render_template, request, redirect, url_for, jsonify
from flask_sqlalchemy import SQLAlchemy
from flask_migrate import Migrate
from datetime import datetime
import requests
import os

# --- Load environment vars (Render injects them) ---
class Config:
    SQLALCHEMY_DATABASE_URI = os.getenv("DATABASE_URL")
    SQLALCHEMY_TRACK_MODIFICATIONS = False
    SECRET_KEY = os.getenv("SECRET_KEY")
    AVIATIONSTACK_KEY = os.getenv("AVIATIONSTACK_KEY")

# --- App & DB Init ---
app = Flask(__name__)
app.config.from_object(Config)

db = SQLAlchemy(app)
migrate = Migrate(app, db)

# --- Models ---
class Flight(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    flight_number = db.Column(db.String(10), nullable=False)
    status = db.Column(db.String(50))
    arrival = db.Column(db.String(100))
    departure = db.Column(db.String(100))
    gate = db.Column(db.String(10))
    baggage_belt = db.Column(db.String(10))

class Advertisement(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(100), nullable=False)
    media_url = db.Column(db.String(255), nullable=False)
    media_type = db.Column(db.String(50), nullable=False)

# --- API Key Check ---
API_KEY = app.config.get("AVIATIONSTACK_KEY")
BASE_URL = "http://api.aviationstack.com/v1"

if not API_KEY:
    print("❌ API Key not found. Make sure it's in Render ENV variables.")
else:
    print("✅ API key loaded successfully.")

# --- Cache ---
cached_data = {
    "arrivals": {},
    "departures": {},
    "belt": {}
}

# ====================
#        ROUTES
# ====================
@app.route("/")
def root():
    return "✅ FlightVision service is running."

@app.route("/view")
def view():
    flights = []
    for icao, data in cached_data["arrivals"].items():
        for item in data.get("data", []):
            flights.append({
                "flight": item.get("flight", {}).get("iata"),
                "departure": item.get("departure", {}).get("airport"),
                "arrival": item.get("arrival", {}).get("airport"),
                "status": item.get("flight_status"),
                "gate": item.get("departure", {}).get("gate") or "N/A"
            })
    return render_template("flight.html", flights=flights)

@app.route("/refresh")
def refresh():
    if not API_KEY:
        return jsonify({"error": "API key missing."}), 500

    print("🔄 Refresh triggered")
    for icao in ["VABB"]:
        try:
            arrivals = requests.get(f"{BASE_URL}/flights?access_key={API_KEY}&arr_icao={icao}").json()
            departures = requests.get(f"{BASE_URL}/flights?access_key={API_KEY}&dep_icao={icao}").json()
            belt_info = []
            for flight in arrivals.get("data", []):
                belt = flight.get("arrival", {}).get("baggage")
                if belt and belt != "N/A":
                    belt_info.append({"flight": flight.get("flight", {}).get("iata"), "belt": belt})

            cached_data["arrivals"][icao] = arrivals
            cached_data["departures"][icao] = departures
            cached_data["belt"][icao] = {"belt_info": belt_info}

            print(f"✅ {icao} refreshed with {len(arrivals.get('data', []))} flights.")
        except Exception as e:
            print(f"❌ Failed to fetch data: {e}")

    return jsonify({"message": "Refreshed", "timestamp": str(datetime.now())})

# ====================
#        Admin
# ====================
@app.route("/admin/flights")
def admin_flights():
    flights = Flight.query.all()
    return render_template("admin/flight_list.html", flights=flights)

@app.route("/admin/flights/new", methods=["GET", "POST"])
def add_flight():
    if request.method == "POST":
        f = Flight(
            flight_number=request.form["flight_number"],
            status=request.form["status"],
            arrival=request.form["arrival"],
            departure=request.form["departure"],
            gate=request.form.get("gate"),
            baggage_belt=request.form.get("baggage_belt")
        )
        db.session.add(f)
        db.session.commit()
        return redirect(url_for("admin_flights"))
    return render_template("admin/flight_form.html")

@app.route("/admin/ads")
def admin_ads():
    ads = Advertisement.query.all()
    return render_template("admin/ad_list.html", ads=ads)

@app.route("/admin/ads/new", methods=["GET", "POST"])
def add_ad():
    if request.method == "POST":
        a = Advertisement(
            title=request.form["title"],
            media_url=request.form["media_url"],
            media_type=request.form["media_type"]
        )
        db.session.add(a)
        db.session.commit()
        return redirect(url_for("admin_ads"))
    return render_template("admin/ad_form.html")

@app.before_first_request
def show_routes():
    print("🔧 Flask Registered Routes (Runtime):")
    print(app.url_map)

if __name__ == "__main__":
app.run(host="0.0.0.0", port=5001, debug=True)

