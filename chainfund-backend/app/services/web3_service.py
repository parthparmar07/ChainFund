from web3 import Web3
from web3.middleware import ExtraDataToPOAMiddleware
import json
import os
from typing import Optional, Dict, Any
from app.config import settings


class Web3Service:
    def __init__(self):
        self.w3 = Web3(Web3.HTTPProvider(settings.bnb_rpc_url))
        self.w3.middleware_onion.inject(ExtraDataToPOAMiddleware, layer=0)

        # Only try to connect and create account if we have a valid private key
        self.connected = False
        self.account = None

        try:
            if self.w3.is_connected():
                self.connected = True
                # Only create account if we have a valid private key
                if settings.private_key and settings.private_key != "your_private_key_here":
                    self.account = self.w3.eth.account.from_key(settings.private_key)
                else:
                    print("Warning: No valid private key provided - blockchain features disabled")
            else:
                print("Warning: Could not connect to blockchain - features disabled")
        except Exception as e:
            print(f"Warning: Web3 initialization failed: {e} - blockchain features disabled")

        self.contracts = {}

        # Load contract ABIs (only if connected)
        if self.connected:
            self._load_contract_abis()

    def _load_contract_abis(self):
        """Load contract ABIs from files"""
        try:
            # These would be the compiled contract ABIs
            # For now, we'll use placeholder structures
            self.campaign_abi = self._get_campaign_abi()
            self.nft_abi = self._get_nft_abi()
            self.factory_abi = self._get_factory_abi()
        except Exception as e:
            print(f"Error loading contract ABIs: {e}")

    def _get_campaign_abi(self) -> list:
        """Placeholder for Campaign contract ABI"""
        return [
            {
                "inputs": [
                    {"name": "backer", "type": "address"},
                    {"name": "amount", "type": "uint256"}
                ],
                "name": "fund",
                "outputs": [],
                "stateMutability": "payable",
                "type": "function"
            },
            {
                "inputs": [{"name": "milestoneIndex", "type": "uint256"}],
                "name": "releaseMilestone",
                "outputs": [],
                "stateMutability": "nonpayable",
                "type": "function"
            }
        ]

    def _get_nft_abi(self) -> list:
        """Placeholder for NFT contract ABI"""
        return [
            {
                "inputs": [
                    {"name": "to", "type": "address"},
                    {"name": "tier", "type": "string"},
                    {"name": "amount", "type": "uint256"}
                ],
                "name": "mint",
                "outputs": [{"name": "", "type": "uint256"}],
                "stateMutability": "nonpayable",
                "type": "function"
            },
            {
                "inputs": [
                    {"name": "to", "type": "address"},
                    {"name": "skillLevel", "type": "string"},
                    {"name": "skillScore", "type": "uint256"}
                ],
                "name": "mintSkillNFT",
                "outputs": [{"name": "", "type": "uint256"}],
                "stateMutability": "nonpayable",
                "type": "function"
            },
            {
                "inputs": [
                    {"name": "tokenId", "type": "uint256"},
                    {"name": "newSkillLevel", "type": "string"},
                    {"name": "newSkillScore", "type": "uint256"}
                ],
                "name": "updateSkillNFT",
                "outputs": [],
                "stateMutability": "nonpayable",
                "type": "function"
            }
        ]

    def _get_factory_abi(self) -> list:
        """Placeholder for Factory contract ABI"""
        return [
            {
                "inputs": [
                    {"name": "creator", "type": "address"},
                    {"name": "goalAmount", "type": "uint256"},
                    {"name": "milestoneCount", "type": "uint256"}
                ],
                "name": "createCampaign",
                "outputs": [{"name": "", "type": "address"}],
                "stateMutability": "nonpayable",
                "type": "function"
            }
        ]

    async def deploy_campaign_contract(self, creator_wallet: str, goal_amount: float, milestone_count: int) -> str:
        """Deploy a new campaign contract"""
        if not self.connected or not self.account:
            # Return mock response for demo purposes
            return f"0x{creator_wallet[2:42]}"  # Mock contract address

        try:
            factory_contract = self.w3.eth.contract(
                address=settings.campaign_factory_address,
                abi=self.factory_abi
            )

            # Build transaction
            txn = factory_contract.functions.createCampaign(
                creator_wallet,
                self.w3.to_wei(goal_amount, 'ether'),
                milestone_count
            ).build_transaction({
                'from': self.account.address,
                'nonce': self.w3.eth.get_transaction_count(self.account.address),
                'gas': 2000000,
                'gasPrice': self.w3.eth.gas_price
            })

            # Sign and send transaction
            signed_txn = self.w3.eth.account.sign_transaction(txn, settings.private_key)
            tx_hash = self.w3.eth.send_raw_transaction(signed_txn.rawTransaction)

            # Wait for transaction receipt
            receipt = self.w3.eth.wait_for_transaction_receipt(tx_hash)

            # Get deployed contract address from logs
            contract_address = receipt.logs[0].address

            return contract_address

        except Exception as e:
            raise Exception(f"Failed to deploy campaign contract: {str(e)}")

    async def fund_campaign(self, contract_address: str, backer_wallet: str, amount: float) -> str:
        """Fund a campaign contract"""
        try:
            campaign_contract = self.w3.eth.contract(
                address=contract_address,
                abi=self.campaign_abi
            )

            # Build transaction
            txn = campaign_contract.functions.fund(
                backer_wallet,
                self.w3.to_wei(amount, 'ether')
            ).build_transaction({
                'from': self.account.address,
                'value': self.w3.to_wei(amount, 'ether'),
                'nonce': self.w3.eth.get_transaction_count(self.account.address),
                'gas': 200000,
                'gasPrice': self.w3.eth.gas_price
            })

            # Sign and send transaction
            signed_txn = self.w3.eth.account.sign_transaction(txn, settings.private_key)
            tx_hash = self.w3.eth.send_raw_transaction(signed_txn.rawTransaction)

            return self.w3.to_hex(tx_hash)

        except Exception as e:
            raise Exception(f"Failed to fund campaign: {str(e)}")

    async def release_milestone(self, contract_address: str, milestone_index: int) -> str:
        """Release funds for a completed milestone"""
        try:
            campaign_contract = self.w3.eth.contract(
                address=contract_address,
                abi=self.campaign_abi
            )

            # Build transaction
            txn = campaign_contract.functions.releaseMilestone(milestone_index).build_transaction({
                'from': self.account.address,
                'nonce': self.w3.eth.get_transaction_count(self.account.address),
                'gas': 200000,
                'gasPrice': self.w3.eth.gas_price
            })

            # Sign and send transaction
            signed_txn = self.w3.eth.account.sign_transaction(txn, settings.private_key)
            tx_hash = self.w3.eth.send_raw_transaction(signed_txn.rawTransaction)

            return self.w3.to_hex(tx_hash)

        except Exception as e:
            raise Exception(f"Failed to release milestone: {str(e)}")

    async def mint_nft(self, owner_wallet: str, tier: str, amount: float) -> int:
        """Mint an NFT for a backer"""
        try:
            nft_contract = self.w3.eth.contract(
                address=settings.nft_contract_address,
                abi=self.nft_abi
            )

            # Build transaction
            txn = nft_contract.functions.mint(
                owner_wallet,
                tier,
                self.w3.to_wei(amount, 'ether')
            ).build_transaction({
                'from': self.account.address,
                'nonce': self.w3.eth.get_transaction_count(self.account.address),
                'gas': 200000,
                'gasPrice': self.w3.eth.gas_price
            })

            # Sign and send transaction
            signed_txn = self.w3.eth.account.sign_transaction(txn, settings.private_key)
            tx_hash = self.w3.eth.send_raw_transaction(signed_txn.rawTransaction)

            # Wait for receipt to get token ID
            receipt = self.w3.eth.wait_for_transaction_receipt(tx_hash)

            # Extract token ID from logs (this would depend on the actual contract events)
            # For now, return a placeholder
            return 1

        except Exception as e:
            raise Exception(f"Failed to mint NFT: {str(e)}")

    async def mint_skill_nft(self, owner_wallet: str, skill_level: str, skill_score: float) -> int:
        """Mint a soulbound skill NFT for a user"""
        if not self.connected or not self.account:
            # Return mock token ID for demo purposes
            import time
            return int(time.time() * 1000) % 1000000  # Mock token ID

        try:
            nft_contract = self.w3.eth.contract(
                address=settings.nft_contract_address,
                abi=self.nft_abi
            )

            # Build transaction for skill NFT minting
            txn = nft_contract.functions.mintSkillNFT(
                owner_wallet,
                skill_level,
                int(skill_score * 100)  # Convert to integer for blockchain (multiply by 100 for precision)
            ).build_transaction({
                'from': self.account.address,
                'nonce': self.w3.eth.get_transaction_count(self.account.address),
                'gas': 250000,  # Higher gas limit for skill NFT
                'gasPrice': self.w3.eth.gas_price
            })

            # Sign and send transaction
            signed_txn = self.w3.eth.account.sign_transaction(txn, settings.private_key)
            tx_hash = self.w3.eth.send_raw_transaction(signed_txn.rawTransaction)

            # Wait for receipt to get token ID
            receipt = self.w3.eth.wait_for_transaction_receipt(tx_hash)

            # Extract token ID from logs (this would depend on the actual contract events)
            # For now, return a placeholder based on current timestamp for uniqueness
            return int(self.w3.eth.block_number * 1000 + receipt.transactionIndex)

        except Exception as e:
            raise Exception(f"Failed to mint skill NFT: {str(e)}")

    async def update_skill_nft(self, token_id: int, new_skill_level: str, new_skill_score: float) -> str:
        """Update an existing skill NFT with new skill level and score"""
        try:
            nft_contract = self.w3.eth.contract(
                address=settings.nft_contract_address,
                abi=self.nft_abi
            )

            # Build transaction for skill NFT update
            txn = nft_contract.functions.updateSkillNFT(
                token_id,
                new_skill_level,
                int(new_skill_score * 100)  # Convert to integer for blockchain (multiply by 100 for precision)
            ).build_transaction({
                'from': self.account.address,
                'nonce': self.w3.eth.get_transaction_count(self.account.address),
                'gas': 200000,
                'gasPrice': self.w3.eth.gas_price
            })

            # Sign and send transaction
            signed_txn = self.w3.eth.account.sign_transaction(txn, settings.private_key)
            tx_hash = self.w3.eth.send_raw_transaction(signed_txn.rawTransaction)

            return self.w3.to_hex(tx_hash)

        except Exception as e:
            raise Exception(f"Failed to update skill NFT: {str(e)}")

    def get_transaction_status(self, tx_hash: str) -> Dict[str, Any]:
        """Get transaction status"""
        try:
            receipt = self.w3.eth.get_transaction_receipt(tx_hash)
            return {
                "status": receipt.status,
                "block_number": receipt.blockNumber,
                "gas_used": receipt.gasUsed
            }
        except Exception as e:
            return {"error": str(e)}


# Global instance
web3_service = Web3Service()