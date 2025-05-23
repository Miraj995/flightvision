#!/bin/bash

# ========== CONFIGURATION ==========
RENDER_URL="https://flightvision.onrender.com"
REFRESH_ENDPOINT="$RENDER_URL/refresh"
VIEW_PAGE="$RENDER_URL/view"

# Optional Postgres credentials
DB_USER="flightvision_db_user"
DB_NAME="flightvision_db"
DB_HOST="dpg-d0monu6mcj7s739gfmm0-a.oregon-postgres.render.com"
DB_PASS="VqudVy31XoYxLDkwsCQxlkdHIqgOdn9r"  # Private: do not commit

# ========== 1. TRIGGER MANUAL REFRESH ==========
echo "🔄 Triggering /refresh ..."
curl -s "$REFRESH_ENDPOINT"
echo -e "\n✅ Refresh triggered."

# ========== 2. CHECK ROUTES ==========
echo -e "\n🔎 Testing route availability (status codes):"
ENDPOINTS=(
  "/view"
  "/admin/flights"
  "/admin/flights/new"
  "/admin/ads"
  "/admin/ads/new"
)

for ENDPOINT in "${ENDPOINTS[@]}"; do
    FULL_URL="$RENDER_URL$ENDPOINT"
    STATUS=$(curl -s -o /dev/null -w "%{http_code}" "$FULL_URL")
    echo "$STATUS  ←  $ENDPOINT"
done

# ========== 3. OPTIONAL DB TESTS ==========
echo -e "\n🛢️ Checking DB for records..."
PGPASSWORD=$DB_PASS psql -h $DB_HOST -U $DB_USER -d $DB_NAME -c "SELECT COUNT(*) FROM flight;"
PGPASSWORD=$DB_PASS psql -h $DB_HOST -U $DB_USER -d $DB_NAME -c "SELECT COUNT(*) FROM advertisement;"

# ========== 4. OPEN MAIN VIEW ==========
echo -e "\n🌐 Opening flight info page..."
xdg-open "$VIEW_PAGE" || open "$VIEW_PAGE"

echo -e "\n✅ Render test complete.\n"

