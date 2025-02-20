from ipaddress import ip_network


class Zone:
    def __init__(
        self, name, host_bandwidth_down, host_bandwidth_up, address_range: str | int
    ) -> None:
        self.name = name
        self.host_bandwidth_down = host_bandwidth_down
        self.host_bandwidth_up = host_bandwidth_up
        self.hosts = ip_network(address_range).hosts()
        self.node_id = None  # Shadow's node_id
