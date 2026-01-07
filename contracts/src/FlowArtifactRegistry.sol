// SPDX-License-Identifier: MIT
pragma solidity ^0.8.20;

import "@openzeppelin/contracts/access/Ownable.sol";

/**
 * @title FlowArtifactRegistry
 * @notice On-chain registry for Flow research artifacts
 * @dev Stores artifact metadata hashes for verification and provenance
 */
contract FlowArtifactRegistry is Ownable {
    struct Artifact {
        bytes32 contentHash;  // IPFS content hash
        address[] contributors;
        uint256 timestamp;
        bool exists;
    }

    mapping(bytes32 => Artifact) public artifacts;
    
    // Track all artifact IDs for enumeration
    bytes32[] public artifactIds;

    event ArtifactRegistered(
        bytes32 indexed artifactId,
        bytes32 contentHash,
        address[] contributors,
        uint256 timestamp
    );

    error ArtifactAlreadyExists();
    error NoContributors();
    error ArtifactNotFound();

    constructor() Ownable(msg.sender) {}

    /**
     * @notice Register a new artifact
     * @param artifactId Unique identifier for the artifact
     * @param contentHash IPFS content hash of the artifact
     * @param contributors Array of contributor addresses
     */
    function registerArtifact(
        bytes32 artifactId,
        bytes32 contentHash,
        address[] calldata contributors
    ) external onlyOwner {
        if (artifacts[artifactId].exists) revert ArtifactAlreadyExists();
        if (contributors.length == 0) revert NoContributors();

        artifacts[artifactId] = Artifact({
            contentHash: contentHash,
            contributors: contributors,
            timestamp: block.timestamp,
            exists: true
        });
        
        artifactIds.push(artifactId);

        emit ArtifactRegistered(artifactId, contentHash, contributors, block.timestamp);
    }

    /**
     * @notice Get artifact details
     * @param artifactId The artifact ID
     * @return contentHash The IPFS content hash
     * @return contributors Array of contributor addresses
     * @return timestamp Registration timestamp
     */
    function getArtifact(bytes32 artifactId) external view returns (
        bytes32 contentHash,
        address[] memory contributors,
        uint256 timestamp
    ) {
        Artifact storage a = artifacts[artifactId];
        if (!a.exists) revert ArtifactNotFound();
        return (a.contentHash, a.contributors, a.timestamp);
    }

    /**
     * @notice Check if an artifact exists
     * @param artifactId The artifact ID
     * @return exists True if the artifact is registered
     */
    function artifactExists(bytes32 artifactId) external view returns (bool) {
        return artifacts[artifactId].exists;
    }

    /**
     * @notice Get the total number of registered artifacts
     * @return count The number of artifacts
     */
    function getArtifactCount() external view returns (uint256) {
        return artifactIds.length;
    }

    /**
     * @notice Get artifact ID by index
     * @param index The index in the artifactIds array
     * @return artifactId The artifact ID at that index
     */
    function getArtifactIdByIndex(uint256 index) external view returns (bytes32) {
        return artifactIds[index];
    }

    /**
     * @notice Verify an artifact's content hash
     * @param artifactId The artifact ID
     * @param contentHash The hash to verify
     * @return valid True if the hash matches
     */
    function verifyArtifact(bytes32 artifactId, bytes32 contentHash) external view returns (bool) {
        Artifact storage a = artifacts[artifactId];
        if (!a.exists) return false;
        return a.contentHash == contentHash;
    }
}
