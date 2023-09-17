// // SPDX-License-Identifier: MIT
// pragma solidity ^0.8.11;

// import { UQ112x112  } from "./InternalMath.sol";
// import "@openzeppelin/contracts/utils/math/SafeMath.sol";
// import "@uniswap/contracts/interfaces/IUniswapV2Pair.sol";
// // import "@uniswap-periphery/contracts/libraries/UniswapV2OracleLibrary.sol";
// // import '@uniswap/lib/contracts/libraries/FixedPoint.sol';
// // import "@uniswap-periphery/contracts/libraries/UniswapV2Library.sol";

// contract AviatoSwapTwap {   
//     using UQ112x112 for uint;    
//     using SafeMath for uint;

//     address private immutable pair_address;
//     address private immutable token1;
//     address private immutable token2;

//     uint public initCumulativePrice1;
//     uint public initCumulativePrice2;
//     uint32 public initTimeStamp;

//     uint public Price1Average;
//     uint public price2Average;

//     constructor(
//         IUniswapV2Pair _pair, address _token1, address _token2
//     ) {
//         pair_address = address(_pair);
//         token1 = _token1;
//         token2 = _token2;

//         initCumulativePrice1 = IUniswapV2Pair(_pair).price0CumulativeLast();
//         initCumulativePrice2 = IUniswapV2Pair(_pair).price1CumulativeLast();
//         (, , initTimeStamp) = IUniswapV2Pair(_pair).getReserves();
//     }


//     function updateCumulativeState() 
//     external 
//     returns(bool updated) {
//     }
// }    