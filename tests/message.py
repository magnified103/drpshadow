from drpshadow import *
from copy import deepcopy
from yaml import load, dump
import os

try:
    from yaml import CLoader as Loader, CDumper as Dumper
except ImportError:
    from yaml import Loader, Dumper

network = DrpNetwork(deepcopy(DEFAULT_CONFIG))

network.write("network.gml")

config = {
    "general": {
        "stop_time": "2 min",
        "progress": True,
        "model_unblocked_syscall_latency": True,
    },
    "network": {
        "use_shortest_path": False,
        "graph": {
            "type": "gml",
            "file": {"path": "network.gml"},
        },
    },
    "hosts": {},
}

cwd = os.path.dirname(os.path.realpath(__file__))

for i in range(8):
    ip_addr = f"11.{i}.0.1"
    config["hosts"][f"bootstrap{i:02}"] = {
        "ip_addr": ip_addr,
        "network_node_id": i * 5,
        "processes": [
            {
                "path": "/usr/bin/node",
                "args": f"{cwd}/bootstrap.js --ip {ip_addr} --seed bootstrap{i:02}",
                "environment": {"DEBUG": "libp2p:*yamux*"},
                "expected_final_state": "running",
            }
        ],
    }

for i in range(40):
    node_id = i % 40
    ip_addr = f"12.{node_id//5}.{node_id%5}.{i//40+1}"
    config["hosts"][f"node{i:02}"] = {
        "ip_addr": ip_addr,
        "network_node_id": node_id,
        "processes": [
            {
                "path": "/usr/bin/node",
                "args": f"{cwd}/node.js --ip {ip_addr} --seed node{i:02}",
                "environment": {"DEBUG": "libp2p:*yamux*"},
                "expected_final_state": "running",
            }
        ],
    }

dump(config, open("shadow.yaml", "w"), Dumper=Dumper)
