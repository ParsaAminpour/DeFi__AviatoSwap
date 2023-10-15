from rich.traceback import install
from rich.console import Console
from rich.prompt import Prompt
from rich.panel import Panel
from rich.text import Text
from rich.theme import Theme
from rich.progress import Progress
from rich import print
from brownie import *
from brownie import TokenA, TokenB, Aviatoswap,\
    ProxyAdmin, TransparentUpgradeableProxy 
from brownie import AviatoswapV2
from brownie import Contract
from brownie import interface
from brownie.exceptions import VirtualMachineError
import json
import time
install()

ex_contract = Aviatoswap[-1]

# First off, this function will call to make initialized to True
def prepare_v2_contract(swap_deployed_address:str, owner:str) -> None:
    block = web3.eth.get_block('latest')

    with Progress() as progress:
        check = progress.add_task("Checking Prefrequencies...", total=2)
        prepare_proxy_contracts = progress.add_task("Preparing Proxy Contracts...", total=3)

        while progress.finished == False:
            deployed_swap = Aviatoswap[-1]
            if deployed_swap.address == swap_deployed_address and deployed_swap.owner() == owner:
                progress.update(check, completed=1)

                initializing_tx = Aviatoswap.initialize({'from':owner})
                initializing_tx.wait(1)
                progress.update(check, completed=2)


                proxy_admin = ProxyAdmin.deploy({'from':owner})
                progress.update(prepare_proxy_contracts, completed=1)

                # Data storage will route in this contract (in proxy_contract)
                proxy = TransparentUpgradeableProxy.deploy(
                    deployed_swap.address, proxy_admin, b'', {'from':owner, 'gas_limmit':1e6})
                progress.update(prepare_proxy_contracts, completed=2)

                proxy_contract = Contract.from_abi("Aviatoswap", proxy.address, Aviatoswap.abi)
                progress.update(prepare_proxy_contracts, completed=3)

    print(f"""
    The Proxy Admin deploy address is [bold green]{proxy_admin}[/]\n
    And the proxy contract address is {proxy_contract.address} which its owner is\n
        [bold purple]{proxy_contract.owner()} 
    """)


def upgrade_contract(acc:str, version_number:int) -> str:
    with Progress() as progress:
        check = progress.add_task("Checking Prefrequencies...", total=2)
        upgrading = progress.add_task(f"Upgrading Contract to V{version_number}...", total=5)

        while progress.finished == False:
            
            if ex_contract.owner() == acc:
                progress.update(check, completed=1)


                try:
                    new_contract = AviatoswapV2.deploy({'from':acc})
                    progress.update(upgrading, completed=1)

                    PROXY_ADMIN = ProxyAdmin[-1]
                    progress.update(upgrading, completed=2)

                    PROXY_CONTRACT = TransparentUpgradeableProxy[-1]
                    progress.update(upgrading, completed=3)

                    upgrade_tx = PROXY_ADMIN.upgrade(
                        PROXY_CONTRACT, AviatoswapV2, {'from':acc})
                    upgrade_tx.wait(1)
                    progress.update(upgrading, completed=4)

                except VirtualMachineError as err:
                    print(f"[bold red]The upgrading process has been encountered to an error[/]\n\
                          Error Message -> {err}\n")
                progress.update(upgrading, completed=5)


                # new contract will deploy in another deployement file
                data = json.dumps({
                    'abi' : new_contract.abi,
                    'proxy_addr' : PROXY_CONTRACT.address,
                    'new_contract_name' : 'AviatoswapV2',
                })
                
    return data

def deploy_new_version(swap_deployed_addr:str, contract_owner:str, version_num:int):
    prepare_v2_contract(swap_deployed_address=swap_deployed_addr, owner=contract_owner)

    upgrading_ask = Prompt.ask("Are you sure you want to upgrade your contract?",
                              default="No", choices=['Yes', 'No'])
    if upgrading_ask == 'Yes':
        data_for_deploy = upgrade_contract(acc=contract_owner, version_number=2)
        data_for_deploy_ = json.load(data_for_deploy)

        Contract.from_abi(data_for_deploy_.get('new_contract_name'),
                          data_for_deploy_.get('proxy_addr'),
                          data_for_deploy_.get('abi'))
        
        print("""
            New contract deployed successfuly
                    """)
        
def main():
    deploy_new_version(ex_contract.address, ex_contract.owner(), 2)
