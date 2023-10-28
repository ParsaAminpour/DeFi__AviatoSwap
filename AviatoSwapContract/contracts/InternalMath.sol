// SPDX-License_identifier: MIT
pragma solidity ^0.8.11;

library UniMath {
    function min(uint x, uint y) internal pure returns (uint z) {
        z = x < y ? x : y;
    }

    // babylonian method (https://en.wikipedia.org/wiki/Methods_of_computing_square_roots#Babylonian_method)
    function sqrt(uint y) internal pure returns (uint z) {
        if (y > 3) {
            z = y;
            uint x = y / 2 + 1;
            while (x < z) {
                z = x;
                x = (y / x + x) / 2;
            }
        } else if (y != 0) {
            z = 1;
        }
    }

    function average(uint[] calldata numbers) public pure returns (uint) {

        uint sum = 0;
        uint count = numbers.length;    
        for (uint i = 0; i < count; i++) {
          sum += numbers[i];
        }   

        uint avg;

        // Use assembly to compute average
        assembly {
          mstore(0x0, sum)
          mstore(0x20, count)
          avg := sdiv(mload(0x0), mload(0x20))
        }   
        return avg;
    }


    /** @dev This function will re-build with inline assembly, ASAP
             still has some vulnerability! */  
    // function _getOptimalAmountForSwapFirstPair(uint _amount, uint _reserve1) internal pure returns(uint actual_amount) {
    //     require(_amount != 0 && _reserve1 != 0, 'invalid inputs');
    //     // We have : (1-f)s^2 + A(2-f)s - aA = 0  -> s=?
    //     uint fee = uint(ufixed128x18(0.003));
    //     unchecked {
    //         uint delta_val = uint((_reserve1*(2-fee))**2) + (4*(1-fee)*(_amount*_reserve1));
    //         uint minusOne;
    //         assembly {
    //             minusOne := 0xfffffffff
    //         }
    //         actual_amount = uint(minusOne*(_reserve1*(2-fee)) + UniMath.sqrt(delta_val)) / 2*(1-fee);
    //     }   
    // }
}