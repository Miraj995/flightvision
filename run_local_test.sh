#!/bin/bash

# Set your deployed Render URL
RENDER_URL="https://flightvision.onrender.com"
REFRESH_ENDPOINT="$RENDER_URL/refresh"
VIEW_PAGE="$RENDER_URL/view"

# Postgres credentials (optional: comment out if not testing DB from CLI)
DB_USER="flightvision_db_user"
DB_NAME="flightvision_db"
DB_HOST="dpg-d0monu6mcj7s739gfmm0-a.oregon-postgres.render.com"
DB_PASS="VqudVy31XoYxLDkwsCQxlkdHIqgOdn9r"  # Ensure this is safe/private

echo "🔄 Triggering manual refresh from Render..."
curl -s "$REFRESH_ENDPOINT"
echo -e "\n✅ Refresh complete!"

# Optional: fetch flights from DB (requires psql CLI + password passing)
echo "📦 Fetching flight records from DB:"
PGPASSWORD=$DB_PASS psql -h $DB_HOST -U $DB_USER -d $DB_NAME -c "SELECT * FROM flight;"

echo "🧾 Fetching ads from DB:"
PGPASSWORD=$DB_PASS psql -h $DB_HOST -U $DB_USER -d $DB_NAME -c "SELECT * FROM advertisement;"

# Automatically open browser to Render view page
echo "🌐 Opening flight view page..."
xdg-open "$VIEW_PAGE" || open "$VIEW_PAGE"

echo "✅ One-time Render test completed."

