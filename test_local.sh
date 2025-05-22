#!/bin/bash

# ────────────────[ Configuration ]───────────────
LOCAL_IP="127.0.0.1"
PORT="5001"
URL="http://${LOCAL_IP}:${PORT}"
LOG_FILE="flask_output.log"

echo -e "\033[1;34m🚀 Starting local test at $URL ...\033[0m"

# ────────────────[ Environment Setup ]───────────────
if [ -f .env ]; then
  export $(grep -v '^#' .env | xargs)
  echo -e "\033[1;32m✅ Environment variables loaded.\033[0m"
else
  echo -e "\033[1;31m❌ .env file not found!\033[0m"
  exit 1
fi

# ────────────────[ Kill Previous Flask Instances ]───────────────
pkill -f "flask run" > /dev/null 2>&1

# ────────────────[ Start Flask Server in Background ]───────────────
echo -e "\033[1;34m📡 Starting Flask server on $LOCAL_IP:$PORT...\033[0m"
source venv/bin/activate
export FLASK_APP=app.py
export FLASK_RUN_HOST=$LOCAL_IP
export FLASK_RUN_PORT=$PORT

flask run > "$LOG_FILE" 2>&1 &
FLASK_PID=$!

# ────────────────[ Wait Until Server is Ready ]───────────────
echo -n "⏳ Waiting for Flask to come online "
for i in {1..10}; do
  curl -s "${URL}/" > /dev/null && break
  echo -n "."
  sleep 1
done
echo ""

if curl -s "${URL}/" > /dev/null; then
  echo -e "\033[1;32m✅ Flask server is responsive.\033[0m"
else
  echo -e "\033[1;31m❌ Flask server did not start correctly. Check $LOG_FILE\033[0m"
  kill -9 $FLASK_PID
  exit 1
fi

# ────────────────[ Manual Refresh ]───────────────
echo -e "\033[1;34m🔄 Triggering manual refresh...\033[0m"
curl -s "${URL}/refresh" && echo -e "\033[1;32m✅ Refresh successful.\033[0m"

# ────────────────[ Open in Browser ]───────────────
xdg-open "${URL}/view" > /dev/null 2>&1 || echo "🌐 Open manually: ${URL}/view"

# ────────────────[ Graceful Shutdown ]───────────────
sleep 10
echo -e "\033[1;33m🛑 Shutting down local server...\033[0m"
kill -9 $FLASK_PID
echo -e "\033[1;32m✅ Test complete. Logs saved to $LOG_FILE\033[0m"

