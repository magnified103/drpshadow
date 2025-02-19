import networkx as nx


class Reliability:
    def __init__(
        self,
        added_latency: int,
        added_packet_loss: float,
        bandwidth_up: str,
        bandwidth_down: str,
    ) -> None:
        self.added_latency = added_latency
        self.added_packet_loss = added_packet_loss
        self.bandwidth_up = bandwidth_up
        self.bandwidth_down = bandwidth_down


class DrpNetworkConfig:
    def __init__(self) -> None:
        self.locations = {}
        self.reliabilities = {}

    def add_location(self, name: str, params: list[tuple[str, int, float]]):
        self.locations[name] = params

    def add_reliability(
        self,
        name: str,
        reliability: Reliability,
    ):
        self.reliabilities[name] = reliability


class DrpNetwork:
    @staticmethod
    def format_node(location_name: str, reliability_name: str) -> str:
        return f"{location_name}-{reliability_name}"

    def __init__(self, config: DrpNetworkConfig) -> None:
        G = nx.DiGraph()
        self.name_mapping = {}
        self.id_mapping = []
        node_id = 0
        for location_name, params in config.locations.items():
            for reliability_name, _ in config.reliabilities.items():
                name = self.format_node(location_name, reliability_name)
                self.name_mapping[name] = node_id
                self.id_mapping.append(name)
                node_id += 1

        for src_location_name, params in config.locations.items():
            for src_reliability_name, src_reliability in config.reliabilities.items():
                src_name = f"{src_location_name}-{src_reliability_name}"
                G.add_node(
                    src_name,
                    host_bandwidth_down=src_reliability.bandwidth_down,
                    host_bandwidth_up=src_reliability.bandwidth_up,
                )
                for dst_location_name, link_latency, link_packet_loss in params:
                    for (
                        dst_reliability_name,
                        dst_reliability,
                    ) in config.reliabilities.items():
                        dst_name = self.format_node(
                            dst_location_name, dst_reliability_name
                        )
                        latency = (
                            link_latency
                            + src_reliability.added_latency
                            + dst_reliability.added_latency
                        )
                        packet_loss = (
                            link_packet_loss
                            + src_reliability.added_packet_loss
                            + dst_reliability.added_packet_loss
                        )
                        G.add_edge(
                            src_name,
                            dst_name,
                            label=f"{src_name} to {dst_name}",
                            latency=f"{latency} ms",
                            packet_loss=packet_loss,
                        )
        self.G = G

    def write(self, path: str) -> None:
        nx.write_gml(self.G, path)


DEFAULT_NETWORK_CONFIG = DrpNetworkConfig()
DEFAULT_NETWORK_CONFIG.add_location(
    "australia",
    [
        ("australia", 2, 0.0),
        ("east_asia", 110, 0.0),
        ("europe", 165, 0.0),
        ("na_west", 110, 0.0),
        ("na_east", 150, 0.0),
        ("south_america", 190, 0.0),
        ("south_africa", 220, 0.0),
        ("west_asia", 180, 0.0),
    ],
)
DEFAULT_NETWORK_CONFIG.add_location(
    "east_asia",
    [
        ("australia", 110, 0.0),
        ("east_asia", 4, 0.0),
        ("europe", 125, 0.0),
        ("na_west", 100, 0.0),
        ("na_east", 140, 0.0),
        ("south_america", 175, 0.0),
        ("south_africa", 175, 0.0),
        ("west_asia", 110, 0.0),
    ],
)
DEFAULT_NETWORK_CONFIG.add_location(
    "europe",
    [
        ("australia", 165, 0.0),
        ("east_asia", 125, 0.0),
        ("europe", 2, 0.0),
        ("na_west", 110, 0.0),
        ("na_east", 70, 0.0),
        ("south_america", 140, 0.0),
        ("south_africa", 95, 0.0),
        ("west_asia", 60, 0.0),
    ],
)
DEFAULT_NETWORK_CONFIG.add_location(
    "na_west",
    [
        ("australia", 110, 0.0),
        ("east_asia", 100, 0.0),
        ("europe", 110, 0.0),
        ("na_west", 2, 0.0),
        ("na_east", 60, 0.0),
        ("south_america", 100, 0.0),
        ("south_africa", 160, 0.0),
        ("west_asia", 150, 0.0),
    ],
)
DEFAULT_NETWORK_CONFIG.add_location(
    "na_east",
    [
        ("australia", 150, 0.0),
        ("east_asia", 140, 0.0),
        ("europe", 70, 0.0),
        ("na_west", 60, 0.0),
        ("na_east", 2, 0.0),
        ("south_america", 100, 0.0),
        ("south_africa", 130, 0.0),
        ("west_asia", 110, 0.0),
    ],
)
DEFAULT_NETWORK_CONFIG.add_location(
    "south_america",
    [
        ("australia", 190, 0.0),
        ("east_asia", 175, 0.0),
        ("europe", 140, 0.0),
        ("na_west", 100, 0.0),
        ("na_east", 100, 0.0),
        ("south_america", 7, 0.0),
        ("south_africa", 195, 0.0),
        ("west_asia", 145, 0.0),
    ],
)
DEFAULT_NETWORK_CONFIG.add_location(
    "south_africa",
    [
        ("australia", 220, 0.0),
        ("east_asia", 175, 0.0),
        ("europe", 95, 0.0),
        ("na_west", 160, 0.0),
        ("na_east", 130, 0.0),
        ("south_america", 190, 0.0),
        ("south_africa", 7, 0.0),
        ("west_asia", 110, 0.0),
    ],
)
DEFAULT_NETWORK_CONFIG.add_location(
    "west_asia",
    [
        ("australia", 180, 0.0),
        ("east_asia", 110, 0.0),
        ("europe", 60, 0.0),
        ("na_west", 150, 0.0),
        ("na_east", 110, 0.0),
        ("south_america", 145, 0.0),
        ("south_africa", 110, 0.0),
        ("west_asia", 5, 0.0),
    ],
)
DEFAULT_NETWORK_CONFIG.add_reliability(
    "reliable",
    Reliability(
        added_latency=0,
        added_packet_loss=0.0,
        bandwidth_up="1 Gbit",
        bandwidth_down="1 Gbit",
    ),
)
DEFAULT_NETWORK_CONFIG.add_reliability(
    "home",
    Reliability(
        added_latency=20,
        added_packet_loss=0.001,
        bandwidth_up="50 Mbit",
        bandwidth_down="50 Mbit",
    ),
)
DEFAULT_NETWORK_CONFIG.add_reliability(
    "constrained",
    Reliability(
        added_latency=20,
        added_packet_loss=0.001,
        bandwidth_up="5 Mbit",
        bandwidth_down="5 Mbit",
    ),
)
DEFAULT_NETWORK_CONFIG.add_reliability(
    "laggy",
    Reliability(
        added_latency=300,
        added_packet_loss=0.05,
        bandwidth_up="50 Mbit",
        bandwidth_down="50 Mbit",
    ),
)
DEFAULT_NETWORK_CONFIG.add_reliability(
    "bad",
    Reliability(
        added_latency=500,
        added_packet_loss=0.2,
        bandwidth_up="2 Mbit",
        bandwidth_down="2 Mbit",
    ),
)

DEFAULT_NETWORK_LOCATIONS = DEFAULT_NETWORK_CONFIG.locations.keys()
DEFAULT_NETWORK_RELIABILITIES = DEFAULT_NETWORK_CONFIG.reliabilities.keys()
