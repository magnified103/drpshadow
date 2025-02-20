from drpshadow.network.zone import Zone


class Link:
    def __init__(self, src: Zone, dst: Zone, latency: int, packet_loss: float) -> None:
        self.src = src
        self.dst = dst
        self.latency = latency
        self.packet_loss = packet_loss
