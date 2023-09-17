from brownie import accounts, TokenA, TokenB, Aviatoswap, web3
from rich import print, print_json
import time
    
def main():
    block = web3.eth.getBlock('latest')
    token1 = TokenA.deploy({'from':accounts[0]})
    token2 = TokenB.deploy({'from':accounts[0]})

    print('The token owner balance is:')
    print(token1.balanceOf(accounts[0]).to('ether'))
    print(token2.balanceOf(accounts[0]).to('ether'))

    swap = Aviatoswap.deploy({'from':accounts[0]})
    print(f'swap lunched at {swap.address}')

    amount = 1e20 # `100`
    token1.approve(swap.address, amount, {'from':accounts[0]})
    token2.approve(swap.address, amount, {'from':accounts[0]})

    print(f"token Approved\n{token1.allowance(accounts[0], swap.address).to('ether')}\n \
          {token2.allowance(accounts[0], swap.address).to('ether')}")
    
    tx = swap._bothSideAddingLiquidity(
        token1.address, token2.address, amount, amount, accounts[0],block.timestamp+10800, {'from':accounts[0]}
    )
    print(tx.error())