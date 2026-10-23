"""Educational Zigbee mesh topology and route recovery simulation."""
from collections import deque
from dataclasses import dataclass, field


@dataclass
class ZigbeeNode:
    node_id: str
    role: str
    neighbors: set[str] = field(default_factory=set)
    online: bool = True
    battery_pct: int = 100


class ZigbeeMesh:
    def __init__(self):
        self.nodes: dict[str, ZigbeeNode] = {}

    def add_node(self, node_id: str, role: str, battery_pct: int = 100):
        if role not in {"coordinator", "router", "end_device"}:
            raise ValueError("Invalid Zigbee role")
        if node_id in self.nodes:
            raise ValueError(f"Node already exists: {node_id}")
        if not 0 <= battery_pct <= 100:
            raise ValueError("Battery must be between 0 and 100")
        if role == "coordinator" and any(
            n.role == "coordinator" for n in self.nodes.values()
        ):
            raise ValueError("Only one coordinator is supported")
        self.nodes[node_id] = ZigbeeNode(node_id, role, battery_pct=battery_pct)

    def connect(self, first: str, second: str):
        a, b = self.nodes[first], self.nodes[second]
        if not a.online or not b.online:
            raise ValueError("Both nodes must be online to connect")
        if a.role == "end_device" and b.role == "end_device":
            raise ValueError("End devices cannot route traffic for each other")
        a.neighbors.add(second)
        b.neighbors.add(first)

    def set_online(self, node_id: str, online: bool):
        self.nodes[node_id].online = online

    def route(self, source: str, destination: str) -> list[str] | None:
        """Return a shortest online route, or None if no route exists."""
        if source not in self.nodes or destination not in self.nodes:
            return None
        if not self.nodes[source].online or not self.nodes[destination].online:
            return None

        queue = deque([[source]])
        visited = {source}
        while queue:
            path = queue.popleft()
            current = path[-1]
            if current == destination:
                return path
            node = self.nodes[current]
            if node.role == "end_device" and current != source:
                continue
            for neighbor_id in sorted(node.neighbors):
                neighbor = self.nodes[neighbor_id]
                if neighbor.online and neighbor_id not in visited:
                    visited.add(neighbor_id)
                    queue.append(path + [neighbor_id])
        return None

    def topology(self) -> dict[str, list[str]]:
        return {
            node_id: sorted(node.neighbors)
            for node_id, node in sorted(self.nodes.items())
        }


def build_demo_mesh() -> ZigbeeMesh:
    mesh = ZigbeeMesh()
    mesh.add_node("coordinator", "coordinator")
    mesh.add_node("router_a", "router")
    mesh.add_node("router_b", "router")
    mesh.add_node("sensor_temp", "end_device", 92)
    mesh.add_node("sensor_light", "end_device", 85)
    mesh.add_node("irrigation", "end_device", 78)

    mesh.connect("coordinator", "router_a")
    mesh.connect("coordinator", "router_b")
    mesh.connect("router_a", "router_b")
    mesh.connect("router_a", "sensor_temp")
    mesh.connect("router_b", "sensor_light")
    mesh.connect("router_b", "irrigation")
    return mesh


if __name__ == "__main__":
    network = build_demo_mesh()
    print("Initial route:", network.route("sensor_temp", "coordinator"))
    network.set_online("router_a", False)
    print("After router_a failure:", network.route("sensor_temp", "coordinator"))
    print("Topology:", network.topology())
