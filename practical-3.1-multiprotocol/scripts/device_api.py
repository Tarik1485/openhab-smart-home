import json
import random
from datetime import datetime, timezone
from http.server import BaseHTTPRequestHandler, HTTPServer
from urllib.parse import urlparse


class DeviceAPI(BaseHTTPRequestHandler):
    def do_GET(self):
        path = urlparse(self.path).path

        if path == "/api/weather/current":
            data = {
                "temperature": round(random.uniform(18, 28), 1),
                "humidity": round(random.uniform(30, 75), 1),
                "pressure": round(random.uniform(990, 1035), 1),
                "timestamp": datetime.now(timezone.utc).isoformat()
            }
        elif path == "/api/weather/status":
            data = {"status": "ONLINE", "protocol": "HTTP"}
        elif path == "/api/devices":
            data = {
                "devices": [
                    {"name": "Weather Station", "protocol": "MQTT"},
                    {"name": "Weather API", "protocol": "HTTP"},
                    {"name": "BLE Temperature Sensor", "protocol": "BLE emulator"}
                ]
            }
        elif path == "/api/ble/scan":
            data = {
                "device": "BLE-THERMOMETER-01",
                "protocol": "BLE emulator",
                "temperature": round(random.uniform(18, 28), 1),
                "rssi": random.randint(-90, -35)
            }
        else:
            self.send_error(404, "Endpoint not found")
            return

        body = json.dumps(data, ensure_ascii=False).encode("utf-8")
        self.send_response(200)
        self.send_header("Content-Type", "application/json; charset=utf-8")
        self.send_header("Content-Length", str(len(body)))
        self.end_headers()
        self.wfile.write(body)

    def log_message(self, format, *args):
        print(f"[HTTP] {args[0]}")


if __name__ == "__main__":
    print("HTTP API started at http://127.0.0.1:8090")
    print("Endpoints: /api/weather/current, /api/weather/status,")
    print("           /api/devices, /api/ble/scan")
    HTTPServer(("127.0.0.1", 8090), DeviceAPI).serve_forever()
