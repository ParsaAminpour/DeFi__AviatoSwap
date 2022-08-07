// SPDX-License-Identifier: MIT
pragma solidity >= 0.8.0;
import { SafeMath as Safe } from "./SafeMath.sol";
// import "@openzeppelin/contracts/token/ERC721/ERC721.sol";

 contract Ownable {
    using Safe for uint;

    address owner;
    constructor() public {
        owner = msg.sender;
    }

    modifier OnlyOwner() {
        require(msg.sender == owner, "Must be the owner");
        _;
    }
 }

 contract ValueStore {
    string value;
    constructor(string memory _value) public {
        value = _value;
    }

    function getValue() public view returns(string memory) {
        return value;
    }
 }

contract ValueRepresent is Ownable{
    address value_store_address;

    constructor(string memory _value) public {
        ValueStore valuestore = new ValueStore(_value);
        value_store_address = address(valuestore);
        super;
    }

    function getValue() public view OnlyOwner returns(string memory) {
        ValueStore value_store_rep = ValueStore(value_store_address);
        return value_store_rep.getValue();
    }
}

contract RoomValur {
    bool room_status;

    constructor(bool _status) public {
        room_status = _status;
    }

    function get_status_func() public view returns(bool) {
        return room_status;
    }
}


contract BookHotel is Ownable {
    using Safe for uint;

    enum RoomStatus { OCCUPIED, VOCANT }
    address payable public _owner;
    RoomStatus room_status;

    constructor() public {
        room_status = RoomStatus.VOCANT;
        super;
    }

    mapping (string => string)public RoomTypeMap;
    mapping(address => string) public users_reserved;

    modifier sufficient_balance(uint _value) {
        require(msg.value >= _value, "insufficient balance available");
        _;
    }

    event Booked(
        address indexed _room_owner, uint indexed _cost);
    receive() external payable sufficient_balance(2 ether){
        require(room_status == RoomStatus.VOCANT, "The room is busy");
        (bool sent, bytes memory data) = 
            owner.call{value:msg.value, gas:5000}("");
        
        require(sent == true, "something went wrong");
        emit Booked(msg.sender, msg.value);
        // return true;
    }

    fallback() external payable OnlyOwner() {
        require(address(this).balance >= 2 ether);

        (bool sent, bytes memory data) = 
            address(this).call{value:2 ether}("");

        require(sent == true, "something went wrong");
    }

}