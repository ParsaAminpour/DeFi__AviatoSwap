// SPDX-License-Identifier: MIT
pragma solidity ^0.8.11;

import "@openzeppelin/contracts/utils/math/SafeMath.sol";
import "@openzeppelin/contracts/utils/math/Math.sol";
import "@openzeppelin/contracts/token/ERC20/ERC20.sol";
import "@openzeppelin/contracts/token/ERC20/IERC20.sol";
import "@openzeppelin/contracts/access/Ownable.sol";
import "@openzeppelin/contracts/security/ReentrancyGuard.sol";

import '@uniswap/contracts/interfaces/IUniswapV2Factory.sol';
import '@uniswap/contracts/interfaces/IUniswapV2Pair.sol';
import { IUniswapV2Router } from "../interfaces/IUniswap.sol";
import { UniMath, UQ112x112 } from "./InternalMath.sol";
import "./TokenA.sol";
import "./TokenB.sol";

contract Aviatoswap is Ownable, ReentrancyGuard, TokenA{
    using SafeMath for uint;
    using Math for uint;
    using UniMath for uint;


    address private FIRST_PAIR;
    address private immutable WETH = 0xC02aaA39b223FE8D0A0e5C4F27eAD9083C756Cc2;
    address private immutable DAI = 0x6B175474E89094C44Da98b954EedeAC495271d0F;
    address private immutable WBTC= 0x2260FAC5E5542a773Aa44fBCfeDf7C193bc2C599;
    address private SECOND_PAIR;

    address private constant UNISWAP_V2_ROUTER = 0x7a250d5630B4cF539739dF2C5dAcb4c659F2488D;
    address private constant UNISWAP_V2_FACTORY = 0x5C69bEe701ef814a2B6a3EDD4B1652CB9cc5aA6f;

    uint private constant FEE = 3;

    modifier amountAndTokensCheck(address _token1, address _token2, uint _amount1) {
        require(_token1 != address(0) && _token2 != address(0), 'invalid token address');
        require(_amount1 != 0, 'invalid amount for swao');
        _;
    }

    function _swapping(address _first_pair, address _second_pair, uint _amountIn, uint _amountOutMin, address _to) 
    internal 
    amountAndTokensCheck(_first_pair, _second_pair, _amountIn)
    nonReentrant{
        require(_first_pair != address(0) && _second_pair != address(0));
        require(_to != address(0), 'invalid destination address');
        FIRST_PAIR = _first_pair;
        SECOND_PAIR = _second_pair;

        IERC20(FIRST_PAIR).transferFrom(msg.sender, address(this), _amountIn);
        IERC20(FIRST_PAIR).approve(UNISWAP_V2_ROUTER, _amountIn);

        address[] memory path = new address[](3);
        path[0] = FIRST_PAIR;
        path[1] = WETH; // considered as swap bridge
        path[2] = SECOND_PAIR;

        IUniswapV2Router(UNISWAP_V2_ROUTER).swapExactTokensForTokens(
            _amountIn, _amountOutMin, path, _to, block.timestamp+10800);
    }


    function _bothSideAddingLiquidity(address _tokenA, address _tokenB, uint _amountA, uint _amountB, address _to, uint _death_time)
    internal 
    amountAndTokensCheck(_tokenA, _tokenB, _amountA)
    returns(uint amountA, uint amountB, uint liquidity) {
        require(_death_time >= block.timestamp && _amountB != 0);
        require(_to != address(0), 'invalid destination address');
        // trasfering and approving
        IERC20(_tokenA).transferFrom(msg.sender, address(this), _amountA);
        IERC20(_tokenB).transferFrom(msg.sender, address(this), _amountB);

        IERC20(_tokenA).approve(UNISWAP_V2_ROUTER, _amountA);
        IERC20(_tokenB).approve(UNISWAP_V2_ROUTER, _amountB);

        (amountA, amountB, liquidity) = IUniswapV2Router(UNISWAP_V2_ROUTER).addLiquidity(
            _tokenA, _tokenB, _amountA, _amountB, 1, 1, _to, block.timestamp+10800);
    }



    /** @dev This function will re-build with inline assembly, ASAP
             still has some vulnerability! */  
    function _getOptimalAmountForSwapFirstPair(uint _amount, uint _reserve1) public pure returns(uint actual_amount) {
        require(_amount != 0 && _reserve1 != 0, 'invalid inputs');
        // We have : (1-f)s^2 + A(2-f)s - aA = 0  -> s=?
        unchecked {
            uint delta_val = uint((_reserve1*(2000-FEE))**2) + (4*(1000-FEE)*(_amount*_reserve1));
            uint minusOne;
            assembly {
                minusOne := 0xfffffffff
            }
            actual_amount = ((UniMath.sqrt(delta_val)) - uint(_reserve1*(2000  -FEE))) / 2*(1-FEE);
        }   
    }

    function _getAmountOut(uint _reserve1, uint _reserve2, uint optimal_val) internal pure returns(uint _amountOut) {
        require(_reserve1 != 0 && _reserve2 != 0, 'invalid inputs');
        uint first_cal = _reserve2*((1000-FEE)*optimal_val);
        uint second_cal = _reserve1 + ((1000-FEE)*optimal_val);

        _amountOut = first_cal.div(second_cal);
    }


    function oneSideAddingLiquiduty(address _token1, address _token2, uint _amout_for_token1) 
    external
    amountAndTokensCheck(_token1, _token2, _amout_for_token1)
    returns(bool)  {
        address pair_ = IUniswapV2Factory(UNISWAP_V2_FACTORY).getPair(_token1, _token2);
        (uint reserve1_, uint reserve2_, ) = IUniswapV2Pair(pair_).getReserves();

        // defining which token will be add to pool
        uint swapOptimalAmount = IUniswapV2Pair(pair_).token0() == _token1 ? // Token0 -> TokenB
            _getOptimalAmountForSwapFirstPair(_amout_for_token1, reserve1_) : // TokenB -> TokenA
                _getOptimalAmountForSwapFirstPair(_amout_for_token1, reserve2_);
        
        uint amountOut = _getAmountOut(reserve1_, reserve2_, swapOptimalAmount);
        require(amountOut > 0, 'An error occured due _getAmountOut function');

        _swapping(_token1, _token2, swapOptimalAmount, 1, msg.sender);
        (uint a_, uint b_, uint liq_) = _bothSideAddingLiquidity(_token1, _token2, swapOptimalAmount, amountOut, msg.sender, block.timestamp+10800);
        assert(a_ != 0 && b_ != 0);
        assert(liq_ != 0);
        return true;
    }

    function removingLiquidity() external {}

    function efficientLiquidityCalculation() external {}
}