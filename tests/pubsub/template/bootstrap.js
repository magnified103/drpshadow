import { Command, Option } from "commander";
import { DRPNode } from "@ts-drp/node";
import { bootstrap_peers } from "./bootstrap_peers.js";

export const program = new Command();
program
	.name("drp-bootstrap")
	.version("0.0.1");

program
	.option("--ip <address>", "IPv4 address of the node")
	.option("--seed <seed>", "private key seed")
    .option("--peer_discovery_interval <ms>", "peer discovery interval");

program.parse(process.args);
const opts = program.opts();

// setup peer discovery interval
let peer_discovery_interval = parseInt(opts.peer_discovery_interval);
if (isNaN(peer_discovery_interval)) {
    peer_discovery_interval = 5000;
}

const bootstrap_node = new DRPNode({
	network_config: {
		listen_addresses: ["/ip4/0.0.0.0/tcp/50000/ws", "/ip4/0.0.0.0/tcp/50001"],
		announce_addresses: [
			`/ip4/${opts.ip}/tcp/50000/ws`,
			`/ip4/${opts.ip}/tcp/50001`,
		],
		bootstrap: true,
		bootstrap_peers,
		log_config: {
            template: "[%t] %l: %n"
        },
		pubsub: {
            peer_discovery_interval,
        }
	},
	keychain_config: {
	    private_key_seed: opts.seed,
	},
});

await bootstrap_node.start();
