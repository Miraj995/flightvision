package com.flightinfo;

import java.awt.Desktop;
import java.io.*;
import java.net.HttpURLConnection;
import java.net.URI;
import java.net.URL;
import java.util.logging.*;
import java.util.stream.Collectors;

import org.json.*;
import io.github.cdimascio.dotenv.Dotenv;

public class FlightDisplayLauncher {
    private static final Logger logger = Logger.getLogger(FlightDisplayLauncher.class.getName());

    public static void main(String[] args) {
        logger.setLevel(Level.ALL);
        ConsoleHandler handler = new ConsoleHandler();
        handler.setLevel(Level.ALL);
        logger.addHandler(handler);

        if (args.length == 0) {
            System.out.println("⚠️  No API URL provided.");
            System.out.println("Usage: java -jar FlightDisplayLauncher.jar <full-api-url>");
            System.out.println("🔗 Example:");
            System.out.println("    java -jar FlightDisplayLauncher.jar \"http://192.168.29.52:5001/arrivals/VABB\"");
            return;
        }

        Dotenv dotenv = Dotenv.configure()
            .directory(System.getProperty("user.dir"))
            .filename(".env")
            .ignoreIfMalformed()
            .ignoreIfMissing()
            .load();

        final String API_KEY = dotenv.get("AVIATIONSTACK_KEY");

        if (API_KEY == null || API_KEY.isBlank()) {
            logger.severe("❌ AVIATIONSTACK_KEY is missing in .env");
            return;
        }

        String targetUrl = args[0];
        logger.info("📡 Fetching flight data from: " + targetUrl);

        try {
            String json = fetchJsonFromUrl(targetUrl, API_KEY);
            logger.fine("🔍 Raw JSON: " + json);

            String html = generateHtmlFromJson(json);

            File htmlFile = new File("flight.html");
            try (FileWriter writer = new FileWriter(htmlFile)) {
                writer.write(html);
                logger.info("✅ HTML output written to: flight.html");
            }

            if (Desktop.isDesktopSupported()) {
                Desktop.getDesktop().browse(htmlFile.toURI());
                logger.info("🌐 Opened flight.html in default browser.");
            } else {
                logger.warning("⚠️  Desktop browsing not supported on this system.");
            }

        } catch (Exception e) {
            logger.log(Level.SEVERE, "💥 Error during execution: " + e.getMessage(), e);
        }
    }

    private static String fetchJsonFromUrl(String urlString, String apiKey) throws Exception {
        URL url = URI.create(urlString + "?access_key=" + apiKey).toURL();
        HttpURLConnection conn = (HttpURLConnection) url.openConnection();
        conn.setRequestMethod("GET");

        logger.fine("➡️  Request sent to: " + url.toString());

        BufferedReader in = new BufferedReader(new InputStreamReader(conn.getInputStream()));
        String content = in.lines().collect(Collectors.joining());
        in.close();
        conn.disconnect();

        return content;
    }

    private static String generateHtmlFromJson(String json) {
        StringBuilder html = new StringBuilder();
        html.append("""
    <html>
    <head>
        <title>Flight Info</title>
        <style>
            body { font-family: Arial, sans-serif; margin: 20px; position: relative; }
            table { border-collapse: collapse; width: 100%; margin-top: 20px; }
            th, td { border: 1px solid #ccc; padding: 8px; text-align: left; }
            th { background-color: #f2f2f2; }
            #clock {
                position: absolute;
                top: 20px;
                right: 20px;
                font-size: 18px;
                font-weight: bold;
                color: #333;
            }
        </style>
        <script>
            function updateClock() {
                const now = new Date();
                const time = now.toLocaleTimeString();
                document.getElementById('clock').textContent = time;
            }
            setInterval(updateClock, 1000);
            window.onload = updateClock;
        </script>
    </head>
    <body>
    <div id="clock"></div>
    <h2>Live Flight Data</h2>
    <table>
    <tr><th>Flight</th><th>Departure</th><th>Arrival</th><th>Status</th><th>Gate</th></tr>
""");


        JSONObject jsonObj = new JSONObject(json);
        JSONArray flights = jsonObj.optJSONArray("data");

        if (flights != null && flights.length() > 0) {
            for (int i = 0; i < Math.min(flights.length(), 20); i++) {
                JSONObject flight = flights.getJSONObject(i);
                String flightNum = flight.optJSONObject("flight").optString("iata", "N/A");
                String dep = flight.optJSONObject("departure").optString("airport", "N/A");
                String arr = flight.optJSONObject("arrival").optString("airport", "N/A");
                String status = flight.optString("flight_status", "N/A");
                String gate = flight.optJSONObject("departure").optString("gate", "N/A");

                html.append("<tr>")
                    .append("<td>").append(flightNum).append("</td>")
                    .append("<td>").append(dep).append("</td>")
                    .append("<td>").append(arr).append("</td>")
                    .append("<td>").append(status).append("</td>")
                    .append("<td>").append(gate).append("</td>")
                    .append("</tr>");
            }
        } else {
            html.append("<tr><td colspan='5'>No flight data available</td></tr>");
            logger.warning("⚠️  No flights found in JSON response.");
        }

        html.append("</table></body></html>");
        return html.toString();
    }
}
