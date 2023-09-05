// SPDX-License-Identifier: MIT
pragma solidity ^0.8.11;

import "@openzeppelin/contracts/utils/math/SafeMath.sol";
import "@openzeppelin/contracts/utils/math/Math.sol";
import "@openzeppelin/contracts/token/ERC20/ERC20.sol";
import "@openzeppelin/contracts/token/ERC20/IERC20.sol";
import "@openzeppelin/contracts/access/Ownable.sol";
import "@openzeppelin/contracts/security/ReentrancyGuard.sol";

import '@uniswap/contracts/interfaces/IUniswapV2Factory.sol';
import { IUniswapV2Router } from "./Uniswap.sol";
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

    // constructor(address _first_pair, address _second_pair) {
    // }

    function swapping(address _first_pair, address _second_pair, uint _amountIn, uint _amountOutMin, address _to) 
    external nonReentrant{
        require(_first_pair != address(0) && _second_pair != address(0));
        FIRST_PAIR = _first_pair;
        SECOND_PAIR = _second_pair;

        IERC20(FIRST_PAIR).transferFrom(msg.sender, address(this), _amountIn);
        IERC20(FIRST_PAIR).approve(UNISWAP_V2_ROUTER, _amountIn);

        address[] memory path = new address[](3);
        path[0] = address(FIRST_PAIR);
        path[1] = address(WETH);
        path[2] = address(SECOND_PAIR);

        IUniswapV2Router(UNISWAP_V2_ROUTER).swapExactTokensForTokens(
            _amountIn, _amountOutMin, path, _to, block.timestamp+10800);
    }

    function addingLiquidity() external {}

    function removingLiquidity() external {}

    function efficientLiquidityCalculation() external {}
}