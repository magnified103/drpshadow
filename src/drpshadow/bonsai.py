from bonsai.parser.base import BaseParser
from bonsai.types import NetworkNode as BonsaiNetworkNode
from drpshadow.ethshadow import EthShadowNetwork
from bonsai import NetworkGenerator
from bonsai.generator import from_config as generator_from_config
from drpshadow.ethshadow import Reliability
from drpshadow.utils import get_drpshadow_root


class IdentityParser(BaseParser):
    def parse(self, network_specification):
        return network_specification


class BonsaiNetwork(EthShadowNetwork):
    def __init__(self, number_of_locations: int):
        super().__init__()

        network_generator = NetworkGenerator(
            parser=IdentityParser(),
            generator=generator_from_config(
                {
                    "type": "default",
                    "config": {
                        "node_generator": {"type": "multinomial", "config": {}},
                        "latency_generator": {
                            "type": "bonsai",
                            "config": {
                                "mode": "most_likely",
                                "batch_size": 100000,
                                "model_path": f"{get_drpshadow_root()}/models/bonsai-gnn-mdn-64-3-0.4-10-knn-20",
                            },
                        },
                    },
                }
            ),
        )

        nodes, edges, latencies = network_generator.generate(
            {"nodes": number_of_locations}
        )

        bonsai_to_str = lambda node: f"{node.get_id():03}-{node.get_country().lower()}-{node.get_asn()}"

        params = [[] for _ in range(len(nodes))]

        for j, edge in enumerate(edges):
            u: BonsaiNetworkNode = nodes[edge[0]]
            v: BonsaiNetworkNode = nodes[edge[1]]
            params[edge[1]].append((bonsai_to_str(u), latencies[j], 0))
            params[edge[0]].append((bonsai_to_str(v), latencies[j], 0))

        for i, node in enumerate(nodes):
            u: BonsaiNetworkNode = node
            params[i].append((bonsai_to_str(u), 5, 0))  # latency to itself is 5ms

            self.add_location(bonsai_to_str(u), params[i])


def get_default_network(number_of_locations: int) -> BonsaiNetwork:
    network = BonsaiNetwork(number_of_locations)

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
    return network
