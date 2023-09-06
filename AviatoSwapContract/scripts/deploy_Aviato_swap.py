from brownie import Aviatoswap, accounts, interfaces, network, config,\
        TokenA, TokenB, oneSideAddingLiquiduty
from rich import print, print_json
from rich.console import Console 
from asgiref.sync import sync_to_async, async_to_sync
from datetime import datetime as dt
import time, json, sys, os
import pandas as pd
from dotenv import load_dotenv
import asyncio
cnsl = Console()

load_dotenv()

@sync_to_async
def get_account() -> str:
    global account
    if network.show_active() == 'development': 
        account = accounts[0]

    if network.show_active() == 'sepolia':
        key = config.get('wallets').get('from_key')
        account = accounts.add(key)

    if network.show_active() == 'mainnet_fork':
        account = accounts[0]


@async_to_sync
async def deploy_swap() -> bool:
    global dai_addr, wbtc_addr, weth_addr
    acc = await get_account()
    dai_addr = config.get('wallets').get('dai_address')
    wbtc_addr = config.get('wallets').get('wbtc_address')
    weth_addr = config.get('wallets').get('weth_address')
    
    DAI = interfaces.IERC20(dai_addr)
    WBTC = interfaces.IERC20(wbtc_addr)
    WETH = interfaces.IERC20(weth_addr)
    dai_whale_addr = "0xe5F8086DAc91E039b1400febF0aB33ba3487F29A"
    
    amount_in = 1_000*(10**18)

    try:
        if DAI.balanceOf(fai_whale_addr) <= 0): 
            raise Exception('Unisufficient Dai balance from DAI whale address')


        swap = await Aviatoswap.deploy({'from':acc})
        cnsl.log(f'Swap deployed at {swap.address} address')
        asyncio.sleep(2)
        
        tx = await DAI.approve(swap.address, amount_in, {'from':dai_whale_addr})
        cnsl.log(f'Dai approved 1_000 DAI to swap address {swap.address}')
        asyncio.sleep(2)

        tx_ = await swap.swapping(
                dai_addr, wbtc_addr, amount_in, 1, accounts[0],\
                        {'from':dai_whale_addr})
        cnsl.log(f'DAI/WBTC swap has just been confirmed in tx address of {tx_.address}')
        asyncio.sleep(2)


    except Exception as err:
        cnsl.log(err.message)
        return False

    return True 

# Adding TokenA/TokenB liquidity to pool (Both side liquidity version)
@async_to_sync
async def adding_both_side_liquidity() -> bool:
    try:
        token1 = await TokenA.deploy({'from':dai_whale_addr})
        token2 = await TokenB.deploy({'from':dai_whale_addr})
    except Exception as err:
        print(f'[bold red]{err}[/bold red]')
    
    # 1 TokenA ~ 0.5 TokenB
    amount1 = 1e21
    amount2 = 5*1e20

    await print(f'''[bold green] The balance of DAI whale 
            from TokenA is {token1.balanceOf(dai_whale_addr} and 
            for TokenB is {token2.balanceOf(dai_whale_addr}[/bold green]''')
    
    try:
        swap = await Aviatoswap.deploy({'from':dai_whale_addr})
        
        asyncio.sleep(2)

        tx1 = await swap.botSideAddingLiquidity(
            token1.address, token2.address, amount1, amount2, 1,1, swap.address,
            {'from'dai_whale_addr})
        
    except Exception as err:
        print(f'[bold red] an error occured: {err.message}\n')
        print(tx1.error())
        return False     
   return True


@async_to_sync
async def adding_one_side_optimal_liquidity() -> bool:
    try:
        token1 = await TokenA.deploy({'from':dai_whale_addr})
        token2 = await TokenB.deploy({'from':dai_whale_addr})
    except Exception as err:
        print(f'[bold red]{err}[/bold red]')

    AMOUNT_IN = 1e21

    try:
        Swap = await Aviatoswap.deploy({'from':dai_whale_addr})
        asyncio.sleep(2)
        OptimanSwap = await Swap.oneSideAddingLiquiduty(
            token1.address, token2.address, AMOUNT_IN, {'from':dai_whale_addr})
        
        print(f'''[bold green]
                The optimal swap deployed at {OptimalSwap.address}''')

    except Exception  as err:
        print(err)
    



if __name__ == '__main__':
    adding_one_side_optimal_liquidity()




def remove_both_side_liquidity() -> bool:
    ...
