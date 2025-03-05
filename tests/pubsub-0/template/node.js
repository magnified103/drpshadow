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
            "/ip4/11.0.0.1/tcp/50000/ws/p2p/12D3KooWC6sm9iwmYbeQJCJipKTRghmABNz1wnpJANvSMabvecwJ",
            "/ip4/11.1.0.1/tcp/50000/ws/p2p/12D3KooWHzRtpN5F3RwnNyygTkaTEymtWy1HQ5kSURKQe8pRdksA",
            "/ip4/11.2.0.1/tcp/50000/ws/p2p/12D3KooWDRX6cHq3mDdq13Q7aDv9GXHYcs1GJKdky3iGPZ1YYyPb",
            "/ip4/11.3.0.1/tcp/50000/ws/p2p/12D3KooWM43k6rCvqqr5Y38CneFGrUuGp9u4QPVCEfYZ5pX6wvzA",
            "/ip4/11.4.0.1/tcp/50000/ws/p2p/12D3KooWH6P7vHkTp5aGTYvZrk3CA8FNyLe4A2ZkRnEpqJJU38px",
            "/ip4/11.5.0.1/tcp/50000/ws/p2p/12D3KooWPh4VTxayNJ8xS5B8Puh8Kv2JnsCf6qLPeuL8E9vsqnoB",
            "/ip4/11.6.0.1/tcp/50000/ws/p2p/12D3KooWRbRMLp7vkb6xApmu8tRbxGKFnybJ8TXcDRQGJGW6b47P",
            "/ip4/11.7.0.1/tcp/50000/ws/p2p/12D3KooWHA9oFWVfN5YFmP4yxvZCTCdayvuFdXV1mxtkFhmQsghK",
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

log.info("Credential: ", node.credentialStore.getPublicCredential())

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
