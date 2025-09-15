from typing import Optional
from pydantic import BaseModel


class SubmitProofRequest(BaseModel):
    pass  # File will be uploaded via multipart


class SubmitProofResponse(BaseModel):
    success: bool
    proof_ipfs: str
    message: str


class VoteOnMilestoneRequest(BaseModel):
    backer_wallet: str
    vote: bool  # True for approve, False for reject


class VoteOnMilestoneResponse(BaseModel):
    success: bool
    vote_recorded: bool
    milestone_status: str
    transaction_hash: Optional[str] = None
    message: str


class MilestoneProgress(BaseModel):
    index: int
    title: str
    amount: float
    status: str
    proof_ipfs: Optional[str] = None
    approval_percentage: float
    total_votes: int