from typing import List, Optional
from pydantic import BaseModel


class MilestoneCreate(BaseModel):
    title: str
    amount: float


class MilestoneResponse(BaseModel):
    index: int
    title: str
    amount: float
    status: str
    proof_ipfs: Optional[str] = None
    votes: List[dict]
    created_at: str
    updated_at: str


class BackerResponse(BaseModel):
    wallet_address: str
    amount_backed: float
    backed_at: str


class CampaignCreateRequest(BaseModel):
    creator_wallet: str
    title: str
    description: str
    goal_amount: float
    milestones: List[MilestoneCreate]


class CampaignResponse(BaseModel):
    id: str
    creator_wallet: str
    title: str
    description: str
    goal_amount: float
    contract_address: Optional[str] = None
    milestones: List[MilestoneResponse]
    backers: List[BackerResponse]
    total_backed: float
    status: str
    created_at: str
    updated_at: str


class CampaignListResponse(BaseModel):
    campaigns: List[CampaignResponse]
    total: int


class FundCampaignRequest(BaseModel):
    backer_wallet: str
    amount: float


class FundCampaignResponse(BaseModel):
    success: bool
    transaction_hash: str
    nft_token_id: Optional[int] = None
    message: str