# Contract Deployment Guide

## Prerequisites

1. **Foundry** installed (`curl -L https://foundry.paradigm.xyz | bash && foundryup`)
2. **Base Sepolia ETH** for gas (get from [Coinbase Faucet](https://www.coinbase.com/faucets/base-sepolia-faucet))
3. **Deployer wallet** private key

## Setup

1. Copy the example env file:
   ```bash
   cp .env.example .env
   ```

2. Edit `.env` with your values:
   ```
   BASE_RPC_URL=https://sepolia.base.org
   PRIVATE_KEY=your_private_key_here
   BASESCAN_API_KEY=optional_for_verification
   ```

3. Install dependencies (if not already done):
   ```bash
   forge install
   ```

## Deploy to Base Sepolia

Run the deployment script:

```bash
source .env
forge script script/Deploy.s.sol:DeployTestnet \
  --rpc-url $BASE_RPC_URL \
  --broadcast \
  -vvvv
```

## Verify Contracts (Optional)

After deployment, verify on BaseScan:

```bash
forge verify-contract <DEPLOYED_ADDRESS> src/MockCNGN.sol:MockCNGN \
  --chain base-sepolia \
  --etherscan-api-key $BASESCAN_API_KEY

forge verify-contract <DEPLOYED_ADDRESS> src/FlowEscrow.sol:FlowEscrow \
  --chain base-sepolia \
  --constructor-args $(cast abi-encode "constructor(address,address)" <CNGN_ADDRESS> <FEE_RECIPIENT>) \
  --etherscan-api-key $BASESCAN_API_KEY

forge verify-contract <DEPLOYED_ADDRESS> src/FlowArtifactRegistry.sol:FlowArtifactRegistry \
  --chain base-sepolia \
  --etherscan-api-key $BASESCAN_API_KEY
```

## Post-Deployment

After deployment, update the backend `.env` with the deployed addresses:

```
ESCROW_CONTRACT_ADDRESS=0x...
REGISTRY_CONTRACT_ADDRESS=0x...
CNGN_CONTRACT_ADDRESS=0x...
```

## Deployed Addresses

| Contract | Address | Network |
|----------|---------|---------|
| MockCNGN | TBD | Base Sepolia |
| FlowEscrow | TBD | Base Sepolia |
| FlowArtifactRegistry | TBD | Base Sepolia |

## Contract ABIs

ABIs are generated in `out/` after compilation:
- `out/MockCNGN.sol/MockCNGN.json`
- `out/FlowEscrow.sol/FlowEscrow.json`
- `out/FlowArtifactRegistry.sol/FlowArtifactRegistry.json`
