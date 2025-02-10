import re
import logging
import argparse

parser = argparse.ArgumentParser()
parser.add_argument("-o", "--output", type=argparse.FileType("w"), default="admins.js")

args = parser.parse_args()

logger = logging.getLogger("parse_pubkeys")

args.output.write("export const admins = new Map();\n")
for i in range(40):
    log_file = f"shadow.data/hosts/node{i:02}/node.1000.stdout"
    admins = {}

    with open(log_file, "r") as f:
        data = f.read()
        try:
            peer_id = re.search(r"INFO: drp::network ::start: Successfuly started DRP network w/ peer_id (\w+)", data).group(1)
            ed25519_pubkey = re.search(r"ed25519PublicKey: '([^']+)'", data).group(1)
            bls_pubkey = re.search(r"blsPublicKey: '([^']+)'", data).group(1)
        except:
            logger.error(f"Error parsing {log_file}")
            break

        args.output.write(f"admins.set(\"{peer_id}\", {{ ed25519PublicKey: \"{ed25519_pubkey}\", blsPublicKey: \"{bls_pubkey}\"}});\n")
