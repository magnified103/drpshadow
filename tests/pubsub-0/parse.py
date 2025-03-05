import argparse
import re
import matplotlib.pyplot as plt
import numpy as np

parser = argparse.ArgumentParser()
parser.add_argument("--data", help="The log directory", required=True)
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


class HostInfo:
    def __init__(self, location, reliability):
        self.location: str = location
        self.reliability: str = reliability


class VertexInfo:
    def __init__(self):
        self.creation_timestamp = None
        self.finality_info = []
        self.merge_info: list[tuple[int, HostInfo]] = []
        self.host: HostInfo = None


START_TIMESTAMP = 946684800000
vertices: dict[str, VertexInfo] = {}

for location in LOCATIONS:
    for reliability in RELIABILITIES[:3]:
        for i in range(5):
            log_file = (
                f"{args.data}/hosts/node-{location}-{reliability}-{i}/node.1000.stdout"
            )

            with open(log_file, "r") as f:
                data = f.read()
                for value, timestamp in re.findall(r"(\w+) created at (\d+)", data):
                    vertices.setdefault(value, VertexInfo())
                    vertices[value].creation_timestamp = int(timestamp) - START_TIMESTAMP
                    vertices[value].host = HostInfo(location, reliability)
                for value, timestamp in re.findall(r"(\w+) received at (\d+)", data):
                    vertices.setdefault(value, VertexInfo())
                    vertices[value].merge_info.append(
                        (int(timestamp) - START_TIMESTAMP, HostInfo(location, reliability))
                    )

by_reliability_scatter = {}

for info in vertices.values():
    if info.host is not None:
        for timestamp, host in info.merge_info:
            by_reliability_scatter.setdefault((info.host.reliability, host.reliability), [])
            by_reliability_scatter[info.host.reliability, host.reliability].append(
                (info.creation_timestamp, timestamp - info.creation_timestamp)
            )

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

for i, rel_i in enumerate(RELIABILITIES[:3]):
    for j, rel_j in enumerate(RELIABILITIES[:3]):
        creation_timestamp, timestamp = zip(*by_reliability_scatter[rel_i, rel_j])
        axs[i].scatter(
            x=creation_timestamp,
            y=timestamp,
            s=0.5,
            c=COLORS[j],
            label=f"{RELIABILITIES[j]}",
        )
    axs[i].set_title(f"{RELIABILITIES[i]}")
    axs[i].legend()

# plt.hist(by_location[4], bins=30, alpha=0.5, label=LOCATIONS[4])

fig.supxlabel("Timestamp")
fig.supylabel("Latency")
fig.suptitle(f"PubSub latency per reliability for {120} nodes, {2} ops/s")
fig.tight_layout()
fig.savefig(f"{args.data}/dist2.svg")
fig.savefig(f"{args.data}/dist2.png")
