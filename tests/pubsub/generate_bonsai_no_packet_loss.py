import argparse
import random
import shutil
from datetime import datetime
from os.path import abspath

from drpshadow.shadow import DrpShadow
from drpshadow.host import Host
from drpshadow.ethshadow import Reliability
from drpshadow.bonsai import BonsaiNetwork

random.seed(0)

parser = argparse.ArgumentParser()
parser.add_argument("--loc", help="Number of locations", type=int, default=50)
parser.add_argument(
    "--output",
    help="Output directory",
    default=datetime.now().strftime("%y%m%d-%H%M%S"),
)
parser.add_argument("--nodes", help="Number of nodes", type=int, default=100)
parser.add_argument("--stop", help="Stop time (sec)", type=float, default=90)
args = parser.parse_args()

if args.nodes % args.loc != 0:
    raise ValueError("Number of nodes must be divisible by number of locations")

network = BonsaiNetwork(args.loc)
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
        "home-no-loss",
        added_latency=20,
        added_packet_loss=0.0,
        bandwidth_up="50 Mbit",
        bandwidth_down="50 Mbit",
    ),
)

network.build_zones_and_links()

output_dir = abspath(args.output)

drpshadow = DrpShadow(network, output_dir)
drpshadow.config["general"]["stop_time"] = f"{round(args.stop * 10**9)} ns"

shutil.copytree("template", output_dir)

index = 0

peer_discovery_interval = 5

for zone in random.sample(
    list(network.filter_zones(reliability="reliable")), 8
):  # sample 8 zones for bootstrap nodes
    host = Host(
        f"bootstrap-{zone.name}",
        zone,
    )
    start_time = random.uniform(0, peer_discovery_interval) # randomize the starting time
    host.add_process(
        "/usr/bin/node",
        [
            "--expose-gc",
            f"{output_dir}/bootstrap.js",
            "--ip", f"{host.ip_addr}",
            "--peer_discovery_interval", f"{peer_discovery_interval*1000}",
            "--seed", f"bootstrap{index:02}",
        ],
        {"DEBUG": "libp2p:*yamux*"},
        "running",
        start_time=start_time,
    )
    drpshadow.add_host(host)
    index += 1

for zone in network.filter_zones(reliability__in=["home-no-loss"]):
    for i in range(args.nodes // args.loc):
        host = Host(
            f"node-{zone.name}-{i}",
            zone,
        )
        start_time=10+random.uniform(0, peer_discovery_interval)    # randomize the starting time
        host.add_process(
            "/usr/bin/node",
            [
                "--expose-gc",
                f"{output_dir}/node.js",
                "--ip", f"{host.ip_addr}",
                "--topic", "123",
                "--peer_discovery_interval", f"{peer_discovery_interval*1000}",
                "--stop", f"{round((args.stop - start_time) * 1000)}",
                "--seed", f"{host.name}",
            ],
            {"DEBUG": "libp2p:*yamux*"},
            "running",
            start_time=start_time,
        )
        drpshadow.add_host(host)

drpshadow.generate_yaml(f"{args.output}/config.yml")
