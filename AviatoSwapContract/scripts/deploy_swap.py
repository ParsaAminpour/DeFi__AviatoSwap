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
install()


theme = Theme({
    'success' : 'bold green on Magenta', 'error' : 'bold red'
})
console = Console(theme=theme)



def deploy(acc):
    print(f"The account is: {acc.address}\n ")
    time.sleep(1)
    block = web3.eth.get_block('latest')
    with Progress() as progress:

        tokens_task = progress.add_task("Deploying Token1...", total=3)
        swap_task = progress.add_task("Deploying Swap...", total=2)
        approval_task = progress.add_task("Approving to swap...", total=2)
        add_liquidity_task = progress.add_task("Adding Liquidity...", total=1)

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
            
            console.print(f"The balances are:\nToken1: {token1.balanceOf(acc)}\nToken2: {token2.balanceOf(acc)}\n\n")
            time.sleep(1)
            progress.update(swap_task, completed=2)

            # approving:
            token1.approve(swap.address, 1e20, {'from':acc})
            time.sleep(1)
            progress.update(approval_task, completed=1)

            token2.approve(swap.address, 1e20, {'from':acc})
            time.sleep(1)
            progress.update(approval_task, completed=2)
            

            ##### ADD LIQUIDITY #####
            tx = swap._bothSideAddingLiquidity(
                addr1, addr2, 1e20, 1e20, acc, block.timestamp + 10800, 
                {'from':acc})
            tx.wait(1)
            progress.update(add_liquidity_task, completed=1)


            # factory_addr = "0x5C69bEe701ef814a2B6a3EDD4B1652CB9cc5aA6f"
            # pair_addr = interface.IUniswapV2Factory(factory_addr).getPair(token1.address, token2.address)
            # pair_token = interface.IERC20(pair_addr)

            # res = interface.IUniswapV2Pair(pair_addr).getReserves()
            
            # lp_balance = interface.IUniswapV2Pair(pair_addr).balanceOf(acc)
            # lp_amount = swap._calculateAmountOfLpTokenForBurn(1e19, 1e19, res[0], res[1], lp_balance)
            # print(f"lp amount to burn is {lp_amount.to('ether')}\nand lp balance is {lp_balance.to('ether')}")
            # print(f"reserves amounts are: {res[0].to('ether')}\n{res[1].to('ether')}")


    # ############## SWAP TOKENS ##############
    # router01_address = "0xf164fC0Ec4E93095b804a4795bBe1e041497b92a"
    # print(f"The current token1 balance for acc is {token1.balanceOf(acc).to('ether')}\nWhich is greater than 1e19 {token1.balanceOf(acc) > 1e19}")
    # token1.approve(swap.address, token1.balanceOf(acc), {'from':acc})
    # print(f"The allowance amount for swap is {token1.allowance(acc, swap.address)}")
    # time.sleep(2)

    # tx2 = swap.swapping(
    #     token1.address, token2.address, 1e19, 1, accounts[0], {'from':accounts[0]}
    # )
    # tx2.wait(1)

def main():
    network_selected = Prompt.ask("Which network we gonna use?",
        default="development", choices=["mainnet", "mainnet-fork", "Sepolia"])
    account = accounts[0] if network_selected == 'mainnet-fork' \
        else config.get('wallets').get('from_key')
    print(f"The network is {network.show_active()}")
    deploy(acc=account)