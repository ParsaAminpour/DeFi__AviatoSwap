from brownie import *
from rich import print
from brownie import TokenA, TokenB, Aviatoswap
from brownie import interface
from brownie.exceptions import VirtualMachineError
# from brownie import interfaces
import time


def getReservesOffChain(owner:str, token1_addr:str, token2_addr:str):
    global factory_addr
    factory_addr = "0x5C69bEe701ef814a2B6a3EDD4B1652CB9cc5aA6f"
    pair_addr = interface.IUniswapV2Factory(factory_addr).getPair(token1_addr, token2_addr)

    reserves = list(interface.IUniswapV2Pair(pair_addr).getReserves())
    reserves.pop()  # reomve timestamp from list

    liq_balance = interface.IUniswapV2Pair(pair_addr).balanceOf(owner)
    reserves.append(liq_balance)
    return reserves



def main():
    global addr1, addr2, router_addr

    block = web3.eth.get_block('latest')
    # acc = accounts.add(config.get('wallets').get('from_key'))
    acc = accounts[0]
    print(f"The account is: {acc.address}\n ")
    time.sleep(2)

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
        print(tx.error())

        print("after add liquidity transaction..")
        time.sleep(2)
        print("And the add liquidity events are:\n")
        time.sleep(2)
        print(tx.events, "\n\n")  

    else: print(f"[bold red]{ tx.revert_msg }[/bold red]")


    get_balances_tx = swap.getLiquidityBalanceOfPairs(
        token1.address, token2.address
    )
    print(f"And the balances of reserves and liquidity token of token1 and token2 \
          pairs are:\n{get_balances_tx.events}\n\n")

    

    #######################################
    #       Remove Liquidity
    #######################################


    # Remove liquidity after adding to the liquidity pool
    print("[bold green]Lets remove liquidity of token1 and token2 in 1/1 rate (based on liquidity ratio[/bold green])")
    time.sleep(3)

    try:
        token1_amount_for_remove, token2_amount_for_remove = 1e19, 1e19

        # lp_token_for_remove = swap._calculateAmountOfLpTokenForBurn(
        #     token1_amount_for_remove, token2_amount_for_remove, get_balances_tx[2]
        # )

        reserves_and_liq_balance = getReservesOffChain(acc.address, token1.address, token2.address) 
        print(f"""The Lp token for this amounts of pairs\n
              Token1 => {token1_amount_for_remove} | {token1_amount_for_remove / 1e18}\n
              Token2 => {token2_amount_for_remove} | {token2_amount_for_remove / 1e18}\n
              is => {reserves_and_liq_balance[2]}""")
        print(f"Amounts of reserves and liquidity tokens are: {reserves_and_liq_balance}")


        liq_amount_to_remove = swap._calculateAmountOfLpTokenForBurn(
            token1_amount_for_remove, token2_amount_for_remove, reserves_and_liq_balance[0], reserves_and_liq_balance[1], reserves_and_liq_balance[2]
        )
        print(f"Liquidity token amount for remove based on these amount is {liq_amount_to_remove}\n\n")
        time.sleep(2)

        factory_addr = "0x5C69bEe701ef814a2B6a3EDD4B1652CB9cc5aA6f"
        pair_addr = interface.IUniswapV2Factory(factory_addr).getPair(token1.address, token2.address)
        pair_token = interface.IERC20(pair_addr)
        router_addr = "0x7a250d5630B4cF539739dF2C5dAcb4c659F2488D"
        # approving operations:
        if reserves_and_liq_balance[2] != liq_amount_to_remove: # note whole liquidity token balance
            pair_token.approve(router_addr, reserves_and_liq_balance[2], {'from':acc})

            remove_liq_tx = interface.IUniswapV2Router(router_addr).removeLiquidity(
                token1.address, token2.address, liq_amount_to_remove, 1, 1, acc, block.timestamp + 10800,
                    {'from':acc}
            )
            time.sleep(3)

        else:
            pair_token.approve(router_addr, reserves_and_liq_balance[2], {'from':acc})
            remove_liq_tx = interface.IUniswapV2Router(router_addr).removeLiquidity(
                token1.address, token2.address, liq_amount_to_remove, 1, 1, acc, block.timestamp + 10800,
                    {'from':acc}
            )
            time.sleep(3)

        new_reserves = list(interface.IUniswapV2Pair(pair_addr).getReserves())
        new_reserves.pop()
        new_liq_token_balance = interface.IUniswapV2Pair(pair_addr).balanceOf(acc)
        print(f"""
                Remove Liquidity occured and the new amounts are:\n
                The reserve1 amount => {new_reserves[0]} | {new_reserves[0].to('ether')}\n
                The reserve2 amount => {new_reserves[1]} | {new_reserves[1].to('ether')}\n
                And the {acc.address[:5]}... address liquidity balance is => {new_liq_token_balance} | {new_liq_token_balance / 1e18}\n
              """)

    
    except VirtualMachineError:
        print(f"[bold red] {remove_liq_tx.revert_msg} [/bold red]")
        print(remove_liq_tx.info())


    
