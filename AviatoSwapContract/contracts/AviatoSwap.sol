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
import "./TokenA.sol";
import "./TokenB.sol";

contract Aviatoswap is Ownable, ReentrancyGuard, TokenA{
    using SafeMath for uint;
    using Math for uint;

    address private FIRST_PAIR;
    address private immutable WETH = 0xC02aaA39b223FE8D0A0e5C4F27eAD9083C756Cc2;
    address private immutable DAI = 0x6B175474E89094C44Da98b954EedeAC495271d0F;
    address private immutable WBTC= 0x2260FAC5E5542a773Aa44fBCfeDf7C193bc2C599;
    address private SECOND_PAIR;

    address private constant UNISWAP_V2_ROUTER = 0x7a250d5630B4cF539739dF2C5dAcb4c659F2488D;

    function swapping(address _first_pair, address _second_pair, uint _amountIn, uint _amountOutMin, address _to) 
    external nonReentrant{
        require(_first_pair != address(0) && _second_pair != address(0));
        FIRST_PAIR = _first_pair;
        SECOND_PAIR = _second_pair;

        IERC20(FIRST_PAIR).transferFrom(msg.sender, address(this), _amountIn);
        IERC20(FIRST_PAIR).approve(UNISWAP_V2_ROUTER, _amountIn);

        address[] memory path = new address[](3);
        path[0] = FIRST_PAIR;
        path[1] = WETH;
        path[2] = SECOND_PAIR;

        IUniswapV2Router(UNISWAP_V2_ROUTER).swapExactTokensForTokens(
            _amountIn, _amountOutMin, path, _to, block.timestamp+10800);
    }

    function bothSideAddingLiquidity(address _tokenA, address _tokenB, uint _amountA, uint _amountB, uint _amountAMin, uint _amountBMin, address _to, uint _death_time)
    external 
    returns(uint amountA, uint amountB, uint liquidity) {
        require(_tokenA != address(0) && _tokenB != address(0), 'invalid token address');
        require(_amountA != 0 && _amountB != 0, 'invalid amount for swao');
        require(_amountAMin <= _amountA && _amountBMin <= _amountB, 'invalid minimum amount');
        require(_to != address(0), 'invalid destination address');
        require(_death_time >= block.timestamp);

        // trasfering and approving
        IERC20(_tokenA).transferFrom(msg.sender, address(this), _amountA);
        IERC20(_tokenB).transferFrom(msg.sender, address(this), _amountB);

        IERC20(_tokenA).approve(UNISWAP_V2_ROUTER, _amountA);
        IERC20(_tokenB).approve(UNISWAP_V2_ROUTER, _amountB);

        (amountA, amountB, liquidity) = IUniswapV2Router(UNISWAP_V2_ROUTER).addLiquidity(
            _tokenA, _tokenB, _amountA, _amountB, _amountAMin, _amountBMin, _to, block.timestamp+10800);
    }

    function oneSideAddingLiquiduty() external {}

    function removingLiquidity() external {}

    function efficientLiquidityCalculation() external {}
}