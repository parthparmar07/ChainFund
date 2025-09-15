from fastapi import APIRouter, HTTPException
from app.schemas.campaign_schemas import FundCampaignRequest, FundCampaignResponse
from app.models.campaign import Backer
from app.services.web3_service import web3_service
from app.services.nft_service import nft_service
from app.db import get_collection
from app.utils.signature import validate_wallet_address, normalize_wallet_address
from datetime import datetime

router = APIRouter()


@router.post("/{campaign_id}/fund", response_model=FundCampaignResponse)
async def fund_campaign(campaign_id: str, request: FundCampaignRequest):
    """Fund a campaign and mint NFT for the backer"""
    try:
        # Validate backer wallet address
        if not validate_wallet_address(request.backer_wallet):
            raise HTTPException(status_code=400, detail="Invalid backer wallet address")

        normalized_backer = normalize_wallet_address(request.backer_wallet)

        collection = await get_collection("campaigns")

        # Get campaign
        try:
            from bson import ObjectId
            campaign = await collection.find_one({"_id": ObjectId(campaign_id)})
        except:
            campaign = None

        if not campaign:
            campaign = await collection.find_one({"contract_address": campaign_id})

        if not campaign:
            raise HTTPException(status_code=404, detail="Campaign not found")

        # Check if campaign is active
        if campaign.get("status") != "active":
            raise HTTPException(status_code=400, detail="Campaign is not active")

        # Check if contract address exists
        contract_address = campaign.get("contract_address")
        if not contract_address:
            raise HTTPException(status_code=400, detail="Campaign contract not deployed")

        # Fund the campaign on blockchain
        tx_hash = await web3_service.fund_campaign(
            contract_address,
            normalized_backer,
            request.amount
        )

        # Update campaign in database
        backers = campaign.get("backers", [])
        total_backed = campaign.get("total_backed", 0.0)

        # Check if backer already exists
        existing_backer = None
        for backer in backers:
            if backer["wallet_address"] == normalized_backer:
                existing_backer = backer
                break

        if existing_backer:
            # Update existing backer
            existing_backer["amount_backed"] += request.amount
            existing_backer["backed_at"] = datetime.utcnow()
            total_backed += request.amount
        else:
            # Add new backer
            new_backer = Backer(
                wallet_address=normalized_backer,
                amount_backed=request.amount,
                backed_at=datetime.utcnow()
            )
            backers.append(new_backer)
            total_backed += request.amount

        # Update campaign
        await collection.update_one(
            {"_id": campaign["_id"]},
            {
                "$set": {
                    "backers": [backer.dict() if hasattr(backer, 'dict') else backer for backer in backers],
                    "total_backed": total_backed,
                    "updated_at": datetime.utcnow()
                }
            }
        )

        # Mint NFT for the backer
        nft_result = await nft_service.mint_nft_for_backer(
            str(campaign["_id"]),
            normalized_backer,
            request.amount
        )

        return FundCampaignResponse(
            success=True,
            transaction_hash=tx_hash,
            nft_token_id=nft_result.get("token_id") if nft_result else None,
            message="Campaign funded successfully"
        )

    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Funding failed: {str(e)}")


@router.get("/{campaign_id}/backers")
async def get_campaign_backers(campaign_id: str):
    """Get all backers of a campaign"""
    try:
        collection = await get_collection("campaigns")

        # Get campaign
        try:
            from bson import ObjectId
            campaign = await collection.find_one({"_id": ObjectId(campaign_id)})
        except:
            campaign = None

        if not campaign:
            campaign = await collection.find_one({"contract_address": campaign_id})

        if not campaign:
            raise HTTPException(status_code=404, detail="Campaign not found")

        backers = campaign.get("backers", [])

        return {
            "campaign_id": campaign_id,
            "backers": backers,
            "total_backers": len(backers)
        }

    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to get backers: {str(e)}")