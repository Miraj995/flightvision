#!/bin/bash

echo "🚀 Starting one-time refresh test"

# Activate virtual environment
source venv/bin/activate

# Run Flask app in the background
export FLASK_APP=app.py
flask run --port=5001 > flask.log 2>&1 &
FLASK_PID=$!
sleep 2

# Trigger one-time cache refresh
curl http://127.0.0.1:5001/refresh
echo ""
echo "✅ Refresh complete!"

# Query flight records from DB
echo "📦 Fetching flight records from DB:"
PGPASSWORD=securepass psql -U miraj -h localhost -d flightvision_db -c "SELECT * FROM flight;"

# Query advertisements
echo "🧾 Fetching ads from DB:"
PGPASSWORD=securepass psql -U miraj -h localhost -d flightvision_db -c "SELECT * FROM advertisement;"

# Kill the Flask server
echo "🛑 Shutting down Flask app..."
kill $FLASK_PID

echo "✅ One-time run complete."

