from brownie import Aviatoswap, accounts, interfaces, network, config
from rich import print, print_json
from rich.console import Console 
from asgiref.sync import sync_to_async, async_to_sync
from datetime import datetime as dt
import time, json, sys
import asyncio
cnsl = Console()

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
    acc = await get_account()
    dai_addr = config.get('wallets').get('dai_address')
    wbtc_addr = config.get('wallets').get('wbtc_address')
    weth_addr = config.get('wallets').get('weth_address')
    
    DAI = interfaces.IERC20(dai_addr)
    WBTC = interfaces.IERC20(wbtc_addr)
    WETH = interfaces.IERC20(weth_addr)
    dai_whale_addr = "0xe5F8086DAc91E039b1400febF0aB33ba3487F29A"
    
    try:
        if DAI.balanceOf(fai_whale_addr) <= 0): 
            raise Exception('Unisufficient Dai balance from DAI whale address')

        swap = await Aviatoswap.deploy({'from':acc})
        cnsl.log(f'Swap deployed at {swap.address} address')
        asyncio.sleep(2)
        
        tx = await DAI.approve(swap.address, 1_000*(10**18), {'from':dai_whale_addr})
        cnsl.log(f'Dai approved 1_000 DAI to swap address {swap.address}')
        asyncio.sleep(2)

        tx_ = await swap.swapping(
                dai_addr, wbtc_addr, 1_000*(10**18), 1, accounts[0],\
                        {'from':dai_whale_addr})
        cnsl.log(f'DAI/WBTC swap has just been confirmed in tx address of {tx_.address}')
        asyncio.sleep(2)


    except Exception as err:
        cnsl.log(err.message)



def main():
    deploy_swap()

