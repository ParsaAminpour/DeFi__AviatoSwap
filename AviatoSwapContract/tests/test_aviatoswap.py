import pytest
from brownie import Contract, accounts, chain, Aviatoswap
from brownie import VirtualMachineError

@pytest.fixture
def aviatoswap(Contract):
    # TODO: Deploy Aviatoswap contract
    try:
        swap = Aviatoswap.deploy({'from':accounts[0]})
    except VirtualMachineError as err:
        print(err)
    
    yield swap

def test_swapping_requires_valid_pairs(aviatoswap):
    tokenA = "0x0000000000000000000000000000000000000000"
    tokenB = "0x0000000000000000000000000000000000000000"
    
    with pytest.reverts():
        aviatoswap.swapping(tokenA, tokenB, 1, 1, accounts[0])
        
def test_swapping_transfers_tokens(aviatoswap, token, accounts):
    pair = token.address
    amountIn = 100
    
    token.approve(aviatoswap, amountIn, {"from": accounts[0]})
    
    balanceBefore = aviatoswap.balanceOf(token)  
    aviatoswap.swapping(pair, pair, amountIn, 1, accounts[0], {"from": accounts[0]})
    balanceAfter = aviatoswap.balanceOf(token)

    assert balanceAfter == balanceBefore + amountIn
    
def test_adding_liquidity(aviatoswap, tokenA, tokenB, accounts):
    amountA = 100
    amountB = 150
    
    tokenA.approve(aviatoswap, amountA, {"from": accounts[0]})
    tokenB.approve(aviatoswap, amountB, {"from": accounts[0]})

    aviatoswap.bothSideAddingLiquidity(tokenA, tokenB, amountA, amountB, accounts[0], chain.time() + 1000)

    assert tokenA.balanceOf(aviatoswap) == amountA
    assert tokenB.balanceOf(aviatoswap) == amountB

# TODO: Add more test cases