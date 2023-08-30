// SPDX-License-Identifier: MIT
pragma solidity ^0.8.0;

import "./AviatoTokenContract.sol";
import "@openzeppelin/contracts/token/ERC20/ERC20.sol";
import "@openzeppelin/contracts/token/ERC20/IERC20.sol";
import "@openzeppelin/contracts/utils/Address.sol";
import "@openzeppelin/contracts/utils/Counters.sol";
import "@openzeppelin/contracts/access/Ownable.sol";
import "hardhat/console.sol";


contract AviatoSwap is ERC20 ,Ownable {
    using Counters for uint;
    using Address for address;
	
    uint private token_per_eth = 10000;
    uint private airdrop_amount = 100;
    address[] private address_list;
    mapping(address => bool) private minted;
    AviatoTokenContract token_;

    event airdrop(address indexed _receiver_address, uint indexed _amount_received);
    event mint_problem(address indexed _mint_address, uint indexed _mint_amount);


    constructor(string memory _name, string memory _symbol) 
        ERC20(_name, _symbol) {
        _mint(msg.sender, 100 * 10**18);
        token_per_eth = 10000;
        airdrop_amount = 100;
    }

    function set_allowance(uint _amount) public {
        require(balanceOf(msg.sender) >= _amount, "invalid amount");
        _approve(msg.sender, address(this), uint256(_amount));
    }


    function purchaseToken(uint token_amount_) public payable onlyOwner { //receive ether
        uint contract_balance_before_receiving = address(this).balance;
        uint eth_amount_should_send = token_amount_ / 10000;
        uint balance_expected_after_transfering = contract_balance_before_receiving - eth_amount_should_send;

        require(balance_expected_after_transfering == balanceOf(address(this)), "something bad happened about trnasfering");
        require(msg.value == eth_amount_should_send);
        require(balanceOf(address(this)) >= token_amount_, "unsufficient amount from contract token amount");

        bool result_ = transfer(msg.sender, token_amount_);
        require(result_, "some error occured in purchaseToken function");
    }   


    function sellToken(uint token_amount) public payable onlyOwner {
        uint eth_rate_amount = token_amount / 10000;
        uint swap_allowance_before_impl = allowance(msg.sender, address(this));
        uint swap_token_balance_before_impl = balanceOf(address(this));

        require(address(this).balance >= eth_rate_amount, "unsufficient eth contract balance sellToken function impl");
        require(swap_allowance_before_impl >= token_amount);

        bool receinve_token_from_Owner = transferFrom(msg.sender, address(this), token_amount);
        bool dec_allowance_ = decreaseAllowance(address(this), token_amount);

        require(receinve_token_from_Owner && dec_allowance_);
        (bool sent, ) = payable(address(this)).call{value:eth_rate_amount}("");
        
        require(sent && balanceOf(address(this)) > swap_token_balance_before_impl, "somthign web srong");
    }


    function getAviatoContractAddress() external payable returns(address) {
        bytes memory contractBytecode = type(AviatoTokenContract).creationCode;
        address contract_addr;
        assembly {
            contract_addr := create(callvalue(), add(contractBytecode, 0x20), mload(contractBytecode)) 
        }
        require(contract_addr != address(0), "The contract address extraction failed");
        return contract_addr;
    }


    // This is the first function that implemented before using other functions of swap
    function swap_airdrop() public onlyOwner returns(uint new_user_balance_, bytes memory _data) {
        require(!minted[msg.sender], "account has get already airdrop");
	    _mint(msg.sender, airdrop_amount);

        minted[msg.sender] = true;
        address_list.push(msg.sender);

        address aviato_token_address = this.getAviatoContractAddress();
        (bool success, bytes memory data) = aviato_token_address.call{value:100, gas:5000}(
            abi.encodeWithSelector(AviatoTokenContract.add_addr_to_address_list.selector, msg.sender)
        );

        require(success, "Some error occured during call operation in swap_airdrop function");
        console.log(string(data));


	require(minted[msg.sender] && balanceOf(msg.sender) == 100);
	new_user_balance_ = balanceOf(msg.sender);
        _data = data;
    }
}

