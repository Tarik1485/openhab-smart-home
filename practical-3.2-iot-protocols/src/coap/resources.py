"""Small in-memory CoAP resource model for educational simulations.

This models resource lookup and GET/PUT behavior. It is not a full RFC 7252
network server and does not implement UDP, Observe, or block-wise transfer.
"""
import json


class CoAPResourceServer:
    def __init__(self):
        self.resources = {
            "/sensors/temperature": 23.75,
            "/sensors/humidity": 61,
            "/sensors/soil-moisture": [42, 39, 45, 51, 47],
            "/sensors/light-level": 720,
            "/sensors/battery-status": 3850,
            "/actuators/irrigation": "OFF",
            "/actuators/ventilation": "OFF",
            "/actuators/heating": "OFF",
            "/diagnostics/network-stats": {"rssi": -80, "packet_loss_pct": 1.2},
            "/diagnostics/error-log": [],
            "/diagnostics/performance": {"sleep_pct": 98},
        }

    def get(self, path: str, accept: str = "json") -> str:
        if path not in self.resources:
            raise KeyError(f"Resource not found: {path}")
        value = self.resources[path]
        if accept == "json":
            return json.dumps(value)
        if accept == "text":
            return str(value)
        if accept == "plain":
            return str(value)
        raise ValueError("Supported formats: json, text, plain")

    def put(self, path: str, value):
        if path not in self.resources:
            raise KeyError(f"Resource not found: {path}")
        if path.startswith("/sensors/") or path.startswith("/diagnostics/"):
            raise PermissionError("Sensor and diagnostic resources are read-only")
        if path.startswith("/actuators/") and value not in {"ON", "OFF"}:
            raise ValueError("Actuator state must be ON or OFF")
        self.resources[path] = value
        return self.resources[path]


if __name__ == "__main__":
    server = CoAPResourceServer()
    print("Temperature:", server.get("/sensors/temperature"))
    print("Soil moisture:", server.get("/sensors/soil-moisture"))
    print("Irrigation:", server.put("/actuators/irrigation", "ON"))
    print("Network stats:", server.get("/diagnostics/network-stats"))
