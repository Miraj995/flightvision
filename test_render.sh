#!/bin/bash

# === CONFIGURATION ===
RENDER_URL="https://flightvision-1.onrender.com"
REFRESH_ENDPOINT="$RENDER_URL/refresh"
VIEW_PAGE="$RENDER_URL/view"
ADS_PAGE="$RENDER_URL/admin/ads"
FLIGHTS_PAGE="$RENDER_URL/admin/flights"
AD_FORM_PAGE="$RENDER_URL/admin/ads/new"
FLIGHT_FORM_PAGE="$RENDER_URL/admin/flights/new"

DB_USER="flightvision_db_user"
DB_NAME="flightvision_db"
DB_HOST="dpg-d0monu6mcj7s739gfmm0-a.oregon-postgres.render.com"
DB_PASS="VqudVy31XoYxLDkwsCQxlkdHIqgOdn9r"  # 🔐 Use ENV or secret manager in prod

echo "🔄 Triggering manual refresh on Render..."
curl -s "$REFRESH_ENDPOINT"
echo -e "\n✅ Refresh complete!\n"

echo "📦 Flight DB Records:"
PGPASSWORD=$DB_PASS psql -h $DB_HOST -U $DB_USER -d $DB_NAME -c "SELECT * FROM flight;"

echo -e "\n🧾 Advertisement DB Records:"
PGPASSWORD=$DB_PASS psql -h $DB_HOST -U $DB_USER -d $DB_NAME -c "SELECT * FROM advertisement;"

echo -e "\n🌐 Opening all key Render pages..."

function open_url() {
    xdg-open "$1" > /dev/null 2>&1 || open "$1"
}

open_url "$VIEW_PAGE"
open_url "$ADS_PAGE"
open_url "$FLIGHTS_PAGE"
open_url "$AD_FORM_PAGE"
open_url "$FLIGHT_FORM_PAGE"

echo -e "\n✅ Render deployment and database check complete."
