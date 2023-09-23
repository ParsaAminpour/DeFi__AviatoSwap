from brownie import *
from brownie import Aviatoswap, TokenA, TokenB
from brownie.exceptions import VirtualMachineError
from brownie.test import given, strategy
import pytest


@pytest.fixture(scope='session')
def account():  
    if network.show_active() == 'sepolia3':
        acc = accounts.add(
            config.get('wallets').get('from_key'))
        print(acc)
        
    if network.show_active() == 'mainnet-fork':
        # print("This is not propotion network for this contract")
        acc = accounts[0]
    
    acc = accounts[0]

    return acc


@pytest.fixture(scope="module")
def swap(account):
    return Aviatoswap.deploy({'from':account})

@pytest.fixture(scope="module")
def token1(account):
    return TokenA.deploy({'from':account})

@pytest.fixture(scope="module")
def token2(account):
    return TokenB.deploy({'from':account})


def test_tokens_balnaces(token1, token2, account):
    assert token1.balanceOf(account).to('ether') == 100_000
    assert token2.balanceOf(account).to('ether') == 100_000


def test_tokens_allowance_and_approval(swap, token1, token2, account):
    assert token1.allowance(swap.address, account) == 0
    assert token2.allowance(swap.address, account) == 0

    token1.approve(swap.address, token1.balanceOf(account), {'from':account})
    token2.approve(swap.address, token2.balanceOf(account), {'from':account})

    assert token1.allowance(account, swap.address) == token1.balanceOf(account)
    assert token2.allowance(account, swap.address) == token2.balanceOf(account)
    


def test_swap_addliquidity(swap, token1, token2, account):
    assert swap.address != 0

    amt = 1e20
    block = web3.eth.get_block('latest')

    token1.approve(swap.address, amt, {'from':account})
    token2.approve(swap.address, amt, {'from':account})

    init_balance1 = token1.balanceOf(account)
    init_balance2 = token2.balanceOf(account)

    assert token1.balanceOf(swap.address) == 0
    assert token2.balanceOf(swap.address) == 0

    token1.transfer(swap.address, amt, {'from':account})
    token2.transfer(swap.address, amt, {'from':account})

    assert token1.balanceOf(account) == init_balance1 - amt
    assert token2.balanceOf(account) == init_balance2 - amt

    # adding liquidity scope:
    with pytest.raises(VirtualMachineError):
        tx = swap._bothSideAddingLiquidity(
            token1.address, token2.address, amt, amt, account, block.timestamp + 100,
            {'from' : account, 'gas_limit':50_000, 'revert_allow':True}
        )

    # check calculations work
    assert swap._getOptimalAmtAtoGetSwapAmtA(100, 10000) == 49
    # assert swap.



    

