#!/bin/bash

# 🌐 Base URL of your deployed app on Render
BASE_URL="https://flightvision.onrender.com"
ICAO="VABB"

# 🧼 Trigger a manual cache refresh
echo "🔁 Triggering cache refresh..."
curl --silent "$BASE_URL/refresh"

# 🌍 Open Render endpoints in default browser
xdg-open "$BASE_URL/view"
xdg-open "$BASE_URL/arrivals/$ICAO"
xdg-open "$BASE_URL/departures/$ICAO"
xdg-open "$BASE_URL/belt/$ICAO"

echo "✅ All endpoints opened in your browser."

