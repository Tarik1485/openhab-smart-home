import sys
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "src"))

from lorawan.payload import FarmReading, encode_payload, decode_payload
from zigbee.mesh import build_demo_mesh
from coap.resources import CoAPResourceServer


class LoRaWANPayloadTests(unittest.TestCase):
    def test_binary_round_trip(self):
        reading = FarmReading(
            (42, 39, 45, 51, 47), 23.75, 61, 1013.2, 3.4,
            76, 50.4501, 30.5234, 3850
        )
        self.assertEqual(decode_payload(encode_payload(reading)), reading)

    def test_payload_is_compact(self):
        reading = FarmReading(
            (42, 39, 45, 51, 47), 23.75, 61, 1013.2, 3.4,
            76, 50.4501, 30.5234, 3850
        )
        self.assertEqual(len(encode_payload(reading)), 22)

    def test_rejects_wrong_soil_sensor_count(self):
        reading = FarmReading(
            (42, 39), 23.75, 61, 1013.2, 3.4,
            76, 50.4501, 30.5234, 3850
        )
        with self.assertRaises(ValueError):
            encode_payload(reading)


class ZigbeeMeshTests(unittest.TestCase):
    def test_initial_route_exists(self):
        mesh = build_demo_mesh()
        self.assertIsNotNone(mesh.route("sensor_temp", "coordinator"))

    def test_failed_router_breaks_single_path(self):
        mesh = build_demo_mesh()
        mesh.set_online("router_a", False)
        self.assertIsNone(mesh.route("sensor_temp", "coordinator"))


class CoAPResourceTests(unittest.TestCase):
    def test_get_temperature(self):
        server = CoAPResourceServer()
        self.assertEqual(server.get("/sensors/temperature"), "23.75")

    def test_unknown_resource(self):
        server = CoAPResourceServer()
        with self.assertRaises(KeyError):
            server.get("/sensors/unknown")

    def test_can_control_irrigation(self):
        server = CoAPResourceServer()
        self.assertEqual(server.put("/actuators/irrigation", "ON"), "ON")

    def test_sensor_is_read_only(self):
        server = CoAPResourceServer()
        with self.assertRaises(PermissionError):
            server.put("/sensors/temperature", 30)


if __name__ == "__main__":
    unittest.main()
