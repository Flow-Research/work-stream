// SPDX-License-Identifier: MIT
pragma solidity ^0.8.20;

import "@openzeppelin/contracts/token/ERC20/ERC20.sol";
import "@openzeppelin/contracts/access/Ownable.sol";

/**
 * @title MockCNGN
 * @notice Mock cNGN token for testing
 * @dev Allows anyone to mint tokens for testing purposes
 */
contract MockCNGN is ERC20, Ownable {
    uint8 private constant DECIMALS = 2; // cNGN has 2 decimals like Naira

    constructor() ERC20("Mock cNGN", "cNGN") Ownable(msg.sender) {}

    /**
     * @notice Mint tokens to an address (for testing)
     * @param to Recipient address
     * @param amount Amount to mint (in smallest units)
     */
    function mint(address to, uint256 amount) external {
        _mint(to, amount);
    }

    /**
     * @notice Get a faucet of test tokens
     * @dev Mints 10,000 cNGN to the caller
     */
    function faucet() external {
        _mint(msg.sender, 1000000); // 10,000 cNGN (10000 * 10^2)
    }

    /**
     * @notice Returns the number of decimals
     */
    function decimals() public pure override returns (uint8) {
        return DECIMALS;
    }
}
