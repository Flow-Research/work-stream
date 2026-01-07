// SPDX-License-Identifier: MIT
pragma solidity ^0.8.20;

import "forge-std/Script.sol";
import "../src/FlowEscrow.sol";
import "../src/FlowArtifactRegistry.sol";
import "../src/MockCNGN.sol";

contract DeployScript is Script {
    function run() external {
        uint256 deployerPrivateKey = vm.envUint("PRIVATE_KEY");
        address feeRecipient = vm.envAddress("FEE_RECIPIENT");
        
        vm.startBroadcast(deployerPrivateKey);
        
        // Deploy mock cNGN (for testnet)
        MockCNGN cngn = new MockCNGN();
        console.log("MockCNGN deployed at:", address(cngn));
        
        // Deploy escrow
        FlowEscrow escrow = new FlowEscrow(address(cngn), feeRecipient);
        console.log("FlowEscrow deployed at:", address(escrow));
        
        // Deploy artifact registry
        FlowArtifactRegistry registry = new FlowArtifactRegistry();
        console.log("FlowArtifactRegistry deployed at:", address(registry));
        
        vm.stopBroadcast();
        
        // Log deployment summary
        console.log("\n=== Deployment Summary ===");
        console.log("Network: Base Sepolia");
        console.log("cNGN Token:", address(cngn));
        console.log("Escrow Contract:", address(escrow));
        console.log("Artifact Registry:", address(registry));
        console.log("Fee Recipient:", feeRecipient);
    }
}

contract DeployTestnet is Script {
    function run() external {
        uint256 deployerPrivateKey = vm.envUint("PRIVATE_KEY");
        
        vm.startBroadcast(deployerPrivateKey);
        
        // Deploy mock cNGN
        MockCNGN cngn = new MockCNGN();
        console.log("MockCNGN deployed at:", address(cngn));
        
        // Use deployer as fee recipient for testnet
        address deployer = vm.addr(deployerPrivateKey);
        
        // Deploy escrow
        FlowEscrow escrow = new FlowEscrow(address(cngn), deployer);
        console.log("FlowEscrow deployed at:", address(escrow));
        
        // Deploy artifact registry
        FlowArtifactRegistry registry = new FlowArtifactRegistry();
        console.log("FlowArtifactRegistry deployed at:", address(registry));
        
        vm.stopBroadcast();
    }
}
