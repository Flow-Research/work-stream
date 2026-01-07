"""IPFS service using Pinata."""
import hashlib
import json
from typing import Any, Optional

import httpx

from app.core.config import settings


class IPFSService:
    """Service for storing and retrieving files from IPFS via Pinata."""
    
    def __init__(self):
        self.api_key = settings.pinata_api_key
        self.secret = settings.pinata_secret
        self.base_url = "https://api.pinata.cloud"
        self.gateway_url = "https://gateway.pinata.cloud/ipfs"
    
    def _get_headers(self) -> dict[str, str]:
        """Get authentication headers for Pinata API."""
        return {
            "pinata_api_key": self.api_key or "",
            "pinata_secret_api_key": self.secret or "",
        }
    
    async def pin_json(
        self,
        data: dict[str, Any],
        name: Optional[str] = None,
    ) -> str:
        """
        Pin JSON data to IPFS.
        
        Args:
            data: The JSON data to pin
            name: Optional name for the pin
            
        Returns:
            The IPFS hash (CID)
        """
        if not self.api_key or not self.secret:
            # Return mock hash for development
            content = json.dumps(data, sort_keys=True).encode()
            return f"Qm{hashlib.sha256(content).hexdigest()[:44]}"
        
        async with httpx.AsyncClient() as client:
            response = await client.post(
                f"{self.base_url}/pinning/pinJSONToIPFS",
                headers=self._get_headers(),
                json={
                    "pinataContent": data,
                    "pinataMetadata": {
                        "name": name or "flow-artifact",
                    },
                },
                timeout=60.0,
            )
            response.raise_for_status()
            result = response.json()
            return result["IpfsHash"]
    
    async def pin_file(
        self,
        file_content: bytes,
        filename: str,
    ) -> str:
        """
        Pin a file to IPFS.
        
        Args:
            file_content: The file content
            filename: The filename
            
        Returns:
            The IPFS hash (CID)
        """
        if not self.api_key or not self.secret:
            # Return mock hash for development
            return f"Qm{hashlib.sha256(file_content).hexdigest()[:44]}"
        
        async with httpx.AsyncClient() as client:
            response = await client.post(
                f"{self.base_url}/pinning/pinFileToIPFS",
                headers=self._get_headers(),
                files={"file": (filename, file_content)},
                timeout=120.0,
            )
            response.raise_for_status()
            result = response.json()
            return result["IpfsHash"]
    
    async def get_json(self, ipfs_hash: str) -> Optional[dict[str, Any]]:
        """
        Retrieve JSON data from IPFS.
        
        Args:
            ipfs_hash: The IPFS hash (CID)
            
        Returns:
            The JSON data or None
        """
        try:
            async with httpx.AsyncClient() as client:
                response = await client.get(
                    f"{self.gateway_url}/{ipfs_hash}",
                    timeout=30.0,
                )
                response.raise_for_status()
                return response.json()
        except Exception:
            return None
    
    async def get_file(self, ipfs_hash: str) -> Optional[bytes]:
        """
        Retrieve file content from IPFS.
        
        Args:
            ipfs_hash: The IPFS hash (CID)
            
        Returns:
            The file content or None
        """
        try:
            async with httpx.AsyncClient() as client:
                response = await client.get(
                    f"{self.gateway_url}/{ipfs_hash}",
                    timeout=60.0,
                )
                response.raise_for_status()
                return response.content
        except Exception:
            return None
    
    def get_gateway_url(self, ipfs_hash: str) -> str:
        """
        Get the gateway URL for an IPFS hash.
        
        Args:
            ipfs_hash: The IPFS hash (CID)
            
        Returns:
            The full gateway URL
        """
        return f"{self.gateway_url}/{ipfs_hash}"
