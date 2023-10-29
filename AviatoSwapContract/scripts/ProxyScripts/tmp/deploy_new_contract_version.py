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

from scripts.ProxyScripts.deploy_upgradeable_contract import upgrade_contract, prepare_v2_contract
import json
import time
install()


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
    impl = Aviatoswap[-1]
    deploy_new_version(impl.address, impl.owner(), 2)
