from rich.traceback import install
from rich.console import Console
from rich.prompt import Prompt
from rich.panel import Panel
from rich.text import Text
from rich.theme import Theme
from rich.progress import Progress
from rich import print
from brownie import *
from brownie import TokenA, TokenB, AviatoswapV2, Aviatoswap
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

def deploy(acc) -> json:
    print(f"The account is: {acc.address}\n ")
    time.sleep(1)
    block = web3.eth.get_block('latest')
    with Progress() as progress:

        tokens_task = progress.add_task("Deploying Tokens...", total=3)
        swap_task = progress.add_task("Deploying Swap...", total=2)
        approval_task = progress.add_task("Approving to swap...", total=2)
        add_liquidity_task = progress.add_task("Adding Liquidity...", total=1)
        add_liquidity_round2_task = progress.add_task("Adding Liquidity (2nd round)...", total=3)

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


            ######## ADD LIQUIDITY (R02) ########
            token1.approve(swap.address, 1e20, {'from':acc})
            time.sleep(1)
            progress.update(add_liquidity_round2_task, completed=1)

            token2.approve(swap.address, 1e20, {'from':acc})
            time.sleep(1)
            progress.update(add_liquidity_round2_task, completed=2)

            second_add = swap._bothSideAddingLiquidity(
                addr1, addr2, 1e20, 1e20, acc, block.timestamp + 10800,
                {'from':acc})
            second_add.wait(1)
            progress.update(add_liquidity_round2_task, completed=3)

            res_round2 = interface.IUniswapV2Pair(pair_addr).getReserves()
            lp_balance_round2 = interface.IUniswapV2Pair(pair_addr).balanceOf(acc)


    print(Panel.fit(f"""
    The reserves amount for token1 and token2 in first round are\n
    [bold green]
        Reserve1 : {res_round1[0]} => {res_round1[0].to('ether')} TokenA\n
        Reserve2 : {res_round1[1]} => {res_round1[1].to('ether')} TokenB
    [/]\n
    The pair token address is: [purple]{pair_token.address}[/]\n
    And the liquidity token balance for this liquidity pair in first round is\n
    [bold green]
        {lp_balance_round1} => {lp_balance_round1.to('ether')} Lp token
    [/]\n\n

    The reserves amount for token1 and token2 in second round are\n
    [bold green]
        Reserve1 : {res_round2[0]} => {res_round2[0].to('ether')} TokenA\n
        Reserve2 : {res_round2[1]} => {res_round2[1].to('ether')} TokenB
    [/]\n
    And the liquidity token balance for this liquidity pair in second round is\n
    [bold green]
        {lp_balance_round2} => {lp_balance_round2.to('ether')} Lp token
    [/]
    
    """, title="Liquidty Pool Data"))
    print("\n\n")




    ########### REMOVE LIQUIDITY ###########
    with Progress() as progress:
        preparing = progress.add_task("Preparing for remove liquidty...", total=3)
        remove_liquidity = progress.add_task("Removing Liquidity...", total=3)

        while not progress.finished:   
            if res_round1[0] * res_round1[1]!= 0: progress.update(preparing, completed=1)
            time.sleep(.5)
            if lp_balance_round2 != 0: progress.update(preparing, completed=2)
            time.sleep(.5)
            if pair_token.address == pair_addr : progress.update(preparing, completed=3)
            time.sleep(.5)

            optimal_lp_amount_to_burn = swap._calculateAmountOfLpTokenForBurn(
                1e19, 1e19, res_round1[0], res_round1[1], lp_balance_round1
            )
            progress.update(remove_liquidity, completed=1)
            
            pair_token.approve(UNISWAP_V2_ROUTER01, optimal_lp_amount_to_burn, {'from':acc})
            progress.update(remove_liquidity, completed=2)

            block = web3.eth.get_block('latest')

            remove_liq_tx = interface.IUniswapV2Router01(UNISWAP_V2_ROUTER01).removeLiquidity(
                token1.address, token2.address, optimal_lp_amount_to_burn, 1, 1, acc, block.timestamp + 10800,
                {'from':acc})
            remove_liq_tx.wait(1)
            progress.update(remove_liquidity, completed=3)


    new_res = interface.IUniswapV2Pair(pair_addr).getReserves()
    new_lp_balance = pair_token.balanceOf(acc)
    print(Panel.fit(f"""
    The Optimal amount for removing was: [red]{optimal_lp_amount_to_burn.to('ether')}[/]\n
    The new reserves amount for token1 and token2 are\n
    [bold green]
        Reserve1 : {new_res[0]} => {new_res[0].to('ether')} TokenA\n
        Reserve2 : {new_res[1]} => {new_res[1].to('ether')} TokenB
    [/]\n
    And the liquidity token balance for this liquidity pair is\n
    [bold green]
        {new_lp_balance} => {new_lp_balance.to('ether')} Lp token
    [/]
    """, title="Liquidty Pool Data after removing 10% of liquidity"))

    return json.dumps({
        'contract_address' : swap.address,
        'contract_owner' : swap.owner(),
    })


def main():
    network_selected = Prompt.ask("Which network we gonna use?",
        default="development", choices=["mainnet", "mainnet-fork", "Sepolia"])
    account = accounts[0] if network_selected == 'mainnet-fork' \
        else config.get('wallets').get('from_key')
    print(f"The network is {network.show_active()}")
    data = deploy(acc=account)
    return data
