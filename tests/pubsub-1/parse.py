import argparse
import re
import os
import matplotlib.pyplot as plt
import numpy as np
import math

parser = argparse.ArgumentParser()
parser.add_argument("--data", help="The log directory", required=True)
parser.add_argument("--percentile", help="The percentile to visualize", type=float, default=100)
args = parser.parse_args()


def get_directories():
    return [
        os.path.abspath(f"{args.data}/hosts/{dir}")
        for dir in os.listdir(f"{args.data}/hosts")
        if os.path.isdir(f"{args.data}/hosts/{dir}") and dir.startswith("node")
    ]


class MessageRecord:
    def __init__(self, msg_id):
        self.msg_id = msg_id
        self.sent_timestamp = None
        self.received_timestamps = []
        self.sender = None
        self.receivers = []

    def add_record(self, receiver, timestamp):
        self.received_timestamps.append(timestamp)
        assert receiver not in self.receivers
        self.receivers.append(receiver)


message_info: dict[MessageRecord] = {}

START_TIMESTAMP = 946684800000

hosts = []

for dir in get_directories():
    host = os.path.basename(dir)
    hosts.append(host)
    with open(f"{dir}/node.1000.stdout", "r") as f:
        data = f.read()
        for msg_id, timestamp in re.findall(r"(\w+) created at (\d+)", data):
            record = message_info.setdefault(msg_id, MessageRecord(msg_id))
            assert record.sent_timestamp is None
            record.sent_timestamp = int(timestamp) - START_TIMESTAMP
            record.sender = host

        for msg_id, timestamp in re.findall(r"(\w+) received at (\d+)", data):
            record = message_info.setdefault(msg_id, MessageRecord(msg_id))
            record.add_record(host, int(timestamp) - START_TIMESTAMP)


online_hosts = set()

for record in message_info.values():
    if len(record.receivers) > 0:
        online_hosts.add(record.sender)

creations = []
latencies = []
reliabilities = []

offline_hosts = set()

for record in message_info.values():
    if record.sender not in online_hosts:
        offline_hosts.add(record.sender)
        continue
    timestamps = [0] + record.received_timestamps
    timestamps.sort()

    try:
        latency = timestamps[math.ceil(args.percentile * len(online_hosts) / 100) - 1] - record.sent_timestamp
    except IndexError:
        latency = 10000

    reliability = len(record.received_timestamps) / len(online_hosts)
    creations.append(record.sent_timestamp)
    latencies.append(latency)
    reliabilities.append(reliability)

for host in offline_hosts:
    print(f"{host} is offline")


# scatter plot

# plt.scatter(x=creations, y=latencies, s=0.5, c=reliabilities, cmap="viridis_r")
plt.scatter(x=creations, y=latencies, s=0.5)

from matplotlib.ticker import ScalarFormatter

plt.yscale("log")
plt.gca().yaxis.set_major_formatter(ScalarFormatter())
plt.gca().yaxis.set_minor_formatter(ScalarFormatter())
# plt.tick_params(labelsize=8)

plt.xlabel("Timestamp")
plt.ylabel("Latency")
plt.suptitle(f"PubSub latency for {len(online_hosts)} nodes, {2} ops/s, {args.percentile}th percentile")
# plt.legend()
# plt.colorbar()
# plt.tight_layout()
plt.savefig(f"{args.data}/dist2.svg")
