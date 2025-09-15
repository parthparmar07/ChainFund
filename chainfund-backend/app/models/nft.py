from datetime import datetime
from typing import Optional
from pydantic import BaseModel, Field
from beanie import Document


class NFT(Document):
    campaign_id: str = Field(..., description="ID of the campaign this NFT belongs to")
    owner_wallet: str = Field(..., description="Owner's wallet address")
    token_id: Optional[int] = Field(None, description="NFT token ID on blockchain")
    tier: str = Field(..., description="NFT tier based on backing amount")
    amount_backed: float = Field(..., description="Amount backed to earn this NFT")
    minted_at: datetime = Field(default_factory=datetime.utcnow)
    transaction_hash: Optional[str] = Field(None, description="Minting transaction hash")

    class Settings:
        name = "nfts"
        indexes = [
            "campaign_id",
            "owner_wallet",
            "token_id",
        ]

    class Config:
        json_encoders = {
            datetime: lambda v: v.isoformat()
        }


class NFTCreate(BaseModel):
    campaign_id: str
    owner_wallet: str
    tier: str
    amount_backed: float


class NFTResponse(BaseModel):
    id: str
    campaign_id: str
    owner_wallet: str
    token_id: Optional[int] = None
    tier: str
    amount_backed: float
    minted_at: datetime
    transaction_hash: Optional[str] = None