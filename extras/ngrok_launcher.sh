#!/bin/bash

# === ngrok_launcher.sh ===
# Securely expose your local FlightVision server to the internet using ngrok

# ------------------------------
# 🔧 Config
LOCAL_PORT=5001
NGROK_BIN="ngrok"  # Or "ngrok" if globally installed
NGROK_LOG="ngrok.log"

echo "🚀 Starting Flask backend on port $LOCAL_PORT..."
cd backend-api-avstack || exit 1
source venv/bin/activate

# Run Flask with 0.0.0.0 so it's accessible externally
nohup flask run --host=0.0.0.0 --port=$LOCAL_PORT > ../../log-avstack.out 2>&1 &
cd ../..

sleep 3  # Give Flask a moment to start

# ------------------------------
# 🌐 Start ngrok
echo "🔗 Launching ngrok tunnel on port $LOCAL_PORT..."
$NGROK_BIN http 0.0.0.0:$LOCAL_PORT --log $NGROK_LOG &
sleep 3

# ------------------------------
# 🌍 Extract ngrok public URL
NGROK_PUBLIC_URL=$(curl -s http://127.0.0.1:4040/api/tunnels \
  | grep -o 'https://[a-zA-Z0-9.-]*ngrok-free.app' \
  | head -n1)

# ------------------------------
# 📣 Show Ready-to-use Public URLs
echo "✅ Public FlightVision Endpoints:"
echo "   📤 Departures: $NGROK_PUBLIC_URL/departures/VABB"
echo "   📥 Arrivals:   $NGROK_PUBLIC_URL/arrivals/VABB"
echo "   🧳 Belt Info:  $NGROK_PUBLIC_URL/belt/VABB"

