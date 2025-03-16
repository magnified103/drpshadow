import { Command, Option } from "commander";
import { DRPNode } from "@ts-drp/node";
import { Message } from "@ts-drp/types";
import { Logger } from "@ts-drp/logger";
import { IntervalRunner } from "@ts-drp/interval-runner"
import { bootstrap_peers } from "./bootstrap_peers.js";
import { simpleMetrics } from "@libp2p/simple-metrics";
// import { admins } from "./admins.js";

// import { raceEvent } from "race-event";

const log = new Logger("node:", {
    template: "[%t] %l: %n",
});

export const program = new Command();
program.version("0.0.1");

program.addOption(
    new Option("--ip <address>", "IPv4 address of the node"),
);
program.addOption(new Option("--seed <seed>", "private key seed"));
program.addOption(new Option("--topic <topic>", "topic to subscribe to"));

const delay = ms => new Promise(res => setTimeout(res, ms));
async function digestMessage(message) {
    const msgUint8 = new TextEncoder().encode(message); // encode as (utf-8) Uint8Array
    const hashBuffer = await crypto.subtle.digest("SHA-256", msgUint8); // hash the message
    const hashArray = Array.from(new Uint8Array(hashBuffer)); // convert buffer to byte array
    const hashHex = hashArray
        .map((b) => b.toString(16).padStart(2, "0"))
        .join(""); // convert bytes to hex string
    return hashHex;
}

program.parse(process.args);
const opts = program.opts();

const node = new DRPNode({
    network_config: {
        bootstrap_peers,
        private_key_seed: opts.seed,
        log_config: {
            template: "[%t] %l: %n"
        },
        browser_metrics: simpleMetrics({
            onMetrics: (metrics) => {
                // do something with metrics
                console.log(metrics)
            },
            intervalMs: 1000 // default 1s
        })
    },
	credential_config: {
	    private_key_seed: opts.seed,
	},
	log_config: {
		template: "[%t] %l: %n"
	}
});

await node.start();

log.info("Credential: ", node.keychain.getPublicCredential())

const libp2pNode = node.networkNode["_node"]
// await raceEvent(libp2pNode, 'transport:listening')

await delay(10000);

node.networkNode.subscribe(opts.topic);
node.networkNode.addGroupMessageHandler(opts.topic, async (e) => {
    const message = Message.decode(e.detail.msg.data);
    const value = Buffer.from(message.data).toString("utf-8");
    const now = Date.now();
    console.log(`${value} received at ${now}`);
});

await delay(5000);

let value = await digestMessage(opts.seed);

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
