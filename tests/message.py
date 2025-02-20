from drpshadow.ethshadow import get_default_network
from drpshadow.shadow import DrpShadow
from drpshadow.host import Host

network = get_default_network()
network.build_zones_and_links()

drpshadow = DrpShadow(
    network,
    "90 sec",
    template_directory="template",
)

index = 0

for zone in network.filter_zones(reliability="reliable"):
    host = Host(
        f"bootstrap-{zone.name}",
        zone,
    )
    host.add_process(
        "/usr/bin/node",
        f"{drpshadow.data_directory}/bootstrap.js --ip {host.ip_addr} --seed bootstrap{index:02}",
        {"DEBUG": "libp2p:*yamux*"},
        "running",
    )
    drpshadow.add_host(host)
    index += 1

for zone in network.filter_zones(reliability__in=["reliable", "home", "constrained"]):
    for i in range(2):
        host = Host(
            f"node-{zone.name}-{i}",
            zone,
        )
        host.add_process(
            "/usr/bin/node",
            f"{drpshadow.data_directory}/node.js --ip {host.ip_addr} --seed {host.name}",
            {"DEBUG": "libp2p:*yamux*"},
            "running",
        )
        drpshadow.add_host(host)

drpshadow.generate_yaml()
