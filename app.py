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

db.init_app(app)
migrate = Migrate(app, db)

KEY = app.config.get("AVIATIONSTACK_KEY")
BASE_URL = "http://api.aviationstack.com/v1"

cached_data = {
    "arrivals": {},
    "departures": {},
    "belt": {}
}

@app.route("/")
def hello():
    return "\u2705 Flask API is running! Access the live refresh at: <a href=\"https://flightvision.onrender.com/refresh\">/refresh</a>"

@app.route("/view")
def homepage():
    flights = Flight.query.all()
    return render_template("flight.html", flights=flights)

@app.route("/refresh")
def manual_refresh():
    print("\U0001f504 Starting cache refresh and DB sync...")

    for icao in ["VABB"]:
        try:
            print(f"\U0001f310 Fetching data for {icao}...")
            arrivals_url = f"{BASE_URL}/flights?access_key={KEY}&arr_icao={icao}"
            departures_url = f"{BASE_URL}/flights?access_key={KEY}&dep_icao={icao}"

            arrivals_response = requests.get(arrivals_url).json()
            departures_response = requests.get(departures_url).json()

            print(f"\u2705 Arrivals fetched: {len(arrivals_response.get('data', []))}")
            print(f"\u2705 Departures fetched: {len(departures_response.get('data', []))}")

            # Clear previous data
            Flight.query.delete()

            # Insert new flights
            for item in arrivals_response.get("data", []):
                new_flight = Flight(
                    flight_number=item.get("flight", {}).get("iata", "Unknown"),
                    status=item.get("flight_status", "Unknown"),
                    arrival=item.get("arrival", {}).get("airport", "Unknown"),
                    departure=item.get("departure", {}).get("airport", "Unknown"),
                    gate=item.get("departure", {}).get("gate") or item.get("arrival", {}).get("gate"),
                    baggage_belt=item.get("arrival", {}).get("baggage")
                )
                db.session.add(new_flight)
            db.session.commit()

            print("\U0001f4c4 Database updated with new flight data.")

        except Exception as e:
            print(f"\u274c Error during refresh for {icao}: {e}")

    return jsonify({"message": "\u2705 Manual cache update and DB sync complete", "time": str(datetime.now())})

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

if __name__ == "__main__":
    print("\U0001f680 Starting Flask server...")
    app.run(host="0.0.0.0", port=5001, debug=True)
