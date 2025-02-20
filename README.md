# DRPshadow: DRP network simulator

Inspired by [Ethshadow](https://github.com/ethereum/ethshadow), DRPshadow is a network simulator that leverages [Shadow](https://github.com/shadow/shadow) to configure and simulate DRP networks.

## Quickstart

Install the dependencies as described in `https://shadow.github.io/docs/guide/install_dependencies.html`.

Install Shadow

```sh
git clone https://github.com/magnified103/shadow.git
cd shadow
git checkout temp_work
./setup build --clean --test
./setup test    # the ioctl test may fails
./setup install
```

Install DRPshadow (it is recommended to set up a separate python environment (`venv`) before using pip)

```sh
git clone https://github.com/magnified103/drpshadow.git
cd drpshadow
git submodule update --init --recursive
pip install -e .
```

Build js-libp2p
```sh
cd ./js-libp2p
npm install
npm run build
cd ..
```

Build ts-drp (in this step some examples could be fail to build)
```sh
cd ./ts-drp
pnpm install
pnpm build
cd ..
```

Generate Shadow config

```sh
cd tests
pnpm install
python3 message.py  # this generates two files: shadow.yaml and network.gml
```

Run the simulation task

```sh
shadow shadow.yaml
```
