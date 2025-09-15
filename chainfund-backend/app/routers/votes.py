from fastapi import APIRouter, HTTPException
from app.schemas.milestone_schemas import VoteOnMilestoneRequest, VoteOnMilestoneResponse
from app.services.web3_service import web3_service
from app.db import get_collection
from app.utils.signature import validate_wallet_address, normalize_wallet_address
from datetime import datetime

router = APIRouter()


@router.post("/{campaign_id}/milestones/{milestone_index}/vote", response_model=VoteOnMilestoneResponse)
async def vote_on_milestone(
    campaign_id: str,
    milestone_index: int,
    request: VoteOnMilestoneRequest
):
    """Vote on a milestone completion"""
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

        # Check if backer has funded this campaign
        backers = campaign.get("backers", [])
        is_backer = any(backer["wallet_address"] == normalized_backer for backer in backers)

        if not is_backer:
            raise HTTPException(status_code=403, detail="Only campaign backers can vote")

        # Check milestone index
        milestones = campaign.get("milestones", [])
        if milestone_index >= len(milestones):
            raise HTTPException(status_code=400, detail="Invalid milestone index")

        milestone = milestones[milestone_index]

        # Check if milestone is in submitted state
        if milestone["status"] != "submitted":
            raise HTTPException(status_code=400, detail="Milestone is not in submitted state")

        # Check if backer has already voted
        votes = milestone.get("votes", [])
        existing_vote = None
        for vote in votes:
            if vote["wallet_address"] == normalized_backer:
                existing_vote = vote
                break

        if existing_vote:
            # Update existing vote
            existing_vote["vote"] = request.vote
            existing_vote["voted_at"] = datetime.utcnow()
        else:
            # Add new vote
            new_vote = {
                "wallet_address": normalized_backer,
                "vote": request.vote,
                "voted_at": datetime.utcnow()
            }
            votes.append(new_vote)

        # Calculate voting results
        total_votes = len(votes)
        approve_votes = sum(1 for vote in votes if vote["vote"])

        # Check if voting threshold is met (simple majority for now)
        approval_threshold = total_votes // 2 + 1
        is_approved = approve_votes >= approval_threshold

        # Update milestone status if approved
        transaction_hash = None
        if is_approved and milestone["status"] == "submitted":
            milestone["status"] = "approved"
            milestone["updated_at"] = datetime.utcnow()

            # Release milestone funds on blockchain
            try:
                contract_address = campaign.get("contract_address")
                if contract_address:
                    transaction_hash = await web3_service.release_milestone(
                        contract_address,
                        milestone_index
                    )
                    milestone["status"] = "completed"
            except Exception as e:
                print(f"Failed to release milestone funds: {str(e)}")
                # Don't fail the vote if blockchain transaction fails

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

        return VoteOnMilestoneResponse(
            success=True,
            vote_recorded=True,
            milestone_status=milestone["status"],
            transaction_hash=transaction_hash,
            message=f"Vote recorded successfully. Current approval: {approve_votes}/{total_votes}"
        )

    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Voting failed: {str(e)}")


@router.get("/{campaign_id}/milestones/{milestone_index}/votes")
async def get_milestone_votes(campaign_id: str, milestone_index: int):
    """Get all votes for a milestone"""
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
        votes = milestone.get("votes", [])

        # Calculate voting statistics
        total_votes = len(votes)
        approve_votes = sum(1 for vote in votes if vote["vote"])
        reject_votes = total_votes - approve_votes

        approval_percentage = (approve_votes / total_votes * 100) if total_votes > 0 else 0

        return {
            "campaign_id": campaign_id,
            "milestone_index": milestone_index,
            "votes": votes,
            "total_votes": total_votes,
            "approve_votes": approve_votes,
            "reject_votes": reject_votes,
            "approval_percentage": round(approval_percentage, 2),
            "milestone_status": milestone["status"]
        }

    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to get votes: {str(e)}")