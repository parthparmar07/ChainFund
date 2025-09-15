from fastapi import APIRouter, HTTPException, Depends
from app.schemas.user_schemas import UserRegisterRequest, UserResponse, AuthRequest, AuthResponse
from app.models.user import User
from app.services.auth_service import auth_service
from app.services.skill_score_service import skill_score_service
from app.services.nft_service import nft_service
from app.db import get_collection
from app.utils.responses import ok, bad_request, not_found
from app.utils.signature import validate_wallet_address, normalize_wallet_address
from datetime import datetime
from typing import Dict, Any, List, Optional
from pydantic import BaseModel

router = APIRouter()


class SkillActivityRequest(BaseModel):
    campaign_id: str
    milestone_id: str
    milestone_title: str
    score_earned: float
    difficulty: str = "medium"
    on_time: bool = True
    peer_reviews: List[float] = []


class SkillScoreResponse(BaseModel):
    wallet_address: str
    skill_score: float
    skill_level: str
    skill_nft_token_id: Optional[int] = None
    total_milestones_completed: int
    total_campaigns_participated: int
    average_completion_time: Optional[float] = None
    skill_breakdown: Dict[str, float]
    recent_achievements: List[Dict[str, Any]]
    next_level_threshold: float


@router.post("/register", response_model=UserResponse)
async def register_user(request: UserRegisterRequest):
    """Register a new user or return existing user"""
    try:
        # Validate wallet address
        if not validate_wallet_address(request.wallet_address):
            raise HTTPException(status_code=400, detail="Invalid wallet address")

        # Normalize wallet address
        normalized_address = normalize_wallet_address(request.wallet_address)

        collection = await get_collection("users")

        # Check if user already exists
        existing_user = await collection.find_one({"wallet_address": normalized_address})

        if existing_user:
            # Update email if provided and different
            if request.email and existing_user.get("email") != request.email:
                await collection.update_one(
                    {"wallet_address": normalized_address},
                    {"$set": {"email": request.email, "updated_at": datetime.utcnow()}}
                )
                existing_user["email"] = request.email

            return UserResponse(**existing_user)

        # Create new user
        user_data = {
            "wallet_address": normalized_address,
            "email": request.email,
            "created_at": datetime.utcnow(),
            "updated_at": datetime.utcnow()
        }

        result = await collection.insert_one(user_data)
        user_data["id"] = str(result.inserted_id)

        return UserResponse(**user_data)

    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Registration failed: {str(e)}")


@router.post("/auth", response_model=AuthResponse)
async def authenticate_user(request: AuthRequest):
    """Authenticate user with MetaMask signature"""
    try:
        # Validate wallet address
        if not validate_wallet_address(request.wallet_address):
            raise HTTPException(status_code=400, detail="Invalid wallet address")

        # Verify signature
        is_valid = auth_service.verify_signature(
            request.wallet_address,
            request.signature,
            request.message
        )

        if not is_valid:
            raise HTTPException(status_code=401, detail="Invalid signature")

        # Get or create user
        collection = await get_collection("users")
        normalized_address = normalize_wallet_address(request.wallet_address)

        user = await collection.find_one({"wallet_address": normalized_address})

        if not user:
            # Create user if doesn't exist
            user_data = {
                "wallet_address": normalized_address,
                "created_at": datetime.utcnow(),
                "updated_at": datetime.utcnow()
            }
            result = await collection.insert_one(user_data)
            user = user_data
            user["id"] = str(result.inserted_id)

        # Create access token
        access_token = auth_service.create_access_token({"sub": normalized_address})

        return AuthResponse(
            access_token=access_token,
            token_type="bearer",
            user=UserResponse(**user)
        )

    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Authentication failed: {str(e)}")


@router.get("/me", response_model=UserResponse)
async def get_current_user(wallet_address: str):
    """Get current user information"""
    try:
        # Validate wallet address
        if not validate_wallet_address(wallet_address):
            raise HTTPException(status_code=400, detail="Invalid wallet address")

        collection = await get_collection("users")
        normalized_address = normalize_wallet_address(wallet_address)

        user = await collection.find_one({"wallet_address": normalized_address})

        if not user:
            raise HTTPException(status_code=404, detail="User not found")

        return UserResponse(**user)

    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to get user: {str(e)}")


@router.get("/skill-score/{wallet_address}", response_model=SkillScoreResponse)
async def get_user_skill_score(wallet_address: str):
    """Get comprehensive skill score data for a user"""
    try:
        # Validate wallet address
        if not validate_wallet_address(wallet_address):
            raise HTTPException(status_code=400, detail="Invalid wallet address")

        normalized_address = normalize_wallet_address(wallet_address)

        skill_data = await skill_score_service.get_skill_score_data(normalized_address)

        if not skill_data:
            raise HTTPException(status_code=404, detail="User not found")

        return SkillScoreResponse(**skill_data)

    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to get skill score: {str(e)}")


@router.post("/skill-activity/{wallet_address}")
async def add_skill_activity(wallet_address: str, activity: SkillActivityRequest):
    """Add a skill-earning activity for a user"""
    try:
        # Validate wallet address
        if not validate_wallet_address(wallet_address):
            raise HTTPException(status_code=400, detail="Invalid wallet address")

        normalized_address = normalize_wallet_address(wallet_address)

        activity_data = {
            "campaign_id": activity.campaign_id,
            "milestone_id": activity.milestone_id,
            "milestone_title": activity.milestone_title,
            "score_earned": activity.score_earned,
            "difficulty": activity.difficulty,
            "on_time": activity.on_time,
            "peer_reviews": activity.peer_reviews
        }

        updated_user = await skill_score_service.add_skill_activity(normalized_address, activity_data)

        if not updated_user:
            raise HTTPException(status_code=404, detail="User not found")

        return ok({
            "message": "Skill activity added successfully",
            "new_skill_score": updated_user.skill_score,
            "new_skill_level": updated_user.skill_level
        })

    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to add skill activity: {str(e)}")


@router.post("/mint-skill-nft/{wallet_address}")
async def mint_skill_nft(wallet_address: str):
    """Mint or update skill NFT for a user"""
    try:
        # Validate wallet address
        if not validate_wallet_address(wallet_address):
            raise HTTPException(status_code=400, detail="Invalid wallet address")

        normalized_address = normalize_wallet_address(wallet_address)

        # Get current skill score
        skill_data = await skill_score_service.get_skill_score_data(normalized_address)

        if not skill_data:
            raise HTTPException(status_code=404, detail="User not found")

        # Mint or update skill NFT
        nft_result = await nft_service.update_skill_nft(normalized_address, skill_data["skill_score"])

        if not nft_result:
            raise HTTPException(status_code=500, detail="Failed to mint/update skill NFT")

        # Update user's skill NFT token ID
        collection = await get_collection("users")
        await collection.update_one(
            {"wallet_address": normalized_address},
            {"$set": {"skill_nft_token_id": nft_result["token_id"]}}
        )

        return ok({
            "message": "Skill NFT minted/updated successfully",
            "nft_data": nft_result
        })

    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to mint skill NFT: {str(e)}")


@router.get("/skill-nft/{wallet_address}")
async def get_skill_nft(wallet_address: str):
    """Get skill NFT information for a user"""
    try:
        # Validate wallet address
        if not validate_wallet_address(wallet_address):
            raise HTTPException(status_code=400, detail="Invalid wallet address")

        normalized_address = normalize_wallet_address(wallet_address)

        skill_nft = await nft_service.get_skill_nft(normalized_address)

        if not skill_nft:
            return ok({"message": "No skill NFT found for user"})

        return ok({"skill_nft": skill_nft})

    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to get skill NFT: {str(e)}")


@router.put("/skill-score/update/{wallet_address}")
async def update_user_skill_score(wallet_address: str):
    """Manually trigger skill score recalculation for a user"""
    try:
        # Validate wallet address
        if not validate_wallet_address(wallet_address):
            raise HTTPException(status_code=400, detail="Invalid wallet address")

        normalized_address = normalize_wallet_address(wallet_address)

        updated_user = await skill_score_service.update_user_skill_score(normalized_address)

        if not updated_user:
            raise HTTPException(status_code=404, detail="User not found")

        return ok({
            "message": "Skill score updated successfully",
            "skill_score": updated_user.skill_score,
            "skill_level": updated_user.skill_level
        })

    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to update skill score: {str(e)}")