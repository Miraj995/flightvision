#!/bin/bash

# Set your deployed Render URL
RENDER_URL="https://flightvision.onrender.com"
REFRESH_ENDPOINT="$RENDER_URL/refresh"

# ========== 1. TRIGGER MANUAL REFRESH ==========
echo "🔁 Triggering /refresh ..."
curl -s "$REFRESH_ENDPOINT"
echo -e "\n✅ Refresh triggered."

# ========== 2. CHECK ROUTES ==========
echo -e "\n🧪 Testing route availability (status codes):"
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
    echo "$STATUS ← $ENDPOINT"
done

# ========== 3. OPEN ROUTES IN BROWSER ==========
echo -e "\n🌐 Opening all pages..."
for ENDPOINT in "${ENDPOINTS[@]}"; do
    xdg-open "$RENDER_URL$ENDPOINT" >/dev/null 2>&1 &
done

echo -e "\n✅ Render test complete. All tabs should be open."

