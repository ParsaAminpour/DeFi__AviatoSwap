from brownie import *
from rich import print
from brownie import TokenA, TokenB, Aviatoswap
from brownie import interface
from brownie.exceptions import VirtualMachineError
# from brownie import interfaces
import time

def main():
    acc = accounts[0]
    block = web3.eth.get_block('latest')
    # acc = accounts.add(config.get('wallets').get('from_key'))
    acc = accounts[0]
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


    print('transaction is pending:')
    tx = swap._bothSideAddingLiquidity(
        addr1, addr2, 1e20, 1e20, acc, block.timestamp + 10800,
        {'from':acc}
    )
    tx.wait(1)
    
    router_addr = "0x7a250d5630B4cF539739dF2C5dAcb4c659F2488D"
    factory_addr = "0x5C69bEe701ef814a2B6a3EDD4B1652CB9cc5aA6f"
    pair_addr = interface.IUniswapV2Factory(factory_addr).getPair(token1.address, token2.address)

    reserves = interface.IUniswapV2Pair(pair_addr).getReserves()

    optimal_amount = swap._getOptimalAmtAtoGetSwapAmtA(
     1e19, reserves[0]
    )
    print(optimal_amount.to('ether'))