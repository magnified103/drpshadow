import re

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

# by_location = [[] for _ in range(8)]
by_reliability = [[] for _ in range(3)]
by_reliability_scatter = [[[] for _ in range(3)] for _ in range(3)]

for info in vertices.values():
    if info.host is not None:
        for timestamp, host in info.merge_info:
            by_reliability[info.host.reliability_id].append(timestamp - info.creation_timestamp)
            by_reliability_scatter[info.host.reliability_id][host.reliability_id].append((info.creation_timestamp, timestamp - info.creation_timestamp))

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

COLORS = [
    "#428959",
    "#2A4F87",
    "#F18F01",
    "#F18F01",
    "#3B1F2B"
]

import matplotlib.pyplot as plt
import numpy as np

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
    hist, bins = np.histogram(by_reliability[i], bins=100)
    logbins = np.logspace(np.log10(bins[0]),np.log10(bins[-1]),len(bins))
    axs[i].set_xscale("log")
    axs[i].hist(by_reliability[i], bins=logbins, alpha=0.5)
    per_80 = np.percentile(by_reliability[i], 80)
    per_90 = np.percentile(by_reliability[i], 90)
    per_95 = np.percentile(by_reliability[i], 95)
    median = np.median(by_reliability[i])
    lines = []
    lines.append(axs[i].axvline(x=median, color="green", label=f"median: {median:0.2f} ms"))
    lines.append(axs[i].axvline(x=per_80, color="black", label=f"$80^{{th}}$: {per_80:0.2f} ms"))
    lines.append(axs[i].axvline(x=per_90, color="red", label=f"$90^{{th}}$: {per_90:0.2f} ms"))
    lines.append(axs[i].axvline(x=per_95, color="purple", label=f"$95^{{th}}$: {per_95:0.2f} ms"))
    axs[i].set_title(f"{RELIABILITIES[i]}")
    axs[i].legend(handles=lines)

# plt.hist(by_location[4], bins=30, alpha=0.5, label=LOCATIONS[4])

fig.supxlabel("Latency (ms), log-scaled")
fig.supylabel("No. of vertices")
fig.suptitle(f"Latency distribution per reliability for {N} nodes, {2} ops/s")
fig.tight_layout()
fig.savefig("dist.svg")



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
        axs[i].scatter(x=creation_timestamp, y=timestamp, s=1, c=COLORS[j], label=f"{RELIABILITIES[j]}")
    axs[i].set_title(f"{RELIABILITIES[i]}")
    axs[i].legend()

# plt.hist(by_location[4], bins=30, alpha=0.5, label=LOCATIONS[4])

fig.supxlabel("Timestamp")
fig.supylabel("Latency")
fig.suptitle(f"Latencies per reliability for {N} nodes, {2} ops/s")
fig.tight_layout()
fig.savefig("dist2.svg")
