import brownie
import pytest

def test_initialize(aviatoswap, accounts):
    # Test initialization
    assert aviatoswap.initialized() == False
    aviatoswap.initialize({'from': accounts[0]})
    assert aviatoswap.initialized() == True

def test_add_liquidity(aviatoswap, accounts):
    # Test adding liquidity
    tokenA = accounts[1]
    tokenB = accounts[2]

    # Initialize your tokens and make them available to the contract
    tokenA._mintForTesting(10**18, {'from': accounts[0]})
    tokenB._mintForTesting(10**18, {'from': accounts[0]})

    # Perform the adding liquidity function
    aviatoswap.oneSideAddingLiquiduty(tokenA, tokenB, 10**17, {'from': accounts[3]})

    # Add assertions to check that liquidity was added correctly

def test_swap_tokens(aviatoswap, accounts):
    # Test token swapping
    tokenA = accounts[1]
    tokenB = accounts[2]

    # Initialize your tokens and make them available to the contract
    tokenA._mintForTesting(10**18, {'from': accounts[0]})
    tokenB._mintForTesting(10**18, {'from': accounts[0]})

    # Perform a token swap and check that the balance has changed correctly

def test_remove_liquidity(aviatoswap, accounts):
    # Test removing liquidity
    tokenA = accounts[1]
    tokenB = accounts[2]

    # Initialize your tokens and make them available to the contract
    tokenA._mintForTesting(10**18, {'from': accounts[0]})
    tokenB._mintForTesting(10**18, {'from': accounts[0]})

    # Add liquidity, then perform the remove liquidity function
    aviatoswap.oneSideAddingLiquiduty(tokenA, tokenB, 10**17, {'from': accounts[3]})
    aviatoswap.removingLiquidity(tokenA, tokenB, 10**15, 10**16, {'from': accounts[3]})

    # Add assertions to check that liquidity was removed correctly

# Add more test cases as needed

