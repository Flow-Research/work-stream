// SPDX-License-Identifier: MIT
pragma solidity ^0.8.20;

import "forge-std/Test.sol";
import "../src/FlowArtifactRegistry.sol";

contract FlowArtifactRegistryTest is Test {
    FlowArtifactRegistry public registry;
    
    address public admin = address(1);
    address public contributor1 = address(2);
    address public contributor2 = address(3);
    
    bytes32 public artifactId = keccak256("artifact-1");
    bytes32 public contentHash = keccak256("QmTestIPFSHash");

    function setUp() public {
        vm.prank(admin);
        registry = new FlowArtifactRegistry();
    }

    function test_RegisterArtifact() public {
        address[] memory contributors = new address[](2);
        contributors[0] = contributor1;
        contributors[1] = contributor2;
        
        vm.prank(admin);
        registry.registerArtifact(artifactId, contentHash, contributors);
        
        assertTrue(registry.artifactExists(artifactId));
        
        (bytes32 hash, address[] memory contribs, uint256 timestamp) = registry.getArtifact(artifactId);
        assertEq(hash, contentHash);
        assertEq(contribs.length, 2);
        assertEq(contribs[0], contributor1);
        assertEq(contribs[1], contributor2);
        assertGt(timestamp, 0);
    }

    function test_RegisterArtifact_RevertOnDuplicate() public {
        address[] memory contributors = new address[](1);
        contributors[0] = contributor1;
        
        vm.prank(admin);
        registry.registerArtifact(artifactId, contentHash, contributors);
        
        vm.prank(admin);
        vm.expectRevert(FlowArtifactRegistry.ArtifactAlreadyExists.selector);
        registry.registerArtifact(artifactId, contentHash, contributors);
    }

    function test_RegisterArtifact_RevertOnNoContributors() public {
        address[] memory contributors = new address[](0);
        
        vm.prank(admin);
        vm.expectRevert(FlowArtifactRegistry.NoContributors.selector);
        registry.registerArtifact(artifactId, contentHash, contributors);
    }

    function test_RegisterArtifact_RevertOnUnauthorized() public {
        address[] memory contributors = new address[](1);
        contributors[0] = contributor1;
        
        vm.prank(contributor1);
        vm.expectRevert();
        registry.registerArtifact(artifactId, contentHash, contributors);
    }

    function test_GetArtifact_RevertOnNotFound() public {
        vm.expectRevert(FlowArtifactRegistry.ArtifactNotFound.selector);
        registry.getArtifact(artifactId);
    }

    function test_VerifyArtifact() public {
        address[] memory contributors = new address[](1);
        contributors[0] = contributor1;
        
        vm.prank(admin);
        registry.registerArtifact(artifactId, contentHash, contributors);
        
        assertTrue(registry.verifyArtifact(artifactId, contentHash));
        assertFalse(registry.verifyArtifact(artifactId, keccak256("wrong")));
    }

    function test_GetArtifactCount() public {
        assertEq(registry.getArtifactCount(), 0);
        
        address[] memory contributors = new address[](1);
        contributors[0] = contributor1;
        
        vm.prank(admin);
        registry.registerArtifact(artifactId, contentHash, contributors);
        
        assertEq(registry.getArtifactCount(), 1);
        
        bytes32 artifactId2 = keccak256("artifact-2");
        vm.prank(admin);
        registry.registerArtifact(artifactId2, contentHash, contributors);
        
        assertEq(registry.getArtifactCount(), 2);
    }

    function test_GetArtifactIdByIndex() public {
        address[] memory contributors = new address[](1);
        contributors[0] = contributor1;
        
        vm.prank(admin);
        registry.registerArtifact(artifactId, contentHash, contributors);
        
        assertEq(registry.getArtifactIdByIndex(0), artifactId);
    }
}
