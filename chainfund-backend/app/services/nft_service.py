from typing import Optional, Dict, Any
from datetime import datetime
from app.models.nft import NFT, NFTCreate
from app.services.web3_service import web3_service
from app.db import get_collection


class NFTService:
    def __init__(self):
        self.tier_thresholds = {
            "Bronze": 0.1,      # 0.1 BNB
            "Silver": 1.0,      # 1 BNB
            "Gold": 5.0,        # 5 BNB
            "Platinum": 10.0,   # 10 BNB
            "Diamond": 50.0     # 50 BNB
        }

        self.skill_nft_levels = {
            "Novice": {"threshold": 0, "color": "#8B5CF6", "description": "Just getting started"},
            "Beginner": {"threshold": 50, "color": "#3B82F6", "description": "Building foundations"},
            "Intermediate": {"threshold": 200, "color": "#10B981", "description": "Gaining expertise"},
            "Advanced": {"threshold": 500, "color": "#F59E0B", "description": "Highly skilled"},
            "Expert": {"threshold": 1000, "color": "#EF4444", "description": "Master contributor"}
        }

    def determine_tier(self, amount: float) -> str:
        """Determine NFT tier based on backing amount"""
        for tier, threshold in reversed(self.tier_thresholds.items()):
            if amount >= threshold:
                return tier
        return "Supporter"  # Default tier for small amounts

    def determine_skill_nft_level(self, skill_score: float) -> str:
        """Determine skill NFT level based on skill score"""
        for level, info in reversed(self.skill_nft_levels.items()):
            if skill_score >= info["threshold"]:
                return level
        return "Novice"

    async def mint_nft_for_backer(self, campaign_id: str, backer_wallet: str, amount: float) -> Optional[Dict[str, Any]]:
        """Mint NFT for a backer and save to database"""
        try:
            # Determine tier
            tier = self.determine_tier(amount)

            # Mint NFT on blockchain
            token_id = await web3_service.mint_nft(backer_wallet, tier, amount)

            # Create NFT record in database
            nft_data = NFTCreate(
                campaign_id=campaign_id,
                owner_wallet=backer_wallet,
                tier=tier,
                amount_backed=amount
            )

            nft = NFT(**nft_data.dict())
            nft.token_id = token_id

            collection = await get_collection("nfts")
            result = await collection.insert_one(nft.dict())

            return {
                "nft_id": str(result.inserted_id),
                "token_id": token_id,
                "tier": tier,
                "amount_backed": amount
            }

        except Exception as e:
            print(f"Error minting NFT: {str(e)}")
            return None

    async def mint_skill_nft(self, wallet_address: str, skill_score: float) -> Optional[Dict[str, Any]]:
        """Mint a soulbound skill NFT for a user based on their skill score"""
        try:
            # Determine skill level
            skill_level = self.determine_skill_nft_level(skill_score)

            # Get level info
            level_info = self.skill_nft_levels[skill_level]

            # Mint skill NFT on blockchain (soulbound - non-transferable)
            token_id = await web3_service.mint_skill_nft(wallet_address, skill_level, skill_score)

            # Create skill NFT record in database
            skill_nft_data = {
                "owner_wallet": wallet_address,
                "tier": skill_level,
                "skill_score": skill_score,
                "is_skill_nft": True,
                "soulbound": True,
                "color": level_info["color"],
                "description": level_info["description"]
            }

            collection = await get_collection("nfts")
            result = await collection.insert_one(skill_nft_data)

            return {
                "nft_id": str(result.inserted_id),
                "token_id": token_id,
                "skill_level": skill_level,
                "skill_score": skill_score,
                "color": level_info["color"],
                "description": level_info["description"]
            }

        except Exception as e:
            print(f"Error minting skill NFT: {str(e)}")
            return None

    async def update_skill_nft(self, wallet_address: str, new_skill_score: float) -> Optional[Dict[str, Any]]:
        """Update existing skill NFT with new skill score"""
        try:
            collection = await get_collection("nfts")

            # Find existing skill NFT
            existing_nft = await collection.find_one({
                "owner_wallet": wallet_address,
                "is_skill_nft": True
            })

            if not existing_nft:
                # No existing skill NFT, mint a new one
                return await self.mint_skill_nft(wallet_address, new_skill_score)

            # Determine new skill level
            new_skill_level = self.determine_skill_nft_level(new_skill_score)
            level_info = self.skill_nft_levels[new_skill_level]

            # Update NFT on blockchain if level changed
            if existing_nft["tier"] != new_skill_level:
                await web3_service.update_skill_nft(existing_nft["token_id"], new_skill_level, new_skill_score)

            # Update database record
            update_data = {
                "tier": new_skill_level,
                "skill_score": new_skill_score,
                "color": level_info["color"],
                "description": level_info["description"],
                "updated_at": {"$date": {"$numberLong": str(int(datetime.utcnow().timestamp() * 1000))}}
            }

            await collection.update_one(
                {"_id": existing_nft["_id"]},
                {"$set": update_data}
            )

            return {
                "nft_id": str(existing_nft["_id"]),
                "token_id": existing_nft["token_id"],
                "skill_level": new_skill_level,
                "skill_score": new_skill_score,
                "color": level_info["color"],
                "description": level_info["description"],
                "updated": True
            }

        except Exception as e:
            print(f"Error updating skill NFT: {str(e)}")
            return None

    async def get_skill_nft(self, wallet_address: str) -> Optional[Dict[str, Any]]:
        """Get skill NFT for a user"""
        try:
            collection = await get_collection("nfts")
            skill_nft = await collection.find_one({
                "owner_wallet": wallet_address,
                "is_skill_nft": True
            })

            return skill_nft

        except Exception as e:
            print(f"Error getting skill NFT: {str(e)}")
            return None

    async def get_nfts_by_wallet(self, wallet_address: str) -> list:
        """Get all NFTs owned by a wallet"""
        try:
            collection = await get_collection("nfts")
            nfts = await collection.find({"owner_wallet": wallet_address}).to_list(length=None)

            return nfts

        except Exception as e:
            print(f"Error getting NFTs for wallet: {str(e)}")
            return []

    async def get_nfts_by_campaign(self, campaign_id: str) -> list:
        """Get all NFTs for a specific campaign"""
        try:
            collection = await get_collection("nfts")
            nfts = await collection.find({"campaign_id": campaign_id}).to_list(length=None)

            return nfts

        except Exception as e:
            print(f"Error getting NFTs for campaign: {str(e)}")
            return []

    async def get_nft_stats(self, campaign_id: str) -> Dict[str, Any]:
        """Get NFT statistics for a campaign"""
        try:
            collection = await get_collection("nfts")

            # Get total NFTs minted
            total_nfts = await collection.count_documents({"campaign_id": campaign_id})

            # Get tier distribution
            pipeline = [
                {"$match": {"campaign_id": campaign_id}},
                {"$group": {"_id": "$tier", "count": {"$sum": 1}}}
            ]

            tier_stats = await collection.aggregate(pipeline).to_list(length=None)

            # Get total backed amount
            total_backed_pipeline = [
                {"$match": {"campaign_id": campaign_id}},
                {"$group": {"_id": None, "total": {"$sum": "$amount_backed"}}}
            ]

            total_result = await collection.aggregate(total_backed_pipeline).to_list(length=1)
            total_backed = total_result[0]["total"] if total_result else 0

            return {
                "total_nfts": total_nfts,
                "tier_distribution": {stat["_id"]: stat["count"] for stat in tier_stats},
                "total_backed": total_backed
            }

        except Exception as e:
            print(f"Error getting NFT stats: {str(e)}")
            return {
                "total_nfts": 0,
                "tier_distribution": {},
                "total_backed": 0
            }

    def get_tier_info(self) -> Dict[str, float]:
        """Get information about NFT tiers and their thresholds"""
        return self.tier_thresholds.copy()

    def get_skill_nft_levels(self) -> Dict[str, Dict[str, Any]]:
        """Get information about skill NFT levels and their thresholds"""
        return self.skill_nft_levels.copy()


# Global instance
nft_service = NFTService()