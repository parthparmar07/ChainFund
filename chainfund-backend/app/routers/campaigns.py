from fastapi import APIRouter, HTTPException
from typing import List, Optional
from app.schemas.campaign_schemas import CampaignCreateRequest, CampaignResponse, CampaignListResponse
from app.models.campaign import Campaign, Milestone
from app.services.web3_service import web3_service
from app.db import get_collection
from app.utils.responses import ok, bad_request, not_found
from app.utils.signature import validate_wallet_address, normalize_wallet_address
from datetime import datetime
import math

router = APIRouter()


@router.post("", response_model=CampaignResponse)
async def create_campaign(request: CampaignCreateRequest):
    """Create a new crowdfunding campaign"""
    try:
        # Validate creator wallet address
        if not validate_wallet_address(request.creator_wallet):
            raise HTTPException(status_code=400, detail="Invalid creator wallet address")

        # Normalize wallet address
        normalized_creator = normalize_wallet_address(request.creator_wallet)

        # Convert milestone data to Milestone objects
        milestones = []
        for i, milestone_data in enumerate(request.milestones):
            milestone = Milestone(
                index=i,
                title=milestone_data["title"],
                amount=milestone_data["amount"],
                status="pending",
                votes=[],
                created_at=datetime.utcnow(),
                updated_at=datetime.utcnow()
            )
            milestones.append(milestone)

        # Deploy campaign contract
        contract_address = await web3_service.deploy_campaign_contract(
            normalized_creator,
            request.goal_amount,
            len(milestones)
        )

        # Create campaign in database
        campaign_data = {
            "creator_wallet": normalized_creator,
            "title": request.title,
            "description": request.description,
            "goal_amount": request.goal_amount,
            "contract_address": contract_address,
            "milestones": [milestone.dict() for milestone in milestones],
            "backers": [],
            "total_backed": 0.0,
            "status": "active",
            "created_at": datetime.utcnow(),
            "updated_at": datetime.utcnow()
        }

        collection = await get_collection("campaigns")
        result = await collection.insert_one(campaign_data)
        campaign_data["id"] = str(result.inserted_id)

        return CampaignResponse(**campaign_data)

    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Campaign creation failed: {str(e)}")


@router.get("", response_model=CampaignListResponse)
async def get_campaigns(
    page: int = 1,
    limit: int = 10,
    status: Optional[str] = None,
    creator: Optional[str] = None
):
    """Get all campaigns with pagination and filtering"""
    try:
        collection = await get_collection("campaigns")

        # Build query
        query = {}
        if status:
            query["status"] = status
        if creator:
            if validate_wallet_address(creator):
                query["creator_wallet"] = normalize_wallet_address(creator)
            else:
                raise HTTPException(status_code=400, detail="Invalid creator wallet address")

        # Get total count
        total = await collection.count_documents(query)

        # Get campaigns with pagination
        skip = (page - 1) * limit
        campaigns_cursor = collection.find(query).skip(skip).limit(limit)
        campaigns = await campaigns_cursor.to_list(length=limit)

        # Convert ObjectId to string
        for campaign in campaigns:
            campaign["id"] = str(campaign["_id"])
            del campaign["_id"]

        return CampaignListResponse(
            campaigns=[CampaignResponse(**campaign) for campaign in campaigns],
            total=total
        )

    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to get campaigns: {str(e)}")


@router.get("/{campaign_id}", response_model=CampaignResponse)
async def get_campaign(campaign_id: str):
    """Get a specific campaign by ID"""
    try:
        collection = await get_collection("campaigns")

        # Try to find by ID first
        try:
            from bson import ObjectId
            campaign = await collection.find_one({"_id": ObjectId(campaign_id)})
        except:
            campaign = None

        # If not found by ID, try by contract address
        if not campaign:
            campaign = await collection.find_one({"contract_address": campaign_id})

        if not campaign:
            raise HTTPException(status_code=404, detail="Campaign not found")

        # Convert ObjectId to string
        campaign["id"] = str(campaign["_id"])
        del campaign["_id"]

        return CampaignResponse(**campaign)

    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to get campaign: {str(e)}")


@router.get("/{campaign_id}/progress")
async def get_campaign_progress(campaign_id: str):
    """Get campaign progress including funding status and milestone completion"""
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

        # Calculate progress
        total_backed = campaign.get("total_backed", 0)
        goal_amount = campaign.get("goal_amount", 0)
        funding_percentage = (total_backed / goal_amount * 100) if goal_amount > 0 else 0

        milestones = campaign.get("milestones", [])
        completed_milestones = sum(1 for m in milestones if m.get("status") == "completed")
        milestone_progress = (completed_milestones / len(milestones) * 100) if milestones else 0

        return {
            "campaign_id": campaign_id,
            "total_backed": total_backed,
            "goal_amount": goal_amount,
            "funding_percentage": round(funding_percentage, 2),
            "backers_count": len(campaign.get("backers", [])),
            "milestones_completed": completed_milestones,
            "total_milestones": len(milestones),
            "milestone_progress": round(milestone_progress, 2),
            "status": campaign.get("status", "active")
        }

    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to get campaign progress: {str(e)}")


@router.get("/categories")
async def get_campaign_categories():
    """Get all available campaign categories with counts"""
    try:
        collection = await get_collection("campaigns")
        
        # Get all campaigns and count by category
        campaigns = await collection.find({}).to_list(length=None)
        
        # Count campaigns by category
        category_counts = {}
        for campaign in campaigns:
            category = campaign.get("category", "Other")
            category_counts[category] = category_counts.get(category, 0) + 1
        
        # Define category descriptions
        category_descriptions = {
            "Technology": "Blockchain, AI, and software projects",
            "Healthcare": "Medical devices, telemedicine, and health tech",
            "Environment": "Sustainable energy, water purification, and eco-projects",
            "Education": "Learning platforms and educational technology",
            "Agriculture": "Farming technology and food production",
            "Gaming": "Blockchain gaming and metaverse projects",
            "Logistics": "Supply chain and transportation optimization",
            "Energy": "Renewable energy and trading platforms"
        }
        
        # Build response
        categories = []
        for category, count in category_counts.items():
            categories.append({
                "name": category,
                "count": count,
                "description": category_descriptions.get(category, f"Projects in {category}")
            })
        
        # Sort by count descending
        categories.sort(key=lambda x: x["count"], reverse=True)
        
        return {"categories": categories}
    
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to get campaign categories: {str(e)}")