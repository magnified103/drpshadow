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
});

await bootstrap_node.start();
