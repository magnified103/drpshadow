from drpshadow.network.zone import Zone
from drpshadow.network.link import Link
from drpshadow.network import Network


class Reliability:
    def __init__(
        self,
        name: str,
        added_latency: int,
        added_packet_loss: float,
        bandwidth_up: str,
        bandwidth_down: str,
    ) -> None:
        self.name = name
        self.added_latency = added_latency
        self.added_packet_loss = added_packet_loss
        self.bandwidth_up = bandwidth_up
        self.bandwidth_down = bandwidth_down


class EthShadowZone(Zone):
    def __init__(
        self,
        location_name: str,
        reliability: Reliability,
        address_range: str | int,
    ) -> None:
        super().__init__(
            f"{location_name}-{reliability.name}",
            reliability.bandwidth_down,
            reliability.bandwidth_up,
            address_range,
        )
        self.location_name = location_name
        self.reliability_name = reliability.name


class EthShadowNetwork(Network):
    def __init__(self) -> None:
        super().__init__()
        self.locations = {}
        self.reliabilities: list[Reliability] = []

    def add_location(self, name: str, params: list[tuple[str, float, float]]):
        if name in self.locations:
            raise ValueError(f"Location {name} already exists")
        self.locations[name] = params

    def add_reliability(self, reliability: Reliability):
        self.reliabilities.append(reliability)

    def filter_zones(
        self,
        location: str = None,
        location__in: list[str] = None,
        reliability: str = None,
        reliability__in: list[str] = None,
    ):
        for zone in self.zones:
            if (
                (location is None or zone.location_name == location)
                and (location__in is None or zone.location_name in location__in)
                and (reliability is None or zone.reliability_name == reliability)
                and (
                    reliability__in is None or zone.reliability_name in reliability__in
                )
            ):
                yield zone

    def build_zones_and_links(self):
        zone_mapping = {}

        for i, (location_name, _) in enumerate(self.locations.items()):
            for j, reliability in enumerate(self.reliabilities):
                zone = EthShadowZone(location_name, reliability, f"11.{i}.{j}.0/24")
                self.add_zone(zone)
                zone_mapping[location_name, reliability.name] = zone

        for src_location_name, params in self.locations.items():
            for src_reliability in self.reliabilities:
                for dst_location_name, link_latency, link_packet_loss in params:
                    for dst_reliability in self.reliabilities:
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

                        src_zone = zone_mapping[src_location_name, src_reliability.name]
                        dst_zone = zone_mapping[dst_location_name, dst_reliability.name]

                        self.add_link(Link(src_zone, dst_zone, latency, packet_loss))


def get_default_network() -> EthShadowNetwork:
    network = EthShadowNetwork()
    network.add_location(
        "australia",
        [
            ("australia", 2, 0.0),
            ("east-asia", 110, 0.0),
            ("europe", 165, 0.0),
            ("na-west", 110, 0.0),
            ("na-east", 150, 0.0),
            ("south-america", 190, 0.0),
            ("south-africa", 220, 0.0),
            ("west-asia", 180, 0.0),
        ],
    )
    network.add_location(
        "east-asia",
        [
            ("australia", 110, 0.0),
            ("east-asia", 4, 0.0),
            ("europe", 125, 0.0),
            ("na-west", 100, 0.0),
            ("na-east", 140, 0.0),
            ("south-america", 175, 0.0),
            ("south-africa", 175, 0.0),
            ("west-asia", 110, 0.0),
        ],
    )
    network.add_location(
        "europe",
        [
            ("australia", 165, 0.0),
            ("east-asia", 125, 0.0),
            ("europe", 2, 0.0),
            ("na-west", 110, 0.0),
            ("na-east", 70, 0.0),
            ("south-america", 140, 0.0),
            ("south-africa", 95, 0.0),
            ("west-asia", 60, 0.0),
        ],
    )
    network.add_location(
        "na-west",
        [
            ("australia", 110, 0.0),
            ("east-asia", 100, 0.0),
            ("europe", 110, 0.0),
            ("na-west", 2, 0.0),
            ("na-east", 60, 0.0),
            ("south-america", 100, 0.0),
            ("south-africa", 160, 0.0),
            ("west-asia", 150, 0.0),
        ],
    )
    network.add_location(
        "na-east",
        [
            ("australia", 150, 0.0),
            ("east-asia", 140, 0.0),
            ("europe", 70, 0.0),
            ("na-west", 60, 0.0),
            ("na-east", 2, 0.0),
            ("south-america", 100, 0.0),
            ("south-africa", 130, 0.0),
            ("west-asia", 110, 0.0),
        ],
    )
    network.add_location(
        "south-america",
        [
            ("australia", 190, 0.0),
            ("east-asia", 175, 0.0),
            ("europe", 140, 0.0),
            ("na-west", 100, 0.0),
            ("na-east", 100, 0.0),
            ("south-america", 7, 0.0),
            ("south-africa", 195, 0.0),
            ("west-asia", 145, 0.0),
        ],
    )
    network.add_location(
        "south-africa",
        [
            ("australia", 220, 0.0),
            ("east-asia", 175, 0.0),
            ("europe", 95, 0.0),
            ("na-west", 160, 0.0),
            ("na-east", 130, 0.0),
            ("south-america", 190, 0.0),
            ("south-africa", 7, 0.0),
            ("west-asia", 110, 0.0),
        ],
    )
    network.add_location(
        "west-asia",
        [
            ("australia", 180, 0.0),
            ("east-asia", 110, 0.0),
            ("europe", 60, 0.0),
            ("na-west", 150, 0.0),
            ("na-east", 110, 0.0),
            ("south-america", 145, 0.0),
            ("south-africa", 110, 0.0),
            ("west-asia", 5, 0.0),
        ],
    )
    network.add_reliability(
        Reliability(
            "reliable",
            added_latency=0,
            added_packet_loss=0.0,
            bandwidth_up="1 Gbit",
            bandwidth_down="1 Gbit",
        ),
    )
    network.add_reliability(
        Reliability(
            "home",
            added_latency=20,
            added_packet_loss=0.001,
            bandwidth_up="50 Mbit",
            bandwidth_down="50 Mbit",
        ),
    )
    network.add_reliability(
        Reliability(
            "constrained",
            added_latency=20,
            added_packet_loss=0.001,
            bandwidth_up="5 Mbit",
            bandwidth_down="5 Mbit",
        ),
    )
    network.add_reliability(
        Reliability(
            "laggy",
            added_latency=300,
            added_packet_loss=0.05,
            bandwidth_up="50 Mbit",
            bandwidth_down="50 Mbit",
        ),
    )
    network.add_reliability(
        Reliability(
            "bad",
            added_latency=500,
            added_packet_loss=0.2,
            bandwidth_up="2 Mbit",
            bandwidth_down="2 Mbit",
        ),
    )
    return network
