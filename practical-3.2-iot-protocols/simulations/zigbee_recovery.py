"""Architecture and test notes for the agricultural IoT simulation."""

from pathlib import Path

root = Path(__file__).resolve().parents[1]
sys_path = root / "src"
import sys
sys.path.insert(0, str(sys_path))

from zigbee.mesh import build_demo_mesh

mesh = build_demo_mesh()
mesh.set_online("router_a", False)
assert mesh.route("sensor_temp", "coordinator") is None

# Simulate rejoining through the available router after a parent failure.
mesh.connect("sensor_temp", "router_b")
recovered_route = mesh.route("sensor_temp", "coordinator")
assert recovered_route is not None

print("Route recovery simulation:", " -> ".join(recovered_route))
