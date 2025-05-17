#!/bin/bash

echo "🧹 Cleaning build directory..."
rm -rf build
mkdir build

echo "🛠️ Compiling Java..."
javac -d build java-launcher/com/flightinfo/FlightDisplayLauncher.java

echo "📦 Creating executable JAR..."
jar cfm FlightDisplayLauncher.jar manifest.txt -C build .

echo "▶️ Starting Full System Scheduler..."
chmod +x scheduler.sh
./scheduler.sh
