# DRPshadow: DRP network simulator

Inspired by [Ethshadow](https://github.com/ethereum/ethshadow), DRPshadow is a network simulator that leverages [Shadow](https://github.com/shadow/shadow) to configure and simulate DRP networks.

## Quickstart
Install DRPshadow

```sh
git clone https://github.com/magnified103/drpshadow.git
cd drpshadow
git submodule update --init --recursive
pip install -e .
```

Generate Shadow config

```sh
cd tests
pnpm install
python3 message.py
```

Run the simulation task

```sh
shadow shadow.yaml
```
