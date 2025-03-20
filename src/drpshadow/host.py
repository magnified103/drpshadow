from drpshadow.network import Zone


class Host:
    def __init__(self, name, zone: Zone, bandwidth_down=None, bandwidth_up=None):
        self.name = name
        self.network_node_id: int = zone.node_id
        self.ip_addr = str(next(zone.hosts))
        self.bandwidth_down = bandwidth_down
        self.bandwidth_up = bandwidth_up
        self.processes = []

    def add_process(
        self,
        path: str,
        args: str|list[str],
        environment: dict[str, str],
        expected_final_state: str,
        start_time: float = 0,  # in seconds
    ):
        self.processes.append(
            {
                "path": path,
                "args": args,
                "environment": environment,
                "expected_final_state": expected_final_state,
                "start_time": f"{round(start_time * 10**9)} ns",
            }
        )
