// SPDX-License-Identifier: MIT
pragma solidity ^0.8.11;

contract tenderly {
    event Log(string indexed _data, uint indexed _block_number);
    
    string private message;
    
    function setMessage(string memory _msg) external returns(bool) {
    	require(bytes(_msg).length > 0, "invalid message");
    	message = _msg;
    	
    	assert(keccak256(bytes(message)) == keccak256(bytes(_msg)));
    	return true;
    }
    
    function get_message() external view returns(string memory) {
    	return message;
    }
}
