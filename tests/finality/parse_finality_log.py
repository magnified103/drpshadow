import re

N = 40

class HostInfo:
    def __init__(self, host_id):
        self.host_id = host_id
        self.location_id = host_id // 5
        self.reliability_id = host_id % 5

class VertexInfo:
    def __init__(self):
        self.creation_timestamp = None
        self.finality_info = []
        self.merge_info = []
        self.host = None

vertices = {}

for i in range(N):
    log_dir = f"shadow.data/hosts/node{i:02}/node.1000.stdout"
    admins = {}
    node_id = i % 40
    loc_id = node_id // 5
    rel_id = node_id % 5

    with open(log_dir, "r") as f:
        data = f.read()
        for hash, timestamp in re.findall(r"INFO: node: Vertex (\w+) created at (\d+)", data):
            vertices.setdefault(hash, VertexInfo())
            vertices[hash].creation_timestamp = int(timestamp)
            vertices[hash].host = HostInfo(i)
        for hash, timestamp in re.findall(r"INFO: node: Vertex (\w+) merged at (\d+)", data):
            vertices.setdefault(hash, VertexInfo())
            vertices[hash].merge_info.append((int(timestamp), HostInfo(i)))
        for hash, timestamp in re.findall(r"INFO: node: Vertex (\w+) finalized at (\d+)", data):
            vertices.setdefault(hash, VertexInfo())
            vertices[hash].finality_info.append((int(timestamp), HostInfo(i)))

by_location = [[] for _ in range(8)]
by_reliability = [[] for _ in range(5)]

for info in vertices.values():
    if info.host is not None:
        for timestamp, host in info.finality_info:
            if host.host_id == info.host.host_id:
                by_location[info.host.location_id].append(timestamp - info.creation_timestamp)
                by_reliability[info.host.reliability_id].append(timestamp - info.creation_timestamp)

LOCATIONS = [
    "australia",
    "east_asia",
    "europe",
    "na_west",
    "na_east",
    "south_america",
    "south_africa",
    "west_asia",
]

RELIABILITIES = [
    "reliable",
    "home",
    "constrained",
    "laggy",
    "bad",
]

import matplotlib.pyplot as plt
import numpy as np

fig, axs = plt.subplots(3, 2)

# for i, dist in enumerate(by_location):
#     plt.hist(dist, label=LOCATIONS[i])


for i, dist in enumerate(by_reliability):
    axs[i // 2, i % 2].hist(dist, bins=np.arange(5000, 35000, 1000), alpha=0.5)
    axs[i // 2, i % 2].set_title(RELIABILITIES[i])
fig.delaxes(axs[2, 1])

# plt.hist(by_location[4], bins=30, alpha=0.5, label=LOCATIONS[4])

fig.supxlabel("Latency (ms)")
fig.supylabel("No. of vertices")
fig.suptitle(f"Finality latency distribution per reliability for {N} nodes")
fig.tight_layout()
fig.savefig("dist.svg")
