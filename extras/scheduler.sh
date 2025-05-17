#!/bin/bash
cd "$(dirname "$0")"

LOCAL_IP="192.168.29.52"

# 🔪 Kill any Flask processes
fuser -k 5001/tcp > /dev/null 2>&1

# 🔁 Recompile Java
echo "🔨 Rebuilding launcher..."
javac -cp .:lib/json-20231013.jar:lib/dotenv-java.jar -d build java-launcher/com/flightinfo/FlightDisplayLauncher.java
jar cfm FlightDisplayLauncher.jar manifest.txt -C build .

# 🚀 Launch Flask for AviationStack
cd backend-api-avstack
source venv/bin/activate
nohup flask run --host=0.0.0.0 --port=5001 > ../../log-avstack.out 2>&1 &
cd ../
sleep 5

ENDPOINTS=("arrivals" "departures" "belt")
AIRPORTS=("VABB" "VIDP")
INTERVAL=30

while true; do
  for AIRPORT in "${AIRPORTS[@]}"; do
    for MODE in "${ENDPOINTS[@]}"; do
      URL="http://${LOCAL_IP}:5001/${MODE}/${AIRPORT}"
      echo "🌐 Launching: $URL"
      java -cp .:lib/json-20231013.jar:lib/dotenv-java.jar:FlightDisplayLauncher.jar com.flightinfo.FlightDisplayLauncher "$URL"
      sleep $INTERVAL
    done
  done
done

