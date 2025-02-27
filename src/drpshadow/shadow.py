from yaml import dump
from datetime import datetime
from os.path import abspath
import os

try:
    from yaml import CDumper as Dumper
except ImportError:
    from yaml import Dumper

from drpshadow.network import Network
from drpshadow.host import Host


class DrpShadow:
    def __init__(
        self,
        network: Network,
        stop_time: str,
        data_directory: str = None,
        template_directory: str = None,
    ):
        self.network = network
        self.stop_time = stop_time
        if data_directory is None:
            self.data_directory = abspath(datetime.now().strftime("%y%m%d-%H%M%S"))
        else:
            self.data_directory = abspath(data_directory)

        self.network_path = f"network.gml"
        if template_directory:
            self.template_directory = abspath(template_directory)
        else:
            self.template_directory = None
        self.hosts: list[Host] = []

    def add_host(self, host: Host):
        self.hosts.append(host)

    def generate_yaml(self) -> None:
        config = {
            "general": {
                "stop_time": self.stop_time,
                "progress": True,
                "model_unblocked_syscall_latency": True,
                "data_directory": self.data_directory,
            },
            "network": {
                "use_shortest_path": False,
                "graph": {
                    "type": "gml",
                    "file": {"path": self.network_path},
                },
            },
            "hosts": {},
        }

        if self.template_directory:
            config["general"]["template_directory"] = self.template_directory

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

            config["hosts"][host.name] = host_config

        # os.makedirs(self.data_directory)
        self.network.generate_gml(self.network_path)
        dump(config, open(f"shadow.yaml", "w"), Dumper=Dumper)
