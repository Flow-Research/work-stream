"""Blockchain service for interacting with smart contracts."""
import json
from typing import Any, Optional

from web3 import Web3
from web3.middleware import geth_poa_middleware

from app.core.config import settings


# ABI definitions (simplified for key functions)
ESCROW_ABI = json.loads('''[
    {
        "inputs": [{"name": "amount", "type": "uint256"}],
        "name": "fundTask",
        "outputs": [{"name": "", "type": "uint256"}],
        "stateMutability": "nonpayable",
        "type": "function"
    },
    {
        "inputs": [
            {"name": "taskId", "type": "uint256"},
            {"name": "subtaskIndex", "type": "uint256"},
            {"name": "worker", "type": "address"},
            {"name": "amount", "type": "uint256"}
        ],
        "name": "approveSubtask",
        "outputs": [],
        "stateMutability": "nonpayable",
        "type": "function"
    },
    {
        "inputs": [{"name": "taskId", "type": "uint256"}],
        "name": "completeTask",
        "outputs": [],
        "stateMutability": "nonpayable",
        "type": "function"
    },
    {
        "inputs": [{"name": "taskId", "type": "uint256"}],
        "name": "raiseDispute",
        "outputs": [],
        "stateMutability": "nonpayable",
        "type": "function"
    },
    {
        "inputs": [{"name": "taskId", "type": "uint256"}],
        "name": "cancelTask",
        "outputs": [],
        "stateMutability": "nonpayable",
        "type": "function"
    },
    {
        "inputs": [{"name": "", "type": "uint256"}],
        "name": "tasks",
        "outputs": [
            {"name": "id", "type": "uint256"},
            {"name": "client", "type": "address"},
            {"name": "totalAmount", "type": "uint256"},
            {"name": "releasedAmount", "type": "uint256"},
            {"name": "status", "type": "uint8"},
            {"name": "createdAt", "type": "uint256"}
        ],
        "stateMutability": "view",
        "type": "function"
    },
    {
        "inputs": [],
        "name": "taskCounter",
        "outputs": [{"name": "", "type": "uint256"}],
        "stateMutability": "view",
        "type": "function"
    }
]''')

REGISTRY_ABI = json.loads('''[
    {
        "inputs": [
            {"name": "artifactId", "type": "bytes32"},
            {"name": "contentHash", "type": "bytes32"},
            {"name": "contributors", "type": "address[]"}
        ],
        "name": "registerArtifact",
        "outputs": [],
        "stateMutability": "nonpayable",
        "type": "function"
    },
    {
        "inputs": [{"name": "artifactId", "type": "bytes32"}],
        "name": "getArtifact",
        "outputs": [
            {"name": "contentHash", "type": "bytes32"},
            {"name": "contributors", "type": "address[]"},
            {"name": "timestamp", "type": "uint256"}
        ],
        "stateMutability": "view",
        "type": "function"
    }
]''')


class BlockchainService:
    """Service for blockchain interactions."""
    
    def __init__(self):
        self.rpc_url = settings.base_rpc_url
        self.escrow_address = settings.escrow_contract_address
        self.registry_address = settings.registry_contract_address
        
        # Initialize Web3
        self.w3 = Web3(Web3.HTTPProvider(self.rpc_url))
        # Add PoA middleware for Base
        self.w3.middleware_onion.inject(geth_poa_middleware, layer=0)
        
        # Initialize contracts if addresses are set
        self.escrow_contract = None
        self.registry_contract = None
        
        if self.escrow_address:
            self.escrow_contract = self.w3.eth.contract(
                address=Web3.to_checksum_address(self.escrow_address),
                abi=ESCROW_ABI,
            )
        
        if self.registry_address:
            self.registry_contract = self.w3.eth.contract(
                address=Web3.to_checksum_address(self.registry_address),
                abi=REGISTRY_ABI,
            )
    
    def is_configured(self) -> bool:
        """Check if blockchain service is properly configured."""
        return bool(self.escrow_address and self.registry_address)
    
    async def get_task(self, task_id: int) -> Optional[dict[str, Any]]:
        """
        Get task data from the escrow contract.
        
        Args:
            task_id: The on-chain task ID
            
        Returns:
            Task data or None
        """
        if not self.escrow_contract:
            return None
        
        try:
            result = self.escrow_contract.functions.tasks(task_id).call()
            return {
                "id": result[0],
                "client": result[1],
                "total_amount": result[2],
                "released_amount": result[3],
                "status": result[4],
                "created_at": result[5],
            }
        except Exception as e:
            print(f"Error getting task: {e}")
            return None
    
    async def get_artifact(self, artifact_id: str) -> Optional[dict[str, Any]]:
        """
        Get artifact data from the registry contract.
        
        Args:
            artifact_id: The artifact ID (hex string)
            
        Returns:
            Artifact data or None
        """
        if not self.registry_contract:
            return None
        
        try:
            artifact_bytes = bytes.fromhex(artifact_id.replace("0x", ""))
            result = self.registry_contract.functions.getArtifact(artifact_bytes).call()
            return {
                "content_hash": result[0].hex(),
                "contributors": result[1],
                "timestamp": result[2],
            }
        except Exception as e:
            print(f"Error getting artifact: {e}")
            return None
    
    def verify_transaction(self, tx_hash: str) -> Optional[dict[str, Any]]:
        """
        Verify a transaction exists and get its details.
        
        Args:
            tx_hash: The transaction hash
            
        Returns:
            Transaction data or None
        """
        try:
            tx = self.w3.eth.get_transaction(tx_hash)
            receipt = self.w3.eth.get_transaction_receipt(tx_hash)
            
            return {
                "hash": tx_hash,
                "from": tx["from"],
                "to": tx["to"],
                "value": tx["value"],
                "status": receipt["status"],
                "block_number": receipt["blockNumber"],
            }
        except Exception as e:
            print(f"Error verifying transaction: {e}")
            return None
    
    def get_task_counter(self) -> int:
        """Get the current task counter from the escrow contract."""
        if not self.escrow_contract:
            return 0

        try:
            return self.escrow_contract.functions.taskCounter().call()
        except Exception:
            return 0

    async def approve_subtask_payment(
        self,
        task_id: int,
        subtask_index: int,
        worker_address: str,
        amount_wei: int,
    ) -> Optional[str]:
        """
        Approve a subtask and release payment to the worker.

        This calls the FlowEscrow.approveSubtask() function which transfers
        the specified amount to the worker.

        Args:
            task_id: The on-chain task ID
            subtask_index: The subtask index within the task
            worker_address: The worker's wallet address
            amount_wei: The payment amount in wei (18 decimals)

        Returns:
            Transaction hash if successful, None otherwise
        """
        if not self.escrow_contract:
            print("Escrow contract not configured")
            return None

        if not settings.admin_private_key:
            print("Admin private key not configured")
            return None

        try:
            # Get the admin account from private key
            account = self.w3.eth.account.from_key(settings.admin_private_key)

            # Build the transaction
            worker_checksum = Web3.to_checksum_address(worker_address)

            tx = self.escrow_contract.functions.approveSubtask(
                task_id,
                subtask_index,
                worker_checksum,
                amount_wei,
            ).build_transaction({
                "from": account.address,
                "nonce": self.w3.eth.get_transaction_count(account.address),
                "gas": 200000,  # Estimated gas limit
                "maxFeePerGas": self.w3.eth.gas_price * 2,
                "maxPriorityFeePerGas": self.w3.to_wei(1, "gwei"),
            })

            # Sign the transaction
            signed_tx = self.w3.eth.account.sign_transaction(tx, settings.admin_private_key)

            # Send the transaction
            tx_hash = self.w3.eth.send_raw_transaction(signed_tx.raw_transaction)

            # Wait for confirmation (with timeout)
            receipt = self.w3.eth.wait_for_transaction_receipt(tx_hash, timeout=60)

            if receipt["status"] == 1:
                return tx_hash.hex()
            else:
                print(f"Transaction failed: {tx_hash.hex()}")
                return None

        except Exception as e:
            print(f"Error approving subtask payment: {e}")
            return None

    async def register_artifact(
        self,
        artifact_id: str,
        content_hash: str,
        contributors: list[str],
    ) -> Optional[str]:
        """
        Register an artifact on the FlowArtifactRegistry.

        Args:
            artifact_id: Unique artifact ID (hex string)
            content_hash: IPFS content hash (hex string)
            contributors: List of contributor wallet addresses

        Returns:
            Transaction hash if successful, None otherwise
        """
        if not self.registry_contract:
            print("Registry contract not configured")
            return None

        if not settings.admin_private_key:
            print("Admin private key not configured")
            return None

        try:
            account = self.w3.eth.account.from_key(settings.admin_private_key)

            # Convert strings to bytes32
            artifact_bytes = bytes.fromhex(artifact_id.replace("0x", "").zfill(64))
            content_bytes = bytes.fromhex(content_hash.replace("0x", "").zfill(64))
            contributor_addresses = [Web3.to_checksum_address(addr) for addr in contributors]

            tx = self.registry_contract.functions.registerArtifact(
                artifact_bytes,
                content_bytes,
                contributor_addresses,
            ).build_transaction({
                "from": account.address,
                "nonce": self.w3.eth.get_transaction_count(account.address),
                "gas": 300000,
                "maxFeePerGas": self.w3.eth.gas_price * 2,
                "maxPriorityFeePerGas": self.w3.to_wei(1, "gwei"),
            })

            signed_tx = self.w3.eth.account.sign_transaction(tx, settings.admin_private_key)
            tx_hash = self.w3.eth.send_raw_transaction(signed_tx.raw_transaction)
            receipt = self.w3.eth.wait_for_transaction_receipt(tx_hash, timeout=60)

            if receipt["status"] == 1:
                return tx_hash.hex()
            else:
                print(f"Transaction failed: {tx_hash.hex()}")
                return None

        except Exception as e:
            print(f"Error registering artifact: {e}")
            return None
