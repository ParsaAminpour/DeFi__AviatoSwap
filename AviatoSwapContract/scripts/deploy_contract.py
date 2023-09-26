from brownie import *
from rich import print
from brownie import TokenA, TokenB, Aviatoswap
# from brownie import interfaces
import time

def main():
    global addr1, addr2

    acc = accounts.add(config.get('wallets').get('from_key'))
    print(f"The account is: {acc.address}")
    block = web3.eth.get_block('latest')

    token1 = TokenA.deploy({'from':acc})
    token2 = TokenB.deploy({'from':acc})
    
    addr1 = token1.address
    addr2 = token2.address

    swap = Aviatoswap.deploy({'from':acc})

    print(f"The balances are:\nToken1: {token1.balanceOf(acc)}\nToken2: {token2.balanceOf(acc)}")
    time.sleep(2)
    print("\n\n")

    # approving:
    token1.approve(swap.address, 1e20, {'from':acc})
    token2.approve(swap.address, 1e20, {'from':acc})
    time.sleep(2)


    if(token1.allowance(acc, swap.address) * token2.allowance(acc, swap.address) != 0):
        print('transaction is pending:')
        tx = swap._bothSideAddingLiquidity(
            addr1, addr2, 1e20, 1e20, acc, block.timestamp + 10800,
            {'from':acc}
        )
        time.sleep("after add liquidity transaction..")
        print(tx.events())  