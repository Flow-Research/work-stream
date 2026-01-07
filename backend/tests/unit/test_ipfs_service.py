"""Unit tests for IPFS service."""
import hashlib
from unittest.mock import AsyncMock, patch, MagicMock

import pytest

from app.services.ipfs import IPFSService


@pytest.fixture
def ipfs_service():
    return IPFSService()


@pytest.fixture
def mock_settings():
    with patch("app.services.ipfs.settings") as mock:
        mock.pinata_api_key = "test_api_key"
        mock.pinata_secret = "test_secret"
        yield mock


class TestIPFSServicePinFile:
    @pytest.mark.asyncio
    async def test_pin_file_returns_mock_hash_when_no_credentials(self, ipfs_service):
        with patch("app.services.ipfs.settings") as mock_settings:
            mock_settings.pinata_api_key = None
            mock_settings.pinata_secret = None
            
            service = IPFSService()
            content = b"test content"
            result = await service.pin_file(content, "test.json")
            
            expected_hash = f"Qm{hashlib.sha256(content).hexdigest()[:44]}"
            assert result == expected_hash

    @pytest.mark.asyncio
    async def test_pin_file_calls_pinata_api(self):
        with patch("app.services.ipfs.settings") as mock_settings:
            mock_settings.pinata_api_key = "test_key"
            mock_settings.pinata_secret = "test_secret"
            
            service = IPFSService()
            
            mock_response = MagicMock()
            mock_response.json.return_value = {"IpfsHash": "QmTestHash123"}
            mock_response.raise_for_status = MagicMock()
            
            with patch("httpx.AsyncClient") as mock_client_class:
                mock_client = AsyncMock()
                mock_client.post = AsyncMock(return_value=mock_response)
                mock_client.__aenter__ = AsyncMock(return_value=mock_client)
                mock_client.__aexit__ = AsyncMock(return_value=None)
                mock_client_class.return_value = mock_client
                
                result = await service.pin_file(b"test content", "test.json")
                
                assert result == "QmTestHash123"
                mock_client.post.assert_called_once()
                call_args = mock_client.post.call_args
                assert "pinFileToIPFS" in call_args[0][0]

    @pytest.mark.asyncio
    async def test_pin_file_handles_api_error(self):
        with patch("app.services.ipfs.settings") as mock_settings:
            mock_settings.pinata_api_key = "test_key"
            mock_settings.pinata_secret = "test_secret"
            
            service = IPFSService()
            
            with patch("httpx.AsyncClient") as mock_client_class:
                mock_client = AsyncMock()
                mock_client.post = AsyncMock(side_effect=Exception("API Error"))
                mock_client.__aenter__ = AsyncMock(return_value=mock_client)
                mock_client.__aexit__ = AsyncMock(return_value=None)
                mock_client_class.return_value = mock_client
                
                with pytest.raises(Exception, match="API Error"):
                    await service.pin_file(b"test content", "test.json")


class TestIPFSServicePinJSON:
    @pytest.mark.asyncio
    async def test_pin_json_returns_mock_hash_when_no_credentials(self):
        with patch("app.services.ipfs.settings") as mock_settings:
            mock_settings.pinata_api_key = None
            mock_settings.pinata_secret = None
            
            service = IPFSService()
            data = {"key": "value"}
            result = await service.pin_json(data)
            
            assert result.startswith("Qm")
            assert len(result) > 40

    @pytest.mark.asyncio
    async def test_pin_json_calls_pinata_api(self):
        with patch("app.services.ipfs.settings") as mock_settings:
            mock_settings.pinata_api_key = "test_key"
            mock_settings.pinata_secret = "test_secret"
            
            service = IPFSService()
            
            mock_response = MagicMock()
            mock_response.json.return_value = {"IpfsHash": "QmJsonHash456"}
            mock_response.raise_for_status = MagicMock()
            
            with patch("httpx.AsyncClient") as mock_client_class:
                mock_client = AsyncMock()
                mock_client.post = AsyncMock(return_value=mock_response)
                mock_client.__aenter__ = AsyncMock(return_value=mock_client)
                mock_client.__aexit__ = AsyncMock(return_value=None)
                mock_client_class.return_value = mock_client
                
                result = await service.pin_json({"test": "data"}, name="test-artifact")
                
                assert result == "QmJsonHash456"


class TestIPFSServiceGetGatewayUrl:
    def test_get_gateway_url_returns_correct_format(self, ipfs_service):
        ipfs_hash = "QmTestHash123"
        result = ipfs_service.get_gateway_url(ipfs_hash)
        
        assert result == f"https://gateway.pinata.cloud/ipfs/{ipfs_hash}"


class TestIPFSServiceGetFile:
    @pytest.mark.asyncio
    async def test_get_file_returns_content(self, ipfs_service):
        mock_response = MagicMock()
        mock_response.content = b"file content"
        mock_response.raise_for_status = MagicMock()
        
        with patch("httpx.AsyncClient") as mock_client_class:
            mock_client = AsyncMock()
            mock_client.get = AsyncMock(return_value=mock_response)
            mock_client.__aenter__ = AsyncMock(return_value=mock_client)
            mock_client.__aexit__ = AsyncMock(return_value=None)
            mock_client_class.return_value = mock_client
            
            result = await ipfs_service.get_file("QmTestHash")
            
            assert result == b"file content"

    @pytest.mark.asyncio
    async def test_get_file_returns_none_on_error(self, ipfs_service):
        with patch("httpx.AsyncClient") as mock_client_class:
            mock_client = AsyncMock()
            mock_client.get = AsyncMock(side_effect=Exception("Network error"))
            mock_client.__aenter__ = AsyncMock(return_value=mock_client)
            mock_client.__aexit__ = AsyncMock(return_value=None)
            mock_client_class.return_value = mock_client
            
            result = await ipfs_service.get_file("QmTestHash")
            
            assert result is None


class TestIPFSServiceGetJSON:
    @pytest.mark.asyncio
    async def test_get_json_returns_data(self, ipfs_service):
        mock_response = MagicMock()
        mock_response.json.return_value = {"key": "value"}
        mock_response.raise_for_status = MagicMock()
        
        with patch("httpx.AsyncClient") as mock_client_class:
            mock_client = AsyncMock()
            mock_client.get = AsyncMock(return_value=mock_response)
            mock_client.__aenter__ = AsyncMock(return_value=mock_client)
            mock_client.__aexit__ = AsyncMock(return_value=None)
            mock_client_class.return_value = mock_client
            
            result = await ipfs_service.get_json("QmTestHash")
            
            assert result == {"key": "value"}

    @pytest.mark.asyncio
    async def test_get_json_returns_none_on_error(self, ipfs_service):
        with patch("httpx.AsyncClient") as mock_client_class:
            mock_client = AsyncMock()
            mock_client.get = AsyncMock(side_effect=Exception("Network error"))
            mock_client.__aenter__ = AsyncMock(return_value=mock_client)
            mock_client.__aexit__ = AsyncMock(return_value=None)
            mock_client_class.return_value = mock_client
            
            result = await ipfs_service.get_json("QmTestHash")
            
            assert result is None
