import { Command, Option } from "commander";
import { DRPNode } from "@ts-drp/node";
import { Message } from "@ts-drp/types";
import { Logger } from "@ts-drp/logger";
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
        bootstrap_peers: [
            "/ip4/11.0.0.1/tcp/50000/ws/p2p/16Uiu2HAmDa8croH4zLsNWy41QBoj28rYDsRNDzBMWnz8BsCdwDBs",
            "/ip4/11.1.0.1/tcp/50000/ws/p2p/16Uiu2HAmJstwH5yYD4zvW2QiPMbPnnjBooqGp7JL7XYNz3oX2dtV",
            "/ip4/11.2.0.1/tcp/50000/ws/p2p/16Uiu2HAmHjWPUfM9XzSQnHE4AHWVZ5g2dh8PHT85PWkofqtr2zA5",
            "/ip4/11.3.0.1/tcp/50000/ws/p2p/16Uiu2HAm1hspuJ9iNtTB4JPnZY3UF9V8fC3DEBUNgRUcJjPZvzWJ",
            "/ip4/11.4.0.1/tcp/50000/ws/p2p/16Uiu2HAkvzeWL2TeWG5dxgVgfV726281cRuRUbXjt1nxQ48rhknP",
            "/ip4/11.5.0.1/tcp/50000/ws/p2p/16Uiu2HAm8tpPFUUoUApaAQA5hEvxMreyTDexULYxmQ2xpGkhf43x",
            "/ip4/11.6.0.1/tcp/50000/ws/p2p/16Uiu2HAmK7xLcgz6Y8KAjk9P6AZCEVtj7rDV27pnuHf5Q1DM4Te1",
            "/ip4/11.7.0.1/tcp/50000/ws/p2p/16Uiu2HAkwgvajBoVeSGq9RidM2VGRCmitccptFtqcaAhY8dAEusV",
        ],
        private_key_seed: opts.seed,
        log_config: {
            template: "[%t] %l: %n"
        }
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

await delay(25000);

node.networkNode.subscribe(opts.topic);
node.networkNode.addGroupMessageHandler(opts.topic, async (e) => {
    const message = Message.decode(e.detail.msg.data);
    const value = Buffer.from(message.data).toString("utf-8");
    const now = Date.now();
    console.log(`${value} received at ${now}`);
});

await delay(5000);

let value = await digestMessage(opts.seed);

const interval = setInterval(async () => {
    await node.networkNode.broadcastMessage(opts.topic, {
        sender: node.networkNode.peerId,
        type: 0,
        data: new Uint8Array(Buffer.from(value)),
    });
    const now = Date.now();
    console.log(`${value} created at ${now}`);
    value = await digestMessage(value);
}, 500);

setTimeout(() => {
    clearInterval(interval);
}, 15000);
