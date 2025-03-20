import re
import os
import logging
import argparse

parser = argparse.ArgumentParser()
parser.add_argument("--data", type=str, default="shadow.data")
parser.add_argument("-o", "--output", default="bootstrap_peers.js")
parser.add_argument("-y", "--yes", action="store_true")

args = parser.parse_args()

print("Reading data from", os.path.abspath(args.data))
print("Writing to", os.path.abspath(args.output))
if not args.yes:
    choice = input("Process? [y/n]")
    if not choice.lower().startswith("y"):
        exit()

output = open(args.output, "w")
logger = logging.getLogger("parse_bootstrap_addr")

output.write("export const bootstrap_peers = [];\n")

for dir in os.listdir(f"{args.data}/hosts"):
    if os.path.isdir(f"{args.data}/hosts/{dir}") and dir.startswith("bootstrap"):
        log_file = f"{args.data}/hosts/{dir}/node.1000.stdout"

        with open(log_file, "r") as f:
            data = f.read()
            try:
                addr = re.search(r"'(/ip4/\d+\.\d+\.\d+\.\d+/tcp/50000/ws/p2p/\w+)'", data).group(1)
            except:
                logger.error(f"Error parsing {log_file}")
                break

            output.write(f"bootstrap_peers.push(\"{addr}\");\n")
