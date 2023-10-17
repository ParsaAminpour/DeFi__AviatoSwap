
# Aviato Swap architecture

**Aviato Swap** project is a decentralized exchange powered by **UniswapV2** architecture which is contain a DAO system for any upgrading from the system.

The smart contract developed via **Brownie framework** and the front-end section is based on **ReactJs** *(Front-end hasn't completed yet and indicating the result will accomplish via brownie scripts)*




## Installation

### via `pipx`

The recommended way to install Brownie is via [`pipx`](https://github.com/pipxproject/pipx). pipx installs Brownie into a virtual environment and makes it available directly from the commandline. Once installed, you will never have to activate a virtual environment prior to using Brownie.

To install `pipx`:

```bash
python3 -m pip install --user pipx
python3 -m pipx ensurepath
```

To install Brownie using `pipx`:

```bash
pipx install eth-brownie
```

To upgrade to the latest version:

```bash
pipx upgrade eth-brownie
```

To use lastest master or another branch as version:
```bash
pipx install git+https://github.com/eth-brownie/brownie.git@master
```

### via `pip`

You can install the latest release via [`pip`](https://pypi.org/project/pip/):

```bash
pip install eth-brownie
```

### via `setuptools`

You can clone the repository and use [`setuptools`](https://github.com/pypa/setuptools) for the most up-to-date version:

```bash
git clone https://github.com/eth-brownie/brownie.git
cd brownie
python3 setup.py install
```

### Ganache-cli Installation
For run the Brownie scripts you need to run Ganachec-cli as a local blockchain
For do that run this command as Installation:

Using npm:

`npm install -g ganache-cli`

or, if you are using Yarn:

`yarn global add ganache-cli`



## Screenshots
![AviatoSwapContractDiagram](https://github.com/ParsaAminpour/Aviato-Swap/assets/77713904/141f258b-bb80-4035-8c4a-02909696ab6d)



## Deployment

## To deploy this project via its brownie scripts:
First off all you should run ganache-cli inside your environment
After adjusting WEB3_INFURA_ENDPOINT in you .env file (from Infura) you should run `source.env` and then you have to run (for mainnet-fork):
```bash
ganache-cli --fork $WEB3_INFURA_ENDPOINT --networkId 999
```


For running the contract add-remove liquidity operations you should run ```deploy_upgradeable_contract_preprations``` script via:
```bash
brownie run scripts/ProxyScripts/deploy_upgradeable_contract_preprations.py
```


## Here is a Demo for this script:
https://github.com/ParsaAminpour/Aviato-Swap/assets/77713904/b0e6bc12-a0c4-403f-afe3-43a99321ed8a



## Authors

- [@ParsaAminpour](https://www.github.com/ParsaAminpour)


## License

[MIT](https://choosealicense.com/licenses/mit/)

