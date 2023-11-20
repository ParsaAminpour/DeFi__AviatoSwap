from brownie import (
    AviatoswapV2,
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
import pytest, math

AMOUNT_IN = 1e20
AMOUNT_IN_FOR_REMOVE = 1e19

UNISWAP_V2_ROUTER01 = "0xf164fC0Ec4E93095b804a4795bBe1e041497b92a"
FACTORY_ADDRESS = "0x5C69bEe701ef814a2B6a3EDD4B1652CB9cc5aA6f"
# UNISWAP_V2_ROUTER01 = "0x7a250d5630B4cF539739dF2C5dAcb4c659F2488D"

@pytest.fixture(scope='module')
def timestamp():
    block = web3.eth.get_block('latest')
    return block.timestamp

@pytest.fixture(scope='session')
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


@pytest.fixture(scope='module')
def provide_contract(provide_account):
    acc = provide_account
    # aviato = Aviatoswap.deploy({'from':acc})
    aviato = AviatoswapV2.deploy({'from':provide_account})

    return aviato

@pytest.fixture(scope='module')
def token1(provide_account):
    return TokenA.deploy({'from':provide_account})

@pytest.fixture(scope='module')
def token2(provide_account):
    return TokenB.deploy({'from':provide_account})


def test_add_liquidity(provide_account, provide_contract, token1, token2, timestamp):
    token1.approve(provide_contract.address, AMOUNT_IN, {'from':provide_account})
    token2.approve(provide_contract.address, AMOUNT_IN, {'from':provide_account})
    block = web3.eth.get_block('latest')
    

    assert token1.allowance(provide_account, provide_contract.address) == 1e20
    assert token2.allowance(provide_account, provide_contract.address) == 1e20


    # with an account which is not associated to AviatoswapV2 deployer
    PROVIDER = accounts[1]
    tx = provide_contract.bothSideAddingLiquidity(
        token1.address, token2.address, AMOUNT_IN, AMOUNT_IN, provide_account, block.timestamp + 10800,
        {'from':accounts[0]}
    )
    tx.wait(1)

    assert tx.events['logLiquidityAdded']['_amount1'] == 1e20
    assert tx.events['logLiquidityAdded']['_amount2'] == 1e20
    assert math.floor(tx.events['logLiquidityAdded']['liqAmount'].to('ether')) == 99

    # owner balance assertion
    assert token1.balanceOf(provide_account).to('ether') == 100000 - 100
    assert token2.balanceOf(provide_account).to('ether') == 100000 - 100

    # Allowance assertion
    assert token1.allowance(provide_account, provide_contract) == 0
    assert token2.allowance(provide_account, provide_contract) == 0

    # swap balance assertion
    assert token1.balanceOf(provide_contract.address) == 0
    assert token2.balanceOf(provide_contract.address) == 0

    # owner liquidity token assertion
    router_addr = "0x7a250d5630B4cF539739dF2C5dAcb4c659F2488D"
    factory_addr = "0x5C69bEe701ef814a2B6a3EDD4B1652CB9cc5aA6f"
    pair_addr = interface.IUniswapV2Factory(factory_addr).getPair(token1.address, token2.address)

    reserves = interface.IUniswapV2Pair(pair_addr).getReserves()
    assert reserves[0] == 1e20
    assert reserves[1] == 1e20

    liq_balance = interface.IUniswapV2Pair(pair_addr).balanceOf(provide_account)
    assert (liq_balance.to('ether')//1) == 99

    aviato1 = Aviatoswap.deploy({'from':provide_account})
    assert aviato1.address != provide_contract.address

    # check role granted
    LIQUIDITY_PROVIDER_ROLE = "0xf4bff5b507dec16e54f7365ca3d82370290609650d2e573391f4d08fc9171fd5"
    ADMIN = "0x41444d494e000000000000000000000000000000000000000000000000000000"
    assert provide_contract.hasRole(LIQUIDITY_PROVIDER_ROLE, provide_account) == True # returns bool
    assert provide_contract.hasRole(ADMIN, provide_account) == True

