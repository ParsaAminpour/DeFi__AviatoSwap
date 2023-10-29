from rich.traceback import install
from rich.console import Console
from rich.prompt import Prompt
from rich.panel import Panel
from rich.text import Text
from rich.theme import Theme
from rich.progress import Progress
from rich import print
from brownie import *
from brownie import TokenA, TokenB, Aviatoswap
from brownie import interface
from brownie.exceptions import VirtualMachineError
import time
import json
install()


theme = Theme({
    'success' : 'bold green on Magenta', 'error' : 'bold red'
})
console = Console(theme=theme)

UNISWAP_V2_ROUTER01 = "0xf164fC0Ec4E93095b804a4795bBe1e041497b92a"
factory_addr = "0x5C69bEe701ef814a2B6a3EDD4B1652CB9cc5aA6f"


def swapping():
    acc = accounts[0]
    print(f"The account is: {acc.address}\n ")
    time.sleep(1)
    block = web3.eth.get_block('latest')

    with Progress() as progress:

        tokens_task = progress.add_task("Deploying Tokens...", total=3)
        swap_task = progress.add_task("Deploying Swap...", total=2)
        approval_task = progress.add_task("Approving to swap...", total=2)
        add_liquidity_task = progress.add_task("Adding Liquidity...", total=1)
        # swapping_task = progress.add_task("Swapping...", total=3)

        while not progress.finished:
            token1 = TokenA.deploy({'from':acc})
            progress.update(tokens_task, completed=1)
            token2 = TokenB.deploy({'from':acc})
            progress.update(tokens_task, completed=2)
            
            addr1 = token1.address
            addr2 = token2.address
            time.sleep(1)
            progress.update(tokens_task, completed=3)


            swap = Aviatoswap.deploy({'from':acc})  
            progress.update(swap_task, completed=1)
            
            # console.print(f"The balances are:\nToken1: {token1.balanceOf(acc)}\nToken2: {token2.balanceOf(acc)}\n\n")
            time.sleep(1)
            progress.update(swap_task, completed=2)

            # approving:
            token1.approve(swap.address, 1e20, {'from':acc})
            time.sleep(1)
            progress.update(approval_task, completed=1)

            token2.approve(swap.address, 1e20, {'from':acc})
            time.sleep(1)
            progress.update(approval_task, completed=2)
            

            ##### ADD LIQUIDITY (R01) #####
            tx = swap._bothSideAddingLiquidity(
                addr1, addr2, 1e20, 1e20, acc, block.timestamp + 10800, 
                {'from':acc})
            tx.wait(1)
            progress.update(add_liquidity_task, completed=1)

            pair_addr = interface.IUniswapV2Factory(factory_addr).getPair(token1.address, token2.address)
            pair_token = interface.IERC20(pair_addr)
            res_round1 = interface.IUniswapV2Pair(pair_addr).getReserves()
            lp_balance_round1 = interface.IUniswapV2Pair(pair_addr).balanceOf(acc)


            ####### SWAP SECTION #######
            token1.approve(swap.address, 1e20, {'from':acc})
            time.sleep(1)

            # token1.approve(UNISWAP_V2_ROUTER01, 1e20, {'from':acc})
            # time.sleep(3)
            print(token1.allowance(acc, swap.address), sep='\n')

            # NOTE: Accomplish this function off-chain
            # path = [
            #     token1.address,
            #     "0xC02aaA39b223FE8D0A0e5C4F27eAD9083C756Cc2",
            #     token2.address
            # ]
            # block2 = web3.eth.get_block('latest')

            # tx2 = interface.IUniswapV2Router01(UNISWAP_V2_ROUTER01).swapExactTokensForTokens(
            #     1e19, 1, path, acc, block2.timestamp, {'from':acc}
            # )

            tx2 = swap.swapping(
                token1.address, token2.address, 1e19, 1, acc, {'from':acc}
            )
            tx2.wait(1)

            print(tx2.events['LogNumber'])
            




def main():
    swapping()