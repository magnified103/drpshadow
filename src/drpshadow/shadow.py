from yaml import dump
import shadowtools.config as scfg
from os.path import abspath

try:
    from yaml import CDumper as Dumper
except ImportError:
    from yaml import Dumper

from drpshadow.network import Network
from drpshadow.host import Host


class DrpShadow:
    def __init__(self, network: Network, output: str):
        self.network = network
        self.hosts: list[Host] = []
        self.output = output
        self.config = scfg.Config(
            general=scfg.General(
                stop_time="90 sec",
                progress=True,
                model_unblocked_syscall_latency=True,
            ),
            network=scfg.Network(
                use_shortest_path=False,
                graph=scfg.Graph(
                    type="gml",
                    file=scfg.GraphFile(path=abspath(f"{self.output}/network.gml")),
                ),
            ),
            hosts={},
        )

    def add_host(self, host: Host):
        self.hosts.append(host)

    def generate_yaml(self, path) -> None:
        for host in self.hosts:
            host_config = {
                "ip_addr": host.ip_addr,
                "network_node_id": host.network_node_id,
                "processes": host.processes,
            }
            if host.bandwidth_down:
                host_config["bandwidth_down"] = host.bandwidth_down
            if host.bandwidth_up:
                host_config["bandwidth_up"] = host.bandwidth_up

            self.config["hosts"][host.name] = host_config

        # os.makedirs(self.data_directory)
        self.network.generate_gml(abspath(f"{self.output}/network.gml"))
        dump(self.config, open(path, "w"), Dumper=Dumper)
