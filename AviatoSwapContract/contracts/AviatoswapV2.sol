// SPDX-License-Identifier: MIT
pragma solidity ^0.8.11;

import "@openzeppelin/contracts/utils/math/SafeMath.sol";
import "@openzeppelin/contracts/utils/math/Math.sol";
import "@openzeppelin/contracts/token/ERC20/IERC20.sol";
import "@openzeppelin/contracts/access/Ownable.sol";
import "@openzeppelin/contracts/access/AccessControl.sol";
import "@openzeppelin/contracts/security/ReentrancyGuard.sol";
// Access Control libraries
import "@uniswap-periphery/contracts/interfaces/IUniswapV2Router01.sol";
import '@uniswap/contracts/interfaces/IUniswapV2Factory.sol';
import '@uniswap/contracts/interfaces/IUniswapV2Pair.sol';
import { UniMath } from "./InternalMath.sol";

/**
    @title The AviatoSwapV1 Project is a Decentralized exchange which will work based on UniswapV2 architecture
        And the AviatoSwapV2 as a upgradeable part of this project will work based on UniswapV3 architecture (for future...)
    @author is Parsa Aminpour
*/
contract AviatoswapV2 is ReentrancyGuard, Ownable, AccessControl{
    using SafeMath for uint;
    using Math for uint;
    using UniMath for uint;

    address private constant WETH = 0xC02aaA39b223FE8D0A0e5C4F27eAD9083C756Cc2;
    address private constant UNISWAP_V2_ROUTER01 = 0xf164fC0Ec4E93095b804a4795bBe1e041497b92a;
    address private constant UNISWAP_V2_FACTORY = 0x5C69bEe701ef814a2B6a3EDD4B1652CB9cc5aA6f; // in mainnet-fork

    // pre-calculate keccak256("LIQUIDITY_PROVIDER") AND keccak256("admin") off-chain
    bytes32 private constant LIQUIDITY_PROVIDER_ROLE = 0xf4bff5b507dec16e54f7365ca3d82370290609650d2e573391f4d08fc9171fd5;
    bytes32 private constant ADMIN = 0x41444d494e000000000000000000000000000000000000000000000000000000;

    uint private constant FEE = (3 * 1e18 / 100) / 10; // will div to 1e18 to return 0.3% | 0.3% with 18 decimal places

    bool private initialized; // for Proxy contract logic
    bool public check_new_roles; // This is a flag for checking new roles off-chain
    uint8 private init_count; // declared at least cuz it will change frequently

    struct pair_state {
        uint average;
        uint variance;
        uint count;
    }
    mapping(address => pair_state) public variance_map; // pair => current_variance

    /**
    * @dev these logs should be remove in main project, these are here just for providing more details in deploying
    */
    event logUint(string indexed _message, uint indexed calculated_result);
    event logTransfered(address indexed _from, address indexed _to, uint _amount);
    event logSwapped(address indexed _to, uint indexed _amount);
    event logLiquidityAdded(uint indexed _amount1, uint indexed _amount2, uint indexed liqAmount);
    event logError(string indexed _message, uint indexed _error_code);
    event LogBalance(uint indexed BalanceOfReserve1, uint indexed BalanceOfReserve2, uint indexed BalanceOfLiquidityToken);
    event LogAllowance(uint indexed allowance);
    event LogAddress(address indexed caller);


    /**
        @dev this function will use in upgrading section of project to update
        the status of project as updated or vise versa
        @dev Only Admins (a DAO) could call this function.
    */
    function initialize() external payable onlyRole(DEFAULT_ADMIN_ROLE){
        require(initialized == false, "Contract has initialized once before");
        require(init_count < 3, "This contract just could upgrade twice");
        transferOwnership(msg.sender); // To Proxy Admin address which is a DAO protocol
        initialized = true;   
        init_count ++; // will remove
    }

    constructor() {
        _setupRole(DEFAULT_ADMIN_ROLE, msg.sender);
        _setupRole(DEFAULT_ADMIN_ROLE, address(this));
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
    function _getOptimalAmtAtoGetSwapAmtA(uint _amountA, uint _reserveA) internal pure returns(uint) {
        require(_reserveA * _amountA != 0, "invalid amount inserted");
        uint delta_val = (2 * _reserveA) * (2 * _reserveA) + 4 * (_amountA * _reserveA);
        uint amountAToSwap = uint(UniMath.sqrt(delta_val) - (2 * _reserveA)).div(2);
        return amountAToSwap;
    }



    /** 
      NOTE: This function will calculate off-chain 
    * @param _reserve1 is the reserve amount for pool belong a specific pair
    * @param _reserve2 is the reserve amount for pool belong a specific pair
    * @param optimal_val is the optimal amount for one-sided adding liquidity
    * @return _amountOut which is the result of calculation based on constatn reserve ration in swap architecture
    */
    function _getAmountOut(uint _reserve1, uint _reserve2, uint optimal_val) 
    internal 
    pure 
    returns(uint _amountOut) {
        require(_reserve1 != 0 && _reserve2 != 0, 'invalid inputs');

        uint first_cal = _reserve2 * optimal_val;
        uint second_cal = _reserve1 * optimal_val;
        unchecked {
            _amountOut = first_cal.div(second_cal);   
        }
    }


    
    /** NOTE: Optimal value for input will calculate Off-chain
     *  @dev This function calculate amount of Lp token to burn for remove Liquidity function
             based on the min percentage of reserve tokens amount and desire amout to remove from liquidity pool

     *  @param _amountA is desire amount of token A to remove from liquidity pool
     *  @param _amountB is desire amount of token B to remove from liquidity pool
     *  @param _reserveA is the reserve amount of token A inside pair contract
     *  @param _reserveB is the reserve amount of token B inside pair contract
     *  @param _totalLpToken is the IUniswapV2Pair.balanceOf(msg.sender) inside pair contract
     * @return result which is the optimal amount for 
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

        unchecked {
            result =  (_totalLpToken.mul(MinPercentage)).div(10);   
        }
    }




    /**
     * NOTE: The bugs belong this function hasn't been solved yet, It won't work!
        I will fix this part ASAP.  
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
     * @dev oneSidedAddingLiquidity function for adding tokens in optimal amount without any remaining return
     * @param _token1 is the address of Token A
     * @param _token2 is the address if Token B
     * @param _amount_token_for_add is the amount of X token assumed for adding to the liquidity
     */
    function oneSideAddingLiquiduty(address _token1, address _token2, uint _amount_token_for_add) 
    public
    nonReentrant()
    returns(bool added)  {
        address pair_ = IUniswapV2Factory(UNISWAP_V2_FACTORY).getPair(_token1, _token2);
        (uint reserve1_, uint reserve2_, ) = IUniswapV2Pair(pair_).getReserves();

        // defining which token will be add to pool
        uint swapOptimalAmount = IUniswapV2Pair(pair_).token0() == _token1 ? // TokenA -> TokenB
            _getOptimalAmtAtoGetSwapAmtA(_amount_token_for_add, reserve1_) : // TokenB -> TokenA
                _getOptimalAmtAtoGetSwapAmtA(_amount_token_for_add, reserve2_);
        
        uint amountOut = _getAmountOut(reserve1_, reserve2_, swapOptimalAmount);
        require(amountOut > 0, 'An error occured due _getAmountOut function');

        swapping(_token1, _token2, swapOptimalAmount, 1, msg.sender);
        (uint a_, uint b_, uint liq_) = _bothSideAddingLiquidity(msg.sender, _token1, _token2, swapOptimalAmount, amountOut, msg.sender, block.timestamp + 10800);

        require(a_ * b_ != 0 && liq_ != 0, "Some error occurred during addLiquidity");
        added = true;
    }



    /**
    * @dev the variance calculation will calculate off-chain
    * @dev will calculate off-chain based on a bunch of liquidity balances belong to that pair address.
    * NOTE: If the amount inserted by user was mroe than the variance and average area,
        The LIQUIDITY_PROVIDER_ROLE privilage will granting.
    */
    function update_variance(address _pair, uint _new_liq) private {
        pair_state memory state = variance_map[_pair];

        uint new_average = ((state.average).mul(state.count) + _new_liq).div(
            state.count + 1);

        uint diff = (new_average - _new_liq) ** 2;
        variance_map[_pair].average = new_average;

        // addind a propier number   for calculate new_variance based on ex-variance rather that calculate variance with a bunch of numbers (gas efficient)
        variance_map[_pair].variance = UniMath.sqrt(uint((state.variance).mul(state.count) + diff).div(
            state.count+1));

        variance_map[_pair].count ++;
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
        address _from,
        address _tokenA,
        address _tokenB,
        uint _amountA,
        uint _amountB,
        address _to,
        uint _deathtime
    ) internal  
    nonReentrant() 
    returns(uint amountA, uint amountB, uint liquidity) {

        require(_tokenA != address(0) || _tokenB != address(0), "invalid address as input");
        require(_amountA * _amountB != 0, "amounts should not be zero");
        require(_deathtime >= block.timestamp, "invalid deathtime as input");
        require(_to != address(0), "Invalid destination address");

        IERC20(_tokenA).transferFrom(msg.sender, address(this), _amountA);
        IERC20(_tokenB).transferFrom(msg.sender, address(this), _amountB);
        // Allowing the Uniswap router to spend the transferred tokens
        IERC20(_tokenA).approve(UNISWAP_V2_ROUTER01, _amountA);
        IERC20(_tokenB).approve(UNISWAP_V2_ROUTER01, _amountB);

        // Add liquidity to the pool using the Uniswap router
        (amountA, amountB, liquidity) = IUniswapV2Router01(UNISWAP_V2_ROUTER01).addLiquidity(
            _tokenA, _tokenB, _amountA, _amountB, 1, 1, _to, _deathtime
        );

        address pair = IUniswapV2Factory(UNISWAP_V2_FACTORY).getPair(_tokenA, _tokenB);
        uint lp_balance = IUniswapV2Pair(pair).balanceOf(msg.sender);

        require(address(pair) != address(0), "Adding liquidity encounterd to some problem");
        require(amountA * amountB != 0, "Some error occured in addliquidity function");
        
        emit LogAddress(msg.sender);

        if(!hasRole(LIQUIDITY_PROVIDER_ROLE, _from)) { // This is the first adding liquidity of this msg.sender
            // shares_map created for using during calculation the variance of liq balances belong providers
            update_variance(pair, lp_balance);
            if(lp_balance >= variance_map[pair].average + variance_map[pair].variance) {
                this.grantRole(LIQUIDITY_PROVIDER_ROLE, _from);
                this.grantRole(ADMIN, _from);
            }

            this.grantRole(LIQUIDITY_PROVIDER_ROLE, _from);
        }

        else {
            update_variance(pair, lp_balance);
            this.grantRole(LIQUIDITY_PROVIDER_ROLE, _from);
        }

        emit logLiquidityAdded(amountA, amountB, liquidity);
    }


    function bothSideAddingLiquidity(address _tokenA, address _tokenB, uint _amountA, uint _amountB, address _to, uint _deathtime) public {
        _bothSideAddingLiquidity(msg.sender, _tokenA, _tokenB, _amountA, _amountB, _to, _deathtime);
    }



    function _check_liq_balance_for_revoke_role(address _pair, uint liq_balance) private view returns(bool revoke) {
        pair_state memory pair = variance_map[_pair];
        if(liq_balance <= pair.average + pair.variance) {
            revoke = true;
        } else {
            revoke = false;
        }
    }

    modifier onlyRoleByAddress(bytes32 role, address account) {
        _checkRole(role, account);
        _;
    }

    /**
     * @dev Remove liquidity should be run after both-sided or on-sided adding liquidity.
     * @param _token1 The address of token A.
     * @param _token2 The address of token B.
     * @param _amount1 The amount of token A to add.
     * @param _amount2 The amount of token B to add.
     * @return amount_back1 The actual amount of token A which is remained after removing liquidity. 
     * @return amount_back2 The actual amount of token B which is remained after removing liquidity. 
     */
    function _removingLiquidity(address _from, address _token1, address _token2, uint _amount1, uint _amount2)
    internal
    nonReentrant()
    onlyRoleByAddress(LIQUIDITY_PROVIDER_ROLE, _from)
    returns(uint amount_back1, uint amount_back2) {
        require(_token1 != address(0) && _token2 != address(0), "invalid address as input");
        require(_amount1 * _amount2 != 0, "amounts should not be zero");

        require(hasRole(LIQUIDITY_PROVIDER_ROLE, _from), "Sender has not permitted to remove liquidity");

        // get pair
        address pair = IUniswapV2Factory(UNISWAP_V2_FACTORY).getPair(_token1, _token2); 
        require(IUniswapV2Pair(pair).token1() == _token1 && IUniswapV2Pair(pair).token1() == _token2, 
            "The pair tokens' address didn't match with addresses in input");

        (uint _reserve1, uint _reserve2, ) = IUniswapV2Pair(pair).getReserves(); // timestamp exist in 3nd arg
        uint liquidity_balance = IUniswapV2Pair(pair).balanceOf(_from);
        require(liquidity_balance != 0, "Liquidity has not been added yet");

        emit LogAllowance(IUniswapV2Pair(pair).allowance(_from, UNISWAP_V2_ROUTER01));

        uint LpAmountForBurn = _calculateAmountOfLpTokenForBurn(_amount1, _amount2, _reserve1, _reserve2, liquidity_balance);
        require(liquidity_balance >= LpAmountForBurn, "Something went wrong in removeLiquidity");
        // require(IUniswapV2Pair(pair).allowance(msg.sender, pair) >= LpAmountForBurn, "Allowance amount is less than lp_amount for burn");        
        

        // senario No.1 : not whole Lp tokens:
        if(_reserve1.add(_reserve2) != _amount1.add(_amount2)) {
            emit logUint("Lp token amount clculated by internal function", LpAmountForBurn);
            emit LogBalance(_reserve1, _reserve2, liquidity_balance);

            /** @dev The bug is due to this approval section that throw (ds-math-sub-underflow) error
                * @dev The approving section will accomplish off-chain
            */ 
            (amount_back1, amount_back2) = IUniswapV2Router01(UNISWAP_V2_ROUTER01).removeLiquidity(
                    _token1, _token2, LpAmountForBurn, 1, 1, _from, block.timestamp + 3600); 
            
            uint new_liq_balance = IUniswapV2Pair(pair).balanceOf(_from);
            if(this._check_liq_balance_for_revoke_role(pair, new_liq_balance)) {
                this.revokeRole(ADMIN, _from);
            }
        }   


        // Senario No.2 : Whole Lp token will burn from liquidity pool:
        // require(IUniswapV2Pair(pair).allowance(msg.sender, pair) == liquidity_balance, "Allowance is not equal to liquidity balance for burning whole liquidity tokens");
        (amount_back1, amount_back2) = IUniswapV2Router01(UNISWAP_V2_ROUTER01).removeLiquidity(
            _token1, _token2, liquidity_balance, 1, 1, _from, block.timestamp + 3600);
        
        if(this._check_liq_balance_for_revoke_role(pair, new_liq_balance)) {
            this.revokeRole(ADMIN, _from);
        }

        require(amount_back1 * amount_back2 != 0, "Some error occured in amount back"); // non of those amount back should be 0 (require is not necessary in here)
    }

    function removeLiquidity(address _from, address _token1, address _token2, uint _amount1, uint _amount2) 
    public {
        require(_from != address(0), "invalid caller address");
        _removingLiquidity(_from, _token1, _token2, _amount1, _amount2);
    }
}
