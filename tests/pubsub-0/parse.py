import argparse
import re
import matplotlib.pyplot as plt
import numpy as np

parser = argparse.ArgumentParser()
parser.add_argument("--dir", help="The log directory")
args = parser.parse_args()

LOCATIONS = [
    "australia",
    "east-asia",
    "europe",
    "na-west",
    "na-east",
    "south-america",
    "south-africa",
    "west-asia",
]

RELIABILITIES = [
    "reliable",
    "home",
    "constrained",
    "laggy",
    "bad",
]

for location in LOCATIONS:
    for reliability in RELIABILITIES[:3]:
        for i in range(1):
            log_file = (
                f"{args.dir}/hosts/node-{location}-{reliability}-{i}/node.1000.stdout"
            )

            with open(log_file, "r") as f:
                data = f.read()
                for value, timestamp in re.findall(r"(\w+) created at (\d+)", data):
                    pass
                for value, timestamp in re.findall(r"(\w+) received at (\d+)", data):
                    pass

N = 42


class HostInfo:
    def __init__(self, host_id):
        self.host_id = host_id
        self.location_id = host_id // 3
        self.reliability_id = host_id % 3


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
    node_id = i % 21
    loc_id = node_id // 3
    rel_id = node_id % 3

    with open(log_dir, "r") as f:
        data = f.read()
        for hash, timestamp in re.findall(
            r"INFO: node: Vertex (\w+) created at (\d+)", data
        ):
            vertices.setdefault(hash, VertexInfo())
            vertices[hash].creation_timestamp = int(timestamp)
            vertices[hash].host = HostInfo(i)
        for hash, timestamp in re.findall(
            r"INFO: node: Vertex (\w+) merged at (\d+)", data
        ):
            vertices.setdefault(hash, VertexInfo())
            vertices[hash].merge_info.append((int(timestamp), HostInfo(i)))
        for hash, timestamp in re.findall(
            r"INFO: node: Vertex (\w+) finalized at (\d+)", data
        ):
            vertices.setdefault(hash, VertexInfo())
            vertices[hash].finality_info.append((int(timestamp), HostInfo(i)))

# by_location = [[] for _ in range(8)]
by_reliability = [[] for _ in range(3)]
by_reliability_scatter = [[[] for _ in range(3)] for _ in range(3)]

for info in vertices.values():
    if info.host is not None:
        for timestamp, host in info.merge_info:
            by_reliability[info.host.reliability_id].append(
                timestamp - info.creation_timestamp
            )
            by_reliability_scatter[info.host.reliability_id][
                host.reliability_id
            ].append((info.creation_timestamp, timestamp - info.creation_timestamp))

COLORS = ["#428959", "#2A4F87", "#F18F01", "#F18F01", "#3B1F2B"]

# scatter plot

# fig, axs = plt.subplots(3, 3)
fig, axs = plt.subplots(3, 1, figsize=(5, 15))
# fig, axs = plt.subplots(1, 1)
# axs.hist(by_reliability[0][0], bins=np.linspace(0, 13000, 100), alpha=0.5)

# for i, dist in enumerate(by_location):
#     plt.hist(dist, label=LOCATIONS[i])

# for i in range(3):
#     for j in range(3):
#         axs[i, j].hist(by_reliability[i][j], alpha=0.5)
#         # axs[i, j].set_xscale("log")
#         axs[i, j].set_title(f"{RELIABILITIES[i]}->{RELIABILITIES[j]}")

for i in range(3):
    for j in range(3):
        creation_timestamp, timestamp = zip(*by_reliability_scatter[i][j])
        axs[i].scatter(
            x=creation_timestamp,
            y=timestamp,
            s=1,
            c=COLORS[j],
            label=f"{RELIABILITIES[j]}",
        )
    axs[i].set_title(f"{RELIABILITIES[i]}")
    axs[i].legend()

# plt.hist(by_location[4], bins=30, alpha=0.5, label=LOCATIONS[4])

fig.supxlabel("Timestamp")
fig.supylabel("Latency")
fig.suptitle(f"Latencies per reliability for {N} nodes, {2} ops/s")
fig.tight_layout()
fig.savefig("dist2.svg")
