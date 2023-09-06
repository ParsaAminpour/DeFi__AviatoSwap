from rich import print
import math

fee = 0.003;

def calculate_just_amount_out_via_amount_in(amount_in:int, reserve1:int, reserve2:int):
    # Equation format is -> dy = ((dx * f) * Y) / ((dx * f) + X)
    amountOut = ((amount_in * (1 - Fee)) * reserve2) / ((amount_in * (1 - Fee)) * reserve1)
    return amountOut

def calculate_optimal_amount_for_adding_liquidity(amount_we_hace:int, reserve1:int, reserve2:int):
    # equation format is -> (1-f)s^ + A(2-f)s -aA = 0
    delta = math.pow(reserve1*(1-fee), 2) - 4*(1-fee)(amount_we_have*reserve1)
    solve = (math.sqrt(delta) - (reserve1*(2-fee))) / 2*(1-fee)
    print(f'[bold green] The fit amount is {solve}')
    
    OptimalAmountOut = calculate_just_amount_out_via_amount_in(solve, reserve1, reserve2)
    print(f'[bold yellow] And you will get {OptimalAmountOut}')

