import { Command, Option } from "commander";
import { DRPNode } from "@ts-drp/node";

export const program = new Command();
program.version("0.0.1");

program.addOption(
	new Option("--ip <address>", "IPv4 address of the node"),
);
program.addOption(new Option("--seed <seed>", "private key seed"));

program.parse(process.args);
const opts = program.opts();

const bootstrap_node = new DRPNode({
	network_config: {
		listen_addresses: ["/ip4/0.0.0.0/tcp/50000/ws", "/ip4/0.0.0.0/tcp/50001"],
		announce_addresses: [
			`/ip4/${opts.ip}/tcp/50000/ws`,
			`/ip4/${opts.ip}/tcp/50001`,
		],
		bootstrap: true,
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
});

await bootstrap_node.start();
