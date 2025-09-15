import requests
import json
from typing import Optional, Dict, Any
from app.config import settings


class IPFSService:
    def __init__(self):
        self.pinata_api_key = settings.pinata_api_key
        self.pinata_secret_key = settings.pinata_secret_key
        self.web3_storage_token = settings.web3_storage_token

    async def upload_file_to_pinata(self, file_data: bytes, filename: str) -> Optional[str]:
        """Upload file to IPFS using Pinata"""
        try:
            url = "https://api.pinata.cloud/pinning/pinFileToIPFS"

            files = {
                'file': (filename, file_data)
            }

            headers = {
                'pinata_api_key': self.pinata_api_key,
                'pinata_secret_api_key': self.pinata_secret_key
            }

            response = requests.post(url, files=files, headers=headers)

            if response.status_code == 200:
                result = response.json()
                return result['IpfsHash']
            else:
                print(f"Pinata upload failed: {response.text}")
                return None

        except Exception as e:
            print(f"Error uploading to Pinata: {str(e)}")
            return None

    async def upload_file_to_web3_storage(self, file_data: bytes, filename: str) -> Optional[str]:
        """Upload file to IPFS using web3.storage"""
        try:
            url = "https://api.web3.storage/upload"

            headers = {
                'Authorization': f'Bearer {self.web3_storage_token}',
                'Content-Type': 'application/octet-stream'
            }

            response = requests.post(url, data=file_data, headers=headers)

            if response.status_code == 200:
                result = response.json()
                return result['cid']
            else:
                print(f"web3.storage upload failed: {response.text}")
                return None

        except Exception as e:
            print(f"Error uploading to web3.storage: {str(e)}")
            return None

    async def upload_file(self, file_data: bytes, filename: str) -> Optional[str]:
        """Upload file to IPFS using available service"""
        # Try Pinata first if credentials are available
        if self.pinata_api_key and self.pinata_secret_key:
            ipfs_hash = await self.upload_file_to_pinata(file_data, filename)
            if ipfs_hash:
                return ipfs_hash

        # Fallback to web3.storage if available
        if self.web3_storage_token:
            ipfs_hash = await self.upload_file_to_web3_storage(file_data, filename)
            if ipfs_hash:
                return ipfs_hash

        # If no services available, return None
        print("No IPFS service available")
        return None

    async def upload_json_to_pinata(self, json_data: Dict[str, Any]) -> Optional[str]:
        """Upload JSON data to IPFS using Pinata"""
        try:
            url = "https://api.pinata.cloud/pinning/pinJSONToIPFS"

            headers = {
                'Content-Type': 'application/json',
                'pinata_api_key': self.pinata_api_key,
                'pinata_secret_api_key': self.pinata_secret_key
            }

            response = requests.post(url, json=json_data, headers=headers)

            if response.status_code == 200:
                result = response.json()
                return result['IpfsHash']
            else:
                print(f"Pinata JSON upload failed: {response.text}")
                return None

        except Exception as e:
            print(f"Error uploading JSON to Pinata: {str(e)}")
            return None

    async def upload_json_to_web3_storage(self, json_data: Dict[str, Any]) -> Optional[str]:
        """Upload JSON data to IPFS using web3.storage"""
        try:
            url = "https://api.web3.storage/upload"

            headers = {
                'Authorization': f'Bearer {self.web3_storage_token}',
                'Content-Type': 'application/json'
            }

            response = requests.post(url, json=json_data, headers=headers)

            if response.status_code == 200:
                result = response.json()
                return result['cid']
            else:
                print(f"web3.storage JSON upload failed: {response.text}")
                return None

        except Exception as e:
            print(f"Error uploading JSON to web3.storage: {str(e)}")
            return None

    async def upload_json(self, json_data: Dict[str, Any]) -> Optional[str]:
        """Upload JSON data to IPFS using available service"""
        # Try Pinata first if credentials are available
        if self.pinata_api_key and self.pinata_secret_key:
            ipfs_hash = await self.upload_json_to_pinata(json_data)
            if ipfs_hash:
                return ipfs_hash

        # Fallback to web3.storage if available
        if self.web3_storage_token:
            ipfs_hash = await self.upload_json_to_web3_storage(json_data)
            if ipfs_hash:
                return ipfs_hash

        # If no services available, return None
        print("No IPFS service available")
        return None

    def get_ipfs_url(self, ipfs_hash: str) -> str:
        """Get IPFS gateway URL for a hash"""
        return f"https://gateway.pinata.cloud/ipfs/{ipfs_hash}"

    def get_web3_storage_url(self, ipfs_hash: str) -> str:
        """Get web3.storage gateway URL for a hash"""
        return f"https://{ipfs_hash}.ipfs.dweb.link/"


# Global instance
ipfs_service = IPFSService()