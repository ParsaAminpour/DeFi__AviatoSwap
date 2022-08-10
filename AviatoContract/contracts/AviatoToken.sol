// SPDX-License-Identifier: SEE LICENSE IN LICENSE
pragma solidity ^0.8.0;
import "@openzeppelin/contracts/token/ERC20/ERC20.sol";
import "@openzeppelin/contracts/access/Ownable.sol";
contract AviatoContract is ERC20 , Ownable{
    address[] private address_list;
    mapping(address => bool) private minted;
    constructor() ERC20("Aviato", "AVT") {
    }

    function mint() public onlyOwner returns(uint new_balance_) {
        _mint(msg.sender, 10000); // equal to 1 ether;
        address_list.push(msg.sender);
        minted[msg.sender] = true;

        new_balance_ = balanceOf(msg.sender);
    }

    function add_addr_to_address_list(address _addr) internal onlyOwner returns(bool) {
        require(_addr != address(0), "address is invalid");
        require(!minted[_addr], "this address has already added");
        address_list.push(_addr);
        minted[_addr] = true;
        return minted[_addr];
    }

    function get_addr() public view returns(address) {
        return address(this);
    }
    
}