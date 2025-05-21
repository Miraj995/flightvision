#!/bin/bash

# 🌍 Your Render root
BASE_URL="https://flightvision.onrender.com"
ICAO="VABB"

# 🌀 Trigger cache refresh (synchronous)
echo "🔁 Triggering manual refresh..."
curl --silent "$BASE_URL/refresh"

# ⏳ Wait a few seconds to ensure cache is updated
sleep 3

# 🧭 Open HTML dashboard
echo "🌐 Opening /view..."
xdg-open "$BASE_URL/view"

# (Optional) Open JSON endpoints in browser tabs
# xdg-open "$BASE_URL/arrivals/$ICAO"
# xdg-open "$BASE_URL/departures/$ICAO"
# xdg-open "$BASE_URL/belt/$ICAO"

echo "✅ FlightVision launched in browser."

