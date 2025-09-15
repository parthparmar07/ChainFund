from datetime import datetime
from typing import Optional, List
from pydantic import BaseModel, Field
from beanie import Document


class SkillHistory(BaseModel):
    campaign_id: str
    milestone_id: str
    milestone_title: str
    score_earned: float
    completed_at: datetime
    difficulty_rating: str  # "easy", "medium", "hard"
    on_time_completion: bool
    peer_reviews: List[float] = []  # List of review scores 1-5


class User(Document):
    wallet_address: str = Field(..., description="User's wallet address")
    email: Optional[str] = Field(None, description="User's email address")
    username: Optional[str] = Field(None, description="User's display name")
    skill_score: float = Field(default=0.0, description="Calculated skill score")
    skill_level: str = Field(default="Beginner", description="Skill level based on score")
    skill_nft_token_id: Optional[int] = Field(None, description="Token ID of skill NFT")
    skill_history: List[SkillHistory] = Field(default_factory=list, description="History of skill-earning activities")
    total_milestones_completed: int = Field(default=0, description="Total milestones completed")
    total_campaigns_participated: int = Field(default=0, description="Total campaigns participated in")
    average_completion_time: Optional[float] = Field(None, description="Average completion time in days")
    created_at: datetime = Field(default_factory=datetime.utcnow)
    updated_at: datetime = Field(default_factory=datetime.utcnow)

    class Settings:
        name = "users"
        indexes = [
            "wallet_address",  # Unique index for wallet address
            "skill_score",     # Index for skill score queries
            "skill_level",     # Index for skill level filtering
        ]

    class Config:
        json_encoders = {
            datetime: lambda v: v.isoformat()
        }


class UserCreate(BaseModel):
    wallet_address: str
    email: Optional[str] = None
    username: Optional[str] = None


class UserResponse(BaseModel):
    id: str
    wallet_address: str
    email: Optional[str] = None
    username: Optional[str] = None
    skill_score: float
    skill_level: str
    skill_nft_token_id: Optional[int] = None
    total_milestones_completed: int
    total_campaigns_participated: int
    created_at: str
    updated_at: str


class SkillScoreResponse(BaseModel):
    wallet_address: str
    skill_score: float
    skill_level: str
    skill_nft_token_id: Optional[int] = None
    total_milestones_completed: int
    total_campaigns_participated: int
    average_completion_time: Optional[float] = None
    skill_breakdown: dict  # Breakdown by categories
    recent_achievements: List[dict]  # Recent skill-earning activities
    next_level_threshold: float  # Score needed for next level