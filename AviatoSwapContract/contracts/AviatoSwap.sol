// SPDX-License-Identifier: MIT
pragma solidity ^0.8.11;

import "@openzeppelin/contracts/utils/math/SafeMath.sol";
import "@openzeppelin/contracts/utils/math/Math.sol";
import "@openzeppelin/contracts/token/ERC20/ERC20.sol";
import "@openzeppelin/contracts/token/ERC20/IERC20.sol";
import "@openzeppelin/contracts/access/Ownable.sol";
import "@openzeppelin/contracts/security/ReentrancyGuard.sol";

import "@uniswap-periphery/contracts/interfaces/IUniswapV2Router01.sol";
import '@uniswap/contracts/interfaces/IUniswapV2Factory.sol';
import '@uniswap/contracts/interfaces/IUniswapV2Pair.sol';
// import { IUniswapV2Router } from "../interfaces/IUniswap.sol";
import { UniMath, UQ112x112 } from "./InternalMath.sol";
import "./TokenA.sol";
import "./TokenB.sol";

contract Aviatoswap is ReentrancyGuard, Ownable{
    using SafeMath for uint;
    using Math for uint;
    using UniMath for uint;

    bool private initialized = false; // for Proxy contract logic
    uint private init_count = 0;

    address private constant WETH = 0xC02aaA39b223FE8D0A0e5C4F27eAD9083C756Cc2;
    address private constant UNISWAP_V2_ROUTER01 = 0xf164fC0Ec4E93095b804a4795bBe1e041497b92a;
    // address private constant UNISWAP_V2_ROUTER = 0x7a250d5630B4cF539739dF2C5dAcb4c659F2488D; // in mainnet-fork
    address private constant UNISWAP_V2_FACTORY = 0x5C69bEe701ef814a2B6a3EDD4B1652CB9cc5aA6f; // in mainnet-fork

    uint private constant FEE = (3 * 1e18 / 100) / 10; // will div to 1e18 to return 0.3%

    event logUint(string indexed _message, uint indexed calculated_result);
    event logTransfered(address indexed _from, address indexed _to, uint _amount);
    event logSwapped(address indexed _to, uint indexed _amount);
    event logLiquidityAdded(uint indexed _amount1, uint indexed _amount2, uint indexed liqAmount);
    event logError(string indexed _message, uint indexed _error_code);
    event LogBalance(uint indexed BalanceOfReserve1, uint indexed BalanceOfReserve2, uint indexed BalanceOfLiquidityToken);
    event LogAllowance(uint indexed allowance);

    modifier amountAndTokensCheck(address _token1, address _token2, uint _amount1) {
        require(_token1 != address(0) && _token2 != address(0), 'invalid token address');
        require(_amount1 != 0, 'invalid amount for swao');
        _;
    }   


    function initialize() external payable {
        require(initialized == false, "Contract has initialized once before");
        require(init_count < 3, "This contract just could upgrade twice");
        transferOwnership(msg.sender); // To Proxy Admin address which is a DAO protocol
        initialized = true;   
        init_count ++;
    }



    /** NOTE: this function is temporary function */
    function getLiquidityBalanceOfPairs(address _token1, address _token2) 
    public  
    returns(uint _reserve1, uint _reserve2, uint _liq_balance) {
        require(_token1 != address(0) && _token2 != address(0), "invalid address inserted");
        
        address pair = IUniswapV2Factory(UNISWAP_V2_FACTORY).getPair(_token1, _token2);
        // require(IUniswapV2Pair(pair).token0() == _token2 && IUniswapV2Pair(pair).token1() == _token1, 
        //     "Some error occured in pair section");
        
        (uint res1_balance, uint res2_balance, ) = IUniswapV2Pair(pair).getReserves();
        uint liquidity_token_balance = IUniswapV2Pair(pair).balanceOf(msg.sender);

        emit LogBalance(res1_balance, res2_balance, liquidity_token_balance);
        (_reserve1, _reserve2, _liq_balance) = (res1_balance, res2_balance, liquidity_token_balance);
    }




    /**
     * NOTE: The Fee variable ignored due to unsupporting decimals in EVM
     * @dev The actual calculation is based on following but because of unsupporting decimals in solidity we remove the fee plot
     *      uint delta_val = uint((_reserve1 * (2000 - FEE)) * 2) + (4 * (1000 - FEE) * (_amount * _reserve1));
     *      actual_amount = ((UniMath.sqrt(delta_val)) - uint(_reserve1 *( 2000  - FEE))) / 2 * (1000 - FEE); 

     * @dev Calculates the optimal amount of tokens to swap in a Uniswap trade.
     * @dev This function will re-build with inline assembly, ASAP still has some vulnerability!  
     * @param _amountA The amount of tokens to swap.
     * @param _reserveA The reserve of the token being swapped.
     * @return actual_amount The actual amount of tokens to swap.
     */

    function _getOptimalAmtAtoGetSwapAmtA(uint _amountA, uint _reserveA) public pure returns(uint) {
        require(_reserveA * _amountA != 0, "invalid amount inserted");
        uint delta_val = (2 * _reserveA) * (2 * _reserveA) + 4 * (_amountA * _reserveA);
        uint amountAToSwap = uint(UniMath.sqrt(delta_val) - (2 * _reserveA)).div(2);
        return amountAToSwap;
    }



    /** NOTE: This function will calculate off-chain */
    function _getAmountOut(uint _reserve1, uint _reserve2, uint optimal_val) 
    public 
    pure 
    returns(uint _amountOut) {
        require(_reserve1 != 0 && _reserve2 != 0, 'invalid inputs');

        uint first_cal = _reserve2 * optimal_val;
        uint second_cal = _reserve1 * optimal_val;

        _amountOut = first_cal.div(second_cal);
    }


    
    /** NOTE: Optimal value for input will calculate Off-chain
     *  @dev This function calculate amount of Lp token to burn for remove Liquidity function
             based on the min percentage of reserve tokens amount and desire amout to remove from liquidity pool

     *  @param _amountA is desire amount of token A to remove from liquidity pool
     *  @param _amountB is desire amount of token B to remove from liquidity pool
     *  @param _reserveA is the reserve amount of token A inside pair contract
     *  @param _reserveB is the reserve amount of token B inside pair contract
      * @param _totalLpToken is the IUniswapV2Pair.balanceOf(msg.sender) inside pair contract
    */
    function _calculateAmountOfLpTokenForBurn(uint _amountA, uint _amountB, uint _reserveA, uint _reserveB, uint _totalLpToken)
    public 
    pure
    returns(uint result) {
        require(_amountA != 0 && _amountB != 0, "invalid inputs");
        
        uint percentageA = (_amountA.mul(100)).div(_reserveA); // 50
        uint percentageB = ((_amountB.mul(100)).div(_reserveB)); // 40
        uint MinPercentage = (Math.min(percentageA, percentageB)).div(10); // 4
        // e.g. 40% ~ 0.4 ~ 4(the MinPercentage valur for this example)

        result =  (_totalLpToken.mul(MinPercentage)).div(10);
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
        nonReentrant()
    {
        require(_first_pair != address(0) && _second_pair != address(0), "Invalid token pair address");
        require(_to != address(0), "Invalid destination address");


        require(IERC20(_first_pair).allowance(msg.sender, address(this)) >= _amountIn, "Insufficient allowance for aviato swap");
        // approval will accomplish off-chain
        IERC20(_first_pair).transferFrom(msg.sender, address(this), _amountIn);

        // The caller of this part is address(this)
        IERC20(_first_pair).approve(UNISWAP_V2_ROUTER01, _amountIn); // Allowing UNISWAPV2Router01 to swap tokens
        require(IERC20(_first_pair).allowance(address(this), UNISWAP_V2_ROUTER01) == _amountIn, "allowance for unisawp_router_01 is not provided");


        // based on UniswapV2 documentation
        address[] memory path = new address[](3);
        path[0] = _first_pair;
        path[1] = WETH; // considered as swap bridge
        path[2] = _second_pair;

        // In this part, the caller is address(this)
        IUniswapV2Router01(UNISWAP_V2_ROUTER01).swapExactTokensForTokens(
            _amountIn, _amountOutMin, path, _to, block.timestamp);
    }


    /**
     * @dev Adds liquidity to a Uniswap pool with both tokens being added simultaneously.
     * @param _tokenA The address of token A.
     * @param _tokenB The address of token B.
     * @param _amountA The amount of token A to add.
     * @param _amountB The amount of token B to add.
     * @param _to The address to receive the liquidity tokens.
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
        uint deathtime
    ) public  nonReentrant() returns(uint amountA, uint amountB, uint liquidity) {
        // require(_death_time >= block.timestamp && _amountB != 0, "Invalid death time or amount B");
        require(_to != address(0), "Invalid destination address");

        IERC20(_tokenA).transferFrom(msg.sender, address(this), _amountA);
        IERC20(_tokenB).transferFrom(msg.sender, address(this), _amountB);
        // Allowing the Uniswap router to spend the transferred tokens
        IERC20(_tokenA).approve(UNISWAP_V2_ROUTER01, _amountA);
        IERC20(_tokenB).approve(UNISWAP_V2_ROUTER01, _amountB);

        // Add liquidity to the pool using the Uniswap router
        (amountA, amountB, liquidity) = IUniswapV2Router01(UNISWAP_V2_ROUTER01).addLiquidity(
            _tokenA, _tokenB, _amountA, _amountB, 1, 1, _to, block.timestamp + 10800
        );

        emit logLiquidityAdded(amountA, amountB, liquidity);
    }




    /**
     * @dev oneSidedAddingLiquidity function for adding tokens in optimal amount without any remaining return
     * @param _token1 is the address of Token A
     * @param _token2 is the address if Token B
     * @param _amount_token_for_add is the amount of X token assumed for adding to the liquidity
     */
    function oneSideAddingLiquiduty(address _token1, address _token2, uint _amount_token_for_add) 
    external
    nonReentrant()
    returns(bool)  {
        address pair_ = IUniswapV2Factory(UNISWAP_V2_FACTORY).getPair(_token1, _token2);
        (uint reserve1_, uint reserve2_, ) = IUniswapV2Pair(pair_).getReserves();

        // defining which token will be add to pool
        uint swapOptimalAmount = IUniswapV2Pair(pair_).token0() == _token1 ? // TokenA -> TokenB
            _getOptimalAmtAtoGetSwapAmtA(_amount_token_for_add, reserve1_) : // TokenB -> TokenA
                _getOptimalAmtAtoGetSwapAmtA(_amount_token_for_add, reserve2_);
        
        uint amountOut = _getAmountOut(reserve1_, reserve2_, swapOptimalAmount);
        require(amountOut > 0, 'An error occured due _getAmountOut function');

        swapping(_token1, _token2, swapOptimalAmount, 1, msg.sender);
        (uint a_, uint b_, uint liq_) = _bothSideAddingLiquidity(_token1, _token2, swapOptimalAmount, amountOut, msg.sender, block.timestamp + 10800);
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
        // require(IUniswapV2Pair(pair).token0() == _token1 && IUniswapV2Pair(pair).token1() == _token2, 
        //     "Some error occured in pair section");

        (uint _reserve1, uint _reserve2, ) = IUniswapV2Pair(pair).getReserves(); // timestamp exist in 3nd arg
        uint liquidity_balance = IUniswapV2Pair(pair).balanceOf(msg.sender);

        emit LogAllowance(IUniswapV2Pair(pair).allowance(msg.sender, UNISWAP_V2_ROUTER01));
        // senario No.1 : not whole Lp tokens:
        if(_reserve1.add(_reserve2) != _amount1.add(_amount2)) {
            uint LpAmountForBurn = _calculateAmountOfLpTokenForBurn(_amount1, _amount2, _reserve1, _reserve2, liquidity_balance);

            require(IUniswapV2Pair(pair).allowance(msg.sender, pair) >= LpAmountForBurn, "Allowance amount is less than lp_amount for burn");
            require(liquidity_balance >= LpAmountForBurn, "Something went wrong in removeLiquidity");

            emit logUint("Lp token amount clculated by internal function", LpAmountForBurn);
            emit LogBalance(_reserve1, _reserve2, liquidity_balance);

            // The bug is due to this approval section that throw (ds-math-sub-underflow) error
            (amount_back1, amount_back2) = IUniswapV2Router01(UNISWAP_V2_ROUTER01).removeLiquidity(
                _token1, _token2, LpAmountForBurn, 1, 1, msg.sender, block.timestamp + 3600); 
        }   

        // Senario No.2 : Whole Lp token will burn from liquidity pool:
        require(IUniswapV2Pair(pair).allowance(msg.sender, pair) == liquidity_balance, "Allowance is not equal to liquidity balance for burning whole liquidity tokens");
        (amount_back1, amount_back2) = IUniswapV2Router01(UNISWAP_V2_ROUTER01).removeLiquidity(
            _token1, _token2, liquidity_balance, 1, 1, msg.sender, block.timestamp + 3600);
        
        assert(amount_back1 * amount_back2 != 0); // non of those amount back should be 0
    }
}
