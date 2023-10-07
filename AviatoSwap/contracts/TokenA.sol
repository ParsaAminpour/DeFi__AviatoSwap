// SPDX-License-Identifier: MIT
pragma solidity ^0.8.11;

import "@openzeppelin/contracts/token/ERC20/ERC20.sol";
import "@openzeppelin/contracts/token/ERC20/extensions/ERC20Burnable.sol";

contract TokenA is ERC20, ERC20Burnable {
    constructor() ERC20("TokenA", "TKA") {
        _mint(msg.sender, 100000*(10**18));
    }
}