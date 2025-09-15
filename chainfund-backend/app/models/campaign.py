from datetime import datetime
from typing import List, Optional
from pydantic import BaseModel, Field
from beanie import Document


class Milestone(BaseModel):
    index: int = Field(..., description="Milestone index")
    title: str = Field(..., description="Milestone title")
    amount: float = Field(..., description="Amount allocated for this milestone")
    status: str = Field(default="pending", description="Status: pending, submitted, approved, rejected, completed")
    proof_ipfs: Optional[str] = Field(None, description="IPFS hash of proof document")
    votes: List[dict] = Field(default_factory=list, description="List of votes from backers")
    created_at: datetime = Field(default_factory=datetime.utcnow)
    updated_at: datetime = Field(default_factory=datetime.utcnow)


class Backer(BaseModel):
    wallet_address: str = Field(..., description="Backer's wallet address")
    amount_backed: float = Field(..., description="Total amount backed by this user")
    backed_at: datetime = Field(default_factory=datetime.utcnow)


class Campaign(Document):
    creator_wallet: str = Field(..., description="Creator's wallet address")
    title: str = Field(..., description="Campaign title")
    description: str = Field(..., description="Campaign description")
    goal_amount: float = Field(..., description="Funding goal amount")
    contract_address: Optional[str] = Field(None, description="Deployed campaign contract address")
    milestones: List[Milestone] = Field(default_factory=list, description="List of campaign milestones")
    backers: List[Backer] = Field(default_factory=list, description="List of campaign backers")
    total_backed: float = Field(default=0.0, description="Total amount backed so far")
    status: str = Field(default="active", description="Campaign status: active, completed, cancelled")
    created_at: datetime = Field(default_factory=datetime.utcnow)
    updated_at: datetime = Field(default_factory=datetime.utcnow)

    class Settings:
        name = "campaigns"
        indexes = [
            "creator_wallet",
            "contract_address",
            "status",
        ]

    class Config:
        json_encoders = {
            datetime: lambda v: v.isoformat()
        }


class CampaignCreate(BaseModel):
    creator_wallet: str
    title: str
    description: str
    goal_amount: float
    milestones: List[dict]  # Will be converted to Milestone objects


class CampaignResponse(BaseModel):
    id: str
    creator_wallet: str
    title: str
    description: str
    goal_amount: float
    contract_address: Optional[str] = None
    milestones: List[Milestone]
    backers: List[Backer]
    total_backed: float
    status: str
    created_at: datetime
    updated_at: datetime