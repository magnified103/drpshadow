import { Command, Option } from "commander";
import { DRPNode } from "@ts-drp/node";
import { Message } from "@ts-drp/types";
import { Logger } from "@ts-drp/logger";
import { IntervalRunner } from "@ts-drp/interval-runner"
import { bootstrap_peers } from "./bootstrap_peers.js";
// import { admins } from "./admins.js";

export const program = new Command();
program
    .name("drp-node")
    .version("0.0.1");
program
    .option("--ip <address>", "IPv4 address of the node")
    .option("--seed <seed>", "private key seed")
    .option("--topic <topic>", "topic to subscribe to")
    .option("--peer_discovery_interval <ms>", "peer discovery interval");
program.parse(process.args);
const opts = program.opts();

// setup peer discovery interval
let peer_discovery_interval = parseInt(opts.peer_discovery_interval);
if (isNaN(peer_discovery_interval)) {
    peer_discovery_interval = 5000;
}

// setup DRPNode
const node = new DRPNode({
    network_config: {
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
	log_config: {
		template: "[%t] %l: %n"
	}
});

await node.start();

const delay = ms => new Promise(res => setTimeout(res, ms));
await delay(10000);

node.networkNode.subscribe(opts.topic);
node.networkNode.addGroupMessageHandler(opts.topic, async (e) => {
    const message = Message.decode(e.detail.msg.data);
    const value = Buffer.from(message.data).toString("utf-8");
    const now = Date.now();
    console.log(`${value} received at ${now}`);
});

await delay(5000);

// setup hash function
async function digestMessage(message) {
    const msgUint8 = new TextEncoder().encode(message); // encode as (utf-8) Uint8Array
    const hashBuffer = await crypto.subtle.digest("SHA-256", msgUint8); // hash the message
    const hashArray = Array.from(new Uint8Array(hashBuffer)); // convert buffer to byte array
    const hashHex = hashArray
        .map((b) => b.toString(16).padStart(2, "0"))
        .join(""); // convert bytes to hex string
    return hashHex;
}
let value = await digestMessage(opts.seed);

// setup interval runner
const runner = new IntervalRunner({
    interval: 500,
    fn: async () => {
        await node.networkNode.broadcastMessage(opts.topic, {
            sender: node.networkNode.peerId,
            type: 0,
            data: new Uint8Array(Buffer.from(value)),
        });
        const now = Date.now();
        console.log(`${value} created at ${now}`);
        value = await digestMessage(value);
        return true;
    }
});

runner.start();

setTimeout(() => {
    runner.stop();
}, 30000);
