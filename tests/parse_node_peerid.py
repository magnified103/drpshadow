import re
import logging
import argparse
import os

parser = argparse.ArgumentParser()
parser.add_argument("--data", type=str, required=True)
parser.add_argument("-o", "--output", type=argparse.FileType("w"), required=True)

args = parser.parse_args()

logger = logging.getLogger("parse_pubkeys")

args.output.write("export const admins = [];\n")
for dir in os.listdir(f"{args.data}/hosts"):
    if os.path.isdir(f"{args.data}/hosts/{dir}") and dir.startswith("node"):
        log_file = f"{args.data}/hosts/{dir}/node.1000.stdout"

        with open(log_file, "r") as f:
            data = f.read()
            try:
                peer_id = re.search(r"INFO: drp::network ::start: Successfuly started DRP network w/ peer_id (\w+)", data).group(1)
            except:
                logger.error(f"Error parsing {log_file}")
                break

            args.output.write(f"admins.push(\"{peer_id}\");\n")
