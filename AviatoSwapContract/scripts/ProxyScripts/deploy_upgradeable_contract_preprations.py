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
from ..deploy_add_and_remove_liquidity import main as add_liq_main
import json
import time
install()

block = web3.eth.get_block('latest')

# First off, this function will call to make initialized to True
def prepare_v2_contract(swap_deployed_address:str, owner:str) -> json:
    global deployed_swap

    with Progress() as progress:
        check = progress.add_task("Checking Prefrequencies...", total=2)
        prepare_proxy_contracts = progress.add_task("Preparing Proxy Contracts...", total=3)

        while not progress.finished:
            deployed_swap = Aviatoswap[-1]
            time.sleep(2)

            if deployed_swap.address == swap_deployed_address and deployed_swap.owner() == owner:

                progress.update(check, completed=1)

                initializing_tx = deployed_swap.initialize({'from':owner})
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

                data = json.dumps({
                    'swap_v1_address' : swap_deployed_address,
                    'swap_v1_owner' : owner,
                    'proxy_admin' : proxy_admin.address,
                    'proxy_contract' : proxy_contract.address,
                })

    print(f"""
    The Proxy Admin deploy address is [bold green]{proxy_admin}[/]\n
    And the proxy contract address is {proxy_contract.address} which its owner is\n
        [bold purple]{proxy_admin}[/] 
    """)
    return data


def upgrade_contract(acc:str, version_number:int) -> json:
    print(deployed_swap.address)
    time.sleep(2)

    with Progress() as progress:
        check = progress.add_task("Checking Prefrequencies...", total=1)
        upgrading = progress.add_task(f"Upgrading Contract to V{version_number}...", total=5)

        # print(acc, deployed_swap.owner())
        time.sleep(5)
        while progress.finished == False:
            if deployed_swap.owner() == acc:
                progress.update(check, completed=1)


                try:
                    new_contract = AviatoswapV2.deploy({'from':acc})
                    progress.update(upgrading, completed=1)
                    time.sleep(3)

                    PROXY_ADMIN = ProxyAdmin[-1]
                    progress.update(upgrading, completed=2)
                    time.sleep(2)

                    PROXY_CONTRACT = TransparentUpgradeableProxy[-1]
                    progress.update(upgrading, completed=3)
                    time.sleep(2)

                    # print(acc == deployed_swap.owner())
                    # time.sleep(5) For debugging

                    upgrade_tx = PROXY_ADMIN.upgrade(
                        PROXY_CONTRACT, new_contract.address, {'from':acc})
                    upgrade_tx.wait(1)
                    progress.update(upgrading, completed=4)
                    print("updated")
                    time.sleep(3)


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
    response = json.loads(add_liq_main())
    print(response, sep='\n\n')

    response2 = json.loads(prepare_v2_contract(
        response.get('contract_address'), response.get('contract_owner')))
    print(response2, sep='\n\n')



    upgrading_ask = Prompt.ask("Are you sure you want to upgrade your contract?",
                              default="No", choices=['Yes', 'No'])
    if upgrading_ask == 'Yes':
        response3 = json.loads(upgrade_contract(response2.get('swap_v1_owner'), 2))

        aviatoswapv2 = Contract.from_abi(response3.get('new_contract_name'),
                          response3.get('proxy_addr'),
                          response3.get('abi'))
        
    print(Panel.fit(f"""[bold yellow]
    The information fetched from response (in add and remove liq) are: 
    Contract address {response.get('contract_address')}
    Contract owner address: {response.get('contract_owner')}\n

    The information fetched from response2 are: 
    SwapV1 contract address: {response2.get('swap_v1_address')}
    SwapV2 owner address{response2.get('swap_v1_owner')}
    Proxy admin is: {response2.get('proxy_admin')}
    proxy contract address is: {response2.get('proxy_contract')}\n

    The information fetched from response3 are: 
    Proxy address: {response3.get('proxy_addr')}
    new contract name: {response3.get("new_contract_name")}\n

    [bold green]And AviatoSwapV2 address is : {aviatoswapv2.address}
    [/]"""))    