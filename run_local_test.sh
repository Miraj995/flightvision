#!/bin/bash

# ==========================
# ✈️ FlightVision Render Test Script
# ==========================

# Constants
RENDER_URL="https://flightvision.onrender.com"
REFRESH_ENDPOINT="$RENDER_URL/refresh"
VIEW_PAGE="$RENDER_URL/view"
ADMIN_FLIGHTS="$RENDER_URL/admin/flights"
ADMIN_ADS="$RENDER_URL/admin/ads"

# Database credentials (Render-managed)
DB_USER="flightvision_db_user"
DB_NAME="flightvision_db"
DB_HOST="dpg-d0monu6mcj7s739gfmm0-a.oregon-postgres.render.com"
DB_PASS="VqudVy31XoYxLDkwsCQxlkdHIqgOdn9r"  # Keep secure

# Trigger remote cache refresh
echo "🔄 Triggering manual refresh on Render..."
curl -s "$REFRESH_ENDPOINT"
echo -e "\n✅ Refresh triggered!"

# Optional: view DB contents
echo "📦 Fetching flights from DB:"
PGPASSWORD=$DB_PASS psql -h $DB_HOST -U $DB_USER -d $DB_NAME -c "SELECT * FROM flight;"

echo "📺 Fetching ads from DB:"
PGPASSWORD=$DB_PASS psql -h $DB_HOST -U $DB_USER -d $DB_NAME -c "SELECT * FROM advertisement;"

# Auto open view + admin URLs
echo "🌍 Opening flight info and admin pages..."
xdg-open "$VIEW_PAGE" || open "$VIEW_PAGE"
xdg-open "$ADMIN_FLIGHTS" || open "$ADMIN_FLIGHTS"
xdg-open "$ADMIN_ADS" || open "$ADMIN_ADS"

echo "✅ One-time Render test completed successfully."

