import argparse
import random
import shutil
from datetime import datetime
from os.path import abspath

from drpshadow.shadow import DrpShadow
from drpshadow.host import Host
from drpshadow.bonsai import get_default_network

random.seed(0)

parser = argparse.ArgumentParser()
parser.add_argument("--loc", help="Number of locations", type=int, default=30)
parser.add_argument(
    "--output",
    help="Output directory",
    default=datetime.now().strftime("%y%m%d-%H%M%S"),
)
parser.add_argument("--nodes", help="Number of nodes", type=int, default=90)
args = parser.parse_args()

if args.nodes % (args.loc * 3) != 0:
    raise ValueError("Number of nodes must be divisible by number of locations")

network = get_default_network(args.loc)
network.build_zones_and_links()

output_dir = abspath(args.output)

drpshadow = DrpShadow(network, output_dir)
drpshadow.config["general"]["stop_time"] = "90 sec"

shutil.copytree("template", output_dir)

index = 0

for zone in random.sample(
    list(network.filter_zones(reliability="reliable")), 8
):  # sample 8 zones for bootstrap nodes
    host = Host(
        f"bootstrap-{zone.name}",
        zone,
    )
    host.add_process(
        "/usr/bin/node",
        f"--expose-gc {output_dir}/bootstrap.js --ip {host.ip_addr} --seed bootstrap{index:02}",
        {"DEBUG": "libp2p:*yamux*"},
        "running",
    )
    drpshadow.add_host(host)
    index += 1

for zone in network.filter_zones(reliability__in=["reliable", "home", "constrained"]):
    for i in range(args.nodes // (args.loc * 3)):
        host = Host(
            f"node-{zone.name}-{i}",
            zone,
        )
        host.add_process(
            "/usr/bin/node",
            f"--expose-gc {output_dir}/node.js --ip {host.ip_addr} --topic 123 --seed {host.name}",
            {"DEBUG": "libp2p:*yamux*"},
            "running",
            10,
        )
        drpshadow.add_host(host)

drpshadow.generate_yaml(f"{args.output}/config.yml")
