from drpshadow.network.zone import Zone
from drpshadow.network.link import Link
import networkx as nx

__all__ = ["Zone", "Link", "Network"]


class Network:
    def __init__(self, zones: list[Zone] = [], links: list[Link] = []) -> None:
        self.zones = zones
        self.links = links
        self.node_id = 0  # Shadow's node_id counter

        for zone in self.zones:
            zone.node_id = self.node_id
            self.node_id += 1

    def add_zone(self, zone: Zone):
        zone.node_id = self.node_id
        self.node_id += 1
        self.zones.append(zone)

    def add_link(self, link: Link):
        self.links.append(link)

    def generate_gml(self, path: str) -> None:
        G = nx.DiGraph()

        for zone in self.zones:
            G.add_node(
                zone.name,
                host_bandwidth_down=zone.host_bandwidth_down,
                host_bandwidth_up=zone.host_bandwidth_up,
            )

        for link in self.links:
            G.add_edge(
                link.src.name,
                link.dst.name,
                label=f"{link.src.name} to {link.dst.name}",
                latency=f"{round(link.latency * 1000000)} ns",
                packet_loss=link.packet_loss,
            )

        nx.write_gml(G, path)
