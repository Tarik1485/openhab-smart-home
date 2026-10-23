import json
import unittest
from urllib.request import urlopen

BASE_URL = "http://127.0.0.1:8090"


def get_json(path):
    with urlopen(BASE_URL + path, timeout=3) as response:
        assert response.status == 200
        return json.loads(response.read().decode("utf-8"))


class DeviceAPITests(unittest.TestCase):
    def test_weather_current(self):
        data = get_json("/api/weather/current")
        self.assertIn("temperature", data)
        self.assertIn("humidity", data)
        self.assertIn("pressure", data)
        self.assertIn("timestamp", data)
        self.assertGreaterEqual(data["temperature"], 18)
        self.assertLessEqual(data["temperature"], 28)

    def test_weather_status(self):
        data = get_json("/api/weather/status")
        self.assertEqual(data["status"], "ONLINE")
        self.assertEqual(data["protocol"], "HTTP")

    def test_devices_list(self):
        data = get_json("/api/devices")
        self.assertEqual(len(data["devices"]), 3)
        protocols = {device["protocol"] for device in data["devices"]}
        self.assertIn("MQTT", protocols)
        self.assertIn("HTTP", protocols)
        self.assertIn("BLE emulator", protocols)

    def test_ble_emulator(self):
        data = get_json("/api/ble/scan")
        self.assertEqual(data["device"], "BLE-THERMOMETER-01")
        self.assertEqual(data["protocol"], "BLE emulator")
        self.assertGreaterEqual(data["temperature"], 18)
        self.assertLessEqual(data["temperature"], 28)
        self.assertGreaterEqual(data["rssi"], -90)
        self.assertLessEqual(data["rssi"], -35)


if __name__ == "__main__":
    unittest.main(verbosity=2)
