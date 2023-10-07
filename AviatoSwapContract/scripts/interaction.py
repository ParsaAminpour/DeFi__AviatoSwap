from brownie import (
    Aviatoswap,
    TokenA,
    TokenB,
    config,
    accounts,
    network,
    web3,
    interface
)
from rich import print
from datetime import datetime as dt
import time


def provide_account():
    if network.show_active() == 'mainnet-fork':
        print("The account generated is from mainnet-fork")
        acc = accounts[0]
        return acc

    if network.show_active() == 'sepolia':
        print("The network generated is from Sepolia test network")
        acc = accounts.add(
            config.get('wallet').get('from_key')
        )
        return acc
    
    return accounts[0]


def deploy():
    acc = provide_account()

    block = web3.eth.get_block('latest')
    acc = accounts.add(config.get('wallets').get('from_key'))
    print(f"The account is: {acc.address}\n ")
    time.sleep(1)

    token1 = TokenA.deploy({'from':acc})
    token2 = TokenB.deploy({'from':acc})
    
    addr1 = token1.address
    addr2 = token2.address

    swap = Aviatoswap.deploy({'from':acc})

    
    print(f"The balances are:\nToken1: {token1.balanceOf(acc)}\nToken2: {token2.balanceOf(acc)}")
    time.sleep(1)
    print("\n\n")

    # approving:
    token1.approve(swap.address, 1e20, {'from':acc})
    token2.approve(swap.address, 1e20, {'from':acc})
    time.sleep(1)

    tx1 = swap._bothSideAddingLiquidity(
        token1.address, token2.address, 1e20, 1e20, acc, block.timestamp + 10800
    )

    print(tx1.events)


def main():
    deploy()