from yaml import load, dump
from datetime import datetime
from os.path import abspath

from drpshadow.network import DrpNetworkConfig


class DrpShadowConfig:
    def __init__(self, stop_time: str, data_directory: str = None):
        self.stop_time = stop_time
        if self.data_directory is None:
            self.data_directory = abspath(datetime.now().strftime("%y%m%d-%H%M%S"))
        else:
            self.data_directory = data_directory


class DrpShadow:
    def __init__(
        self, shadow_config: DrpShadowConfig, network_config: DrpNetworkConfig
    ):
        self.network_path = f"{shadow_config.data_directory}/network.gml"
        self.config = {
            "general": {
                "stop_time": shadow_config.stop_time,
                "data_directory": shadow_config.data_directory,
                "progress": True,
                "model_unblocked_syscall_latency": True,
            },
            "network": {
                "use_shortest_path": False,
                "graph": {
                    "type": "gml",
                    "file": {"path": self.network_path},
                },
            },
        }

    def write(self, path: str) -> None:
        pass
