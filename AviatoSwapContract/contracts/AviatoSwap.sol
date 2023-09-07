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

    /**
     * @dev Swaps tokens on the Uniswap decentralized exchange.
     * @param _first_pair The address of the first token pair to swap.
     * @param _second_pair The address of the second token pair to swap.
     * @param _amountIn The amount of tokens to swap.
     * @param _amountOutMin The minimum amount of tokens to receive from the swap.
     * @param _to The address to receive the swapped tokens.
     */
    function swapping(address _first_pair, address _second_pair, uint _amountIn, uint _amountOutMin, address _to) 
        public 
        amountAndTokensCheck(_first_pair, _second_pair, _amountIn)
        nonReentrant()
    {
        require(_first_pair != address(0) && _second_pair != address(0), "Invalid token pair address");
        require(_to != address(0), "Invalid destination address");

        FIRST_PAIR = _first_pair;
        SECOND_PAIR = _second_pair;

        IERC20(FIRST_PAIR).transferFrom(msg.sender, address(this), _amountIn);
        IERC20(FIRST_PAIR).approve(UNISWAP_V2_ROUTER, _amountIn);

        address[] memory path = new address[](3);
        path[0] = FIRST_PAIR;
        path[1] = WETH; // considered as swap bridge
        path[2] = SECOND_PAIR;

        IUniswapV2Router(UNISWAP_V2_ROUTER).swapExactTokensForTokens(
            _amountIn, _amountOutMin, path, _to, block.timestamp + 10800);
    }


    /**
     * @dev Adds liquidity to a Uniswap pool with both tokens being added simultaneously.
     * @param _tokenA The address of token A.
     * @param _tokenB The address of token B.
     * @param _amountA The amount of token A to add.
     * @param _amountB The amount of token B to add.
     * @param _to The address to receive the liquidity tokens.
     * @param _death_time The timestamp when the liquidity can be removed.
     * @return amountA The actual amount of token A that was added to the pool.
     * @return amountB The actual amount of token B that was added to the pool.
     * @return liquidity The amount of liquidity tokens received.
     */
    function _bothSideAddingLiquidity(
        address _tokenA,
        address _tokenB,
        uint _amountA,
        uint _amountB,
        address _to,
        uint _death_time
    ) public  nonReentrant() returns(uint amountA, uint amountB, uint liquidity) {
        require(_death_time >= block.timestamp && _amountB != 0, "Invalid death time or amount B");
        require(_to != address(0), "Invalid destination address");
        // require(IERC20(_tokenA).allowance(msg.sender, address(this)) != 0);
        // require(IERC20(_tokenB).allowance(msg.sender, address(this)) != 0);


        // Transfer tokens from the caller to the contract
        IERC20(_tokenA).transferFrom(msg.sender, address(this), _amountA);
        IERC20(_tokenB).transferFrom(msg.sender, address(this), _amountB);
        // Approve the Uniswap router to spend the transferred tokens
        IERC20(_tokenA).approve(UNISWAP_V2_ROUTER, _amountA);
        IERC20(_tokenB).approve(UNISWAP_V2_ROUTER, _amountB);

        // Add liquidity to the pool using the Uniswap router
        (amountA, amountB, liquidity) = IUniswapV2Router(UNISWAP_V2_ROUTER).addLiquidity(
            _tokenA, _tokenB, _amountA, _amountB, 1, 1, _to, block.timestamp + 10800
        );
    }


    /** 
     * @dev Calculates the optimal amount of tokens to swap in a Uniswap trade.
     * @dev This function will re-build with inline assembly, ASAP still has some vulnerability!  
     * @param _amount The amount of tokens to swap.
     * @param _reserve1 The reserve of the token being swapped.
     * @return actual_amount The actual amount of tokens to swap.
     */
    function _getOptimalAmountForSwapFirstPair(uint _amount, uint _reserve1) internal pure returns(uint actual_amount) {
        require(_amount != 0 && _reserve1 != 0, 'invalid inputs');
        // We have : (1-f)s^2 + A(2-f)s - aA = 0  -> s=?
        uint delta_val = uint((_reserve1 * (2000 - FEE)) * 2) + (4 * (1000 - FEE) * (_amount * _reserve1));
        actual_amount = ((UniMath.sqrt(delta_val)) - uint(_reserve1 *( 2000  - FEE))) / 2 * (1000 - FEE);
    }


    function _getAmountOut(uint _reserve1, uint _reserve2, uint optimal_val) internal pure returns(uint _amountOut) {
        require(_reserve1 != 0 && _reserve2 != 0, 'invalid inputs');
        uint first_cal = _reserve2*((1000-FEE)*optimal_val);
        uint second_cal = _reserve1 + ((1000-FEE)*optimal_val);

        _amountOut = first_cal.div(second_cal);
    }


    /** @dev Optimal value for input will calculate Off-chain */
    function _calculateAmountOfLpTokenForBurn(uint _amountA, uint _amountB, uint _reserveA, uint _reserveB, uint _totalLpToken)
    internal 
    pure 
    returns(uint willBurn) {
        require(_amountA != 0 && _amountB != 0, "invalid inputs");
        uint percentageA = (_amountA.div(_reserveA)).mul(100);
        uint percentageB = (_amountB.div(_reserveB)).mul(100);
        uint MinPercentage = (Math.min(percentageA, percentageB)).div(10); 
        // e.g. 40% ~ 0.4 ~ 4(the MinPercentage valur for this example)

        willBurn = _totalLpToken.div(MinPercentage);
    }


    function oneSideAddingLiquiduty(address _token1, address _token2, uint _amout_for_token1) 
    external
    nonReentrant()
    amountAndTokensCheck(_token1, _token2, _amout_for_token1)
    returns(bool)  {
        address pair_ = IUniswapV2Factory(UNISWAP_V2_FACTORY).getPair(_token1, _token2);
        (uint reserve1_, uint reserve2_, ) = IUniswapV2Pair(pair_).getReserves();

        // defining which token will be add to pool
        uint swapOptimalAmount = IUniswapV2Pair(pair_).token0() == _token1 ? // TokenA -> TokenB
            _getOptimalAmountForSwapFirstPair(_amout_for_token1, reserve1_) : // TokenB -> TokenA
                _getOptimalAmountForSwapFirstPair(_amout_for_token1, reserve2_);
        
        uint amountOut = _getAmountOut(reserve1_, reserve2_, swapOptimalAmount);
        require(amountOut > 0, 'An error occured due _getAmountOut function');

        swapping(_token1, _token2, swapOptimalAmount, 1, msg.sender);
        (uint a_, uint b_, uint liq_) = _bothSideAddingLiquidity(_token1, _token2, swapOptimalAmount, amountOut, msg.sender, block.timestamp+10800);
        assert(a_ != 0 && b_ != 0);
        assert(liq_ != 0);
        return true;
    }
    

    function removingLiquidity(address _token1, address _token2, uint _amount1, uint _amount2)
    external 
    nonReentrant()
    returns(uint amount_back1, uint amount_back2) {
        // get pair
        address pair = IUniswapV2Factory(UNISWAP_V2_FACTORY).getPair(_token1, _token2); 
        require(IUniswapV2Pair(pair).token0() == _token1 && IUniswapV2Pair(pair).token1() == _token2, 
            "Some error occured in pair section");

        (uint _reserve1, uint _reserve2, ) = IUniswapV2Pair(pair).getReserves();
        uint liquidity_balance = IUniswapV2Pair(pair).balanceOf(address(this));

        // senario No.1 : not whole Lp tokens:
        if(_reserve1.add(_reserve2) != _amount1.add(_amount2)) {
            uint LpAmountForBurn = _calculateAmountOfLpTokenForBurn(_amount1, _amount2, _reserve1, _reserve2, liquidity_balance);
            require(LpAmountForBurn < liquidity_balance, "Something went wrong in removeLiquidity");

            IERC20(pair).approve(UNISWAP_V2_ROUTER, LpAmountForBurn);
            (amount_back1, amount_back2) = IUniswapV2Router(UNISWAP_V2_ROUTER).removeLiquidity(_token1, _token2, LpAmountForBurn, 1, 1, msg.sender, block.timestamp + 10800); 
        }

        // Senario No.2 : Whole Lp token will remove from liquidity pool:
        IERC20(pair).approve(UNISWAP_V2_ROUTER, liquidity_balance);
        (amount_back1, amount_back2) = IUniswapV2Router(UNISWAP_V2_ROUTER).removeLiquidity(_token1, _token2, liquidity_balance, 1, 1, msg.sender, block.timestamp + 10800);
    }

}