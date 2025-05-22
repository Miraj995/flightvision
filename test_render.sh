#!/bin/bash

# === CONFIG ===
RENDER_URL="https://flightvision.onrender.com"
REFRESH_ENDPOINT="$RENDER_URL/refresh"
VIEW_PAGE="$RENDER_URL/view"
FLIGHT_LIST_PAGE="$RENDER_URL/admin/flights"
FLIGHT_FORM_PAGE="$RENDER_URL/admin/flights/new"
AD_LIST_PAGE="$RENDER_URL/admin/ads"
AD_FORM_PAGE="$RENDER_URL/admin/ads/new"

# Optional DB creds
DB_USER="flightvision_db_user"
DB_NAME="flightvision_db"
DB_HOST="dpg-d0monu6mcj7s739gfmm0-a.oregon-postgres.render.com"
DB_PASS="VqudVy31XoYxLDkwsCQxlkdHIqgOdn9r"

echo "🔄 Triggering /refresh ..."
curl -s "$REFRESH_ENDPOINT"
echo -e "\n✅ Refresh triggered."

# Optional: print DB rows (you need psql installed)
echo "📦 Flight DB entries:"
PGPASSWORD=$DB_PASS psql -h $DB_HOST -U $DB_USER -d $DB_NAME -c "SELECT * FROM flight;" 2>/dev/null

echo "📺 Ad DB entries:"
PGPASSWORD=$DB_PASS psql -h $DB_HOST -U $DB_USER -d $DB_NAME -c "SELECT * FROM advertisement;" 2>/dev/null

# === OPEN RENDER PAGES ===
echo "🌐 Opening all Render URLs in browser..."
xdg-open "$VIEW_PAGE" >/dev/null 2>&1 || open "$VIEW_PAGE"
xdg-open "$FLIGHT_LIST_PAGE" >/dev/null 2>&1 || open "$FLIGHT_LIST_PAGE"
xdg-open "$FLIGHT_FORM_PAGE" >/dev/null 2>&1 || open "$FLIGHT_FORM_PAGE"
xdg-open "$AD_LIST_PAGE" >/dev/null 2>&1 || open "$AD_LIST_PAGE"
xdg-open "$AD_FORM_PAGE" >/dev/null 2>&1 || open "$AD_FORM_PAGE"

echo "✅ All tests executed. UI and DB refreshed."


