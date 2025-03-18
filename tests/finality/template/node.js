import { Command, Option } from "commander";
import { DRPNode } from "@ts-drp/node";
import { Message } from "@ts-drp/types";
import { Logger } from "@ts-drp/logger";
import { IntervalRunner } from "@ts-drp/interval-runner"
import { bootstrap_peers } from "./bootstrap_peers.js";
import { simpleMetrics } from "@libp2p/simple-metrics";
import { SetDRP } from "@ts-drp/blueprints";
import { ObjectACL } from "@ts-drp/object";
import { admins } from "./admins.js";

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
        log_config: {
            template: "[%t] %l: %n"
        },
    },
	keychain_config: {
	    private_key_seed: opts.seed,
	},
	log_config: {
		template: "[%t] %l: %n"
	}
});

await node.start();

const libp2pNode = node.networkNode["_node"]
// await raceEvent(libp2pNode, 'transport:listening')

await delay(10000);

const obj = await node.createObject({
    drp: new SetDRP(),
    acl: new ObjectACL({ admins }),
    id: "123",
    config: {
        log_config: {
            template: "[%t] %l: %n"
        }
    }
});

obj.finalityStore.subscribe((hashes) => {
    const now = Date.now();
    for (const hash of hashes) {
        log.info(`Vertex ${hash} finalized at ${now}`);
    }
});
obj.subscribe((object, origin, vertices) => {
    if (origin === "merge") {
        const now = Date.now();
        for (const vertex of vertices) {
            log.info(`Vertex ${vertex.hash} merged at ${now}`);
        }
    }
    if (origin === "callFn") {
        const now = Date.now();
        for (const vertex of vertices) {
            log.info(`Vertex ${vertex.hash} created at ${now}`);
        }
    }
});

await delay(5000);

const acl = obj.acl;
const drp = obj.drp;
let value = await digestMessage(opts.seed);

acl.setKey(node.peerId, node.peerId, node.keychain.blsPublicKey);

const runner = new IntervalRunner({
    interval: 500,
    fn: async () => {
        drp.add(value);
        value = await digestMessage(value);
        return true;
    }
});

runner.start();

setTimeout(() => {
    runner.stop();
}, 30000);
