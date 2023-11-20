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
    aviato = Aviatoswap.deploy({'from':acc})

    print(f"[bold purple]{aviato.address}[/]")

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


    tx = provide_contract._bothSideAddingLiquidity(
        token1.address, token2.address, AMOUNT_IN, AMOUNT_IN, provide_account, block.timestamp + 10800
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

    opt_amount = provide_contract._calculateAmountOfLpTokenForBurn(
        AMOUNT_IN_FOR_REMOVE, AMOUNT_IN_FOR_REMOVE, reserves[0], reserves[1], liq_balance
    )

    
    remove_liq_tx = interface.IUniswapV2Router01(UNISWAP_V2_ROUTER01).removeLiquidity(
        token1.address, token2.address, opt_amount, 1, 1, provide_account, block.timestamp + 10800,
        {'from' : accounts[0]}
    )
    remove_liq_tx.wait(1)
    assert True

# def test_remove_liquidity(provide_account, timestamp):
#     ex_contract = Aviatoswap[-1]
#     token1 = TokenA[-1]
#     token2 = TokenB[-1]

#     pair_addr = interface.IUniswapV2Factory(FACTORY_ADDRESS).getPair(token1.address, token2.address)
#     # print(pair_addr )

#     res_round = interface.IUniswapV2Pair(pair_addr).getReserves()
    
#     lp_balance_round = interface.IUniswapV2Pair(pair_addr).balanceOf(provide_account)

#     opt_amount = ex_contract._calculateAmountOfLpTokenForBurn(
#         1e19, 1e19, res_round[0], res_round[1], lp_balance_round
#     )

#     remove_liq_tx = interface.IUniswapV2Router01(UNISWAP_V2_ROUTER01).removeLiquidity(
#         token1.address, token2.address, opt_amount, 1, 1, provide_account, timestamp + 10800,
#         {'from' : provide_account}
#     )
#     remove_liq_tx.wait(1)

#     res_round_after_burn = interface.IUniswapV2Pair(pair_addr).getReserves()

#     assert res_round_after_burn[0] == res_round[0] - 1e19
#     assert res_round_after_burn[1] == res_round[1] - 1e19

