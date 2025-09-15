from fastapi import APIRouter, HTTPException, UploadFile, File
from app.schemas.milestone_schemas import SubmitProofResponse
from app.services.ipfs_service import ipfs_service
from app.db import get_collection
from app.utils.signature import validate_wallet_address, normalize_wallet_address
from datetime import datetime
import aiofiles

router = APIRouter()


@router.post("/{campaign_id}/milestones/{milestone_index}/proof", response_model=SubmitProofResponse)
async def submit_milestone_proof(
    campaign_id: str,
    milestone_index: int,
    file: UploadFile = File(...),
    creator_wallet: str = None
):
    """Submit proof for milestone completion"""
    try:
        # Validate creator wallet address
        if not creator_wallet or not validate_wallet_address(creator_wallet):
            raise HTTPException(status_code=400, detail="Valid creator wallet address required")

        normalized_creator = normalize_wallet_address(creator_wallet)

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

        # Verify creator
        if campaign["creator_wallet"] != normalized_creator:
            raise HTTPException(status_code=403, detail="Only campaign creator can submit proof")

        # Check milestone index
        milestones = campaign.get("milestones", [])
        if milestone_index >= len(milestones):
            raise HTTPException(status_code=400, detail="Invalid milestone index")

        milestone = milestones[milestone_index]

        # Check if milestone is in correct state
        if milestone["status"] != "pending":
            raise HTTPException(status_code=400, detail="Milestone is not in pending state")

        # Read file content
        file_content = await file.read()

        # Upload to IPFS
        ipfs_hash = await ipfs_service.upload_file(file_content, file.filename)

        if not ipfs_hash:
            raise HTTPException(status_code=500, detail="Failed to upload proof to IPFS")

        # Update milestone
        milestone["proof_ipfs"] = ipfs_hash
        milestone["status"] = "submitted"
        milestone["updated_at"] = datetime.utcnow()

        # Update campaign
        await collection.update_one(
            {"_id": campaign["_id"]},
            {
                "$set": {
                    "milestones": milestones,
                    "updated_at": datetime.utcnow()
                }
            }
        )

        return SubmitProofResponse(
            success=True,
            proof_ipfs=ipfs_hash,
            message="Proof submitted successfully"
        )

    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Proof submission failed: {str(e)}")


@router.get("/{campaign_id}/milestones/{milestone_index}")
async def get_milestone_details(campaign_id: str, milestone_index: int):
    """Get details of a specific milestone"""
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

        # Check milestone index
        milestones = campaign.get("milestones", [])
        if milestone_index >= len(milestones):
            raise HTTPException(status_code=400, detail="Invalid milestone index")

        milestone = milestones[milestone_index]

        # Calculate voting progress
        votes = milestone.get("votes", [])
        total_votes = len(votes)
        approve_votes = sum(1 for vote in votes if vote.get("vote", False))

        approval_percentage = (approve_votes / total_votes * 100) if total_votes > 0 else 0

        return {
            "milestone_index": milestone_index,
            "title": milestone["title"],
            "amount": milestone["amount"],
            "status": milestone["status"],
            "proof_ipfs": milestone.get("proof_ipfs"),
            "votes": votes,
            "total_votes": total_votes,
            "approve_votes": approve_votes,
            "approval_percentage": round(approval_percentage, 2),
            "created_at": milestone["created_at"],
            "updated_at": milestone["updated_at"]
        }

    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to get milestone details: {str(e)}")


@router.get("/{campaign_id}/milestones")
async def get_campaign_milestones(campaign_id: str):
    """Get all milestones for a campaign"""
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

        milestones = campaign.get("milestones", [])

        # Add voting progress to each milestone
        for i, milestone in enumerate(milestones):
            votes = milestone.get("votes", [])
            total_votes = len(votes)
            approve_votes = sum(1 for vote in votes if vote.get("vote", False))
            approval_percentage = (approve_votes / total_votes * 100) if total_votes > 0 else 0

            milestone["total_votes"] = total_votes
            milestone["approve_votes"] = approve_votes
            milestone["approval_percentage"] = round(approval_percentage, 2)

        return {
            "campaign_id": campaign_id,
            "milestones": milestones,
            "total_milestones": len(milestones)
        }

    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to get milestones: {str(e)}")