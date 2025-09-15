from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from typing import List, Optional

# Simple FastAPI app for testing
app = FastAPI(
    title="ChainFund Lite API",
    description="Decentralized crowdfunding dApp backend",
    version="1.0.0"
)

# Utility functions for wallet validation
def validate_wallet_address(address: str) -> bool:
    """Validate Ethereum wallet address format"""
    if not address or not isinstance(address, str):
        return False
    if not address.startswith('0x'):
        return False
    if len(address) != 42:  # 0x + 40 hex characters
        return False
    try:
        int(address, 16)  # Check if it's valid hex
        return True
    except ValueError:
        return False

def normalize_wallet_address(address: str) -> str:
    """Normalize wallet address to lowercase"""
    return address.lower()

# Simple CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=[
        "http://localhost:3000",
        "http://localhost:8080", 
        "http://127.0.0.1:3000",
        "http://127.0.0.1:8080"
    ],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Mock data models
class User(BaseModel):
    id: str = "user_123"
    wallet_address: str
    username: Optional[str] = None
    email: Optional[str] = None
    created_at: str = "2024-01-01T00:00:00Z"

class AuthRequest(BaseModel):
    wallet_address: str
    signature: str
    message: str

class AuthResponse(BaseModel):
    access_token: str
    token_type: str = "bearer"
    user: User

class Milestone(BaseModel):
    id: str
    title: str
    description: str
    amount: float
    status: str = "pending"
    votes_for: int = 0
    votes_against: int = 0
    total_votes: int = 0

class Backer(BaseModel):
    id: str
    wallet_address: str
    amount: float
    timestamp: str

class Campaign(BaseModel):
    id: str
    title: str
    description: str
    goal_amount: float
    total_backed: float
    status: str = "active"
    creator_wallet: str
    milestones: List[Milestone] = []
    backers: List[Backer] = []
    created_at: str = "2024-01-01T00:00:00Z"
    updated_at: str = "2024-01-01T00:00:00Z"
    category: Optional[str] = None
    end_date: Optional[str] = None

class CampaignsResponse(BaseModel):
    campaigns: List[Campaign]
    total: int
    page: int
    limit: int

@app.get("/")
async def root():
    return {"message": "ChainFund Lite API", "version": "1.0.0", "status": "running"}

@app.get("/health")
async def health_check():
    return {"status": "healthy"}

@app.get("/api/v1/test")
async def test_endpoint():
    return {"message": "API is working!", "status": "success"}

# User authentication endpoint
@app.post("/api/v1/users/auth", response_model=AuthResponse)
async def authenticate_user(auth_request: AuthRequest):
    # Mock authentication with different users based on wallet
    mock_users = {
        "0x742d35Cc6634C0532925a3b844Bc454e4438f44e": User(
            id="user_alex",
            wallet_address="0x742d35Cc6634C0532925a3b844Bc454e4438f44e",
            username="AlexChen",
            email="alex.chen@example.com",
            created_at="2024-01-01T00:00:00Z"
        ),
        "0x8d4e6f2a9b1c7d5e3f8a2b6c9d4e1f5a": User(
            id="user_sarah",
            wallet_address="0x8d4e6f2a9b1c7d5e3f8a2b6c9d4e1f5a",
            username="SarahJohnson",
            email="sarah.johnson@example.com",
            created_at="2024-01-15T00:00:00Z"
        ),
        "0x3e7f1a9b5c2d8e4f6a2b7c9d1e5f3a8b": User(
            id="user_mike",
            wallet_address="0x3e7f1a9b5c2d8e4f6a2b7c9d1e5f3a8b",
            username="MikeRodriguez",
            email="mike.rodriguez@example.com",
            created_at="2024-02-01T00:00:00Z"
        )
    }

    # Default user if wallet not found
    user = mock_users.get(auth_request.wallet_address, User(
        wallet_address=auth_request.wallet_address,
        username=f"User{auth_request.wallet_address[-4:]}",
        created_at="2024-01-01T00:00:00Z"
    ))

    return AuthResponse(
        access_token="mock_jwt_token_123",
        user=user
    )

# Get current user
@app.get("/api/v1/users/me", response_model=User)
async def get_current_user():
    # Mock user with more realistic data
    return User(
        id="user_123",
        wallet_address="0x742d35Cc6634C0532925a3b844Bc454e4438f44e",
        username="AlexChen",
        email="alex.chen@example.com",
        created_at="2024-01-01T00:00:00Z"
    )

# Create campaign endpoint
@app.post("/api/v1/campaigns", response_model=Campaign)
async def create_campaign(campaign_data: dict):
    # Mock campaign creation
    return Campaign(
        id="campaign_new",
        title=campaign_data.get("title", "New Campaign"),
        description=campaign_data.get("description", "Campaign description"),
        goal_amount=campaign_data.get("goal_amount", 10000.0),
        total_backed=0.0,
        status="active",
        creator_wallet="0x742d35Cc6634C0532925a3b844Bc454e4438f44e",
        category=campaign_data.get("category", "Technology"),
        created_at="2024-01-01T00:00:00Z",
        updated_at="2024-01-01T00:00:00Z",
        milestones=[],
        backers=[]
    )

# Fund campaign endpoint
@app.post("/api/v1/funding")
async def fund_campaign(funding_data: dict):
    # Mock funding response
    return {
        "transaction_hash": "0x123456789abcdef0123456789abcdef0123456789abcdef0123456789abcdef",
        "amount": funding_data.get("amount", 100.0),
        "campaign_id": funding_data.get("campaign_id", "campaign_1")
    }

# Get available categories
@app.get("/api/v1/campaigns/categories")
async def get_campaign_categories():
    """Get all available campaign categories with counts"""
    # Mock categories with counts
    categories = [
        {"name": "Technology", "count": 3, "description": "Blockchain, AI, and software projects"},
        {"name": "Healthcare", "count": 2, "description": "Medical devices, telemedicine, and health tech"},
        {"name": "Environment", "count": 1, "description": "Sustainable energy, water purification, and eco-projects"},
        {"name": "Education", "count": 1, "description": "Learning platforms and educational technology"},
        {"name": "Agriculture", "count": 1, "description": "Farming technology and food production"},
        {"name": "Gaming", "count": 1, "description": "Blockchain gaming and metaverse projects"},
        {"name": "Logistics", "count": 1, "description": "Supply chain and transportation optimization"},
        {"name": "Energy", "count": 1, "description": "Renewable energy and trading platforms"}
    ]
    return {"categories": categories}

# Get recent activity
@app.get("/api/v1/activity/recent")
async def get_recent_activity(limit: int = 10):
    # Mock recent activity data
    activities = [
        {
            "id": "activity_1",
            "type": "funding",
            "description": "Alex Chen backed 'AI-Powered Health Monitor'",
            "amount": 500.0,
            "campaign_title": "AI-Powered Health Monitor",
            "timestamp": "2024-01-20T14:30:00Z",
            "user": "Alex Chen"
        },
        {
            "id": "activity_2",
            "type": "milestone_approved",
            "description": "Milestone 'Prototype Development' was approved",
            "campaign_title": "AI-Powered Health Monitor",
            "timestamp": "2024-01-19T16:45:00Z",
            "user": "Community Vote"
        },
        {
            "id": "activity_3",
            "type": "funding",
            "description": "Sarah Johnson backed 'Sustainable Water Purification System'",
            "amount": 1000.0,
            "campaign_title": "Sustainable Water Purification System",
            "timestamp": "2024-01-18T11:20:00Z",
            "user": "Sarah Johnson"
        },
        {
            "id": "activity_4",
            "type": "campaign_funded",
            "description": "Campaign 'Sustainable Water Purification System' reached funding goal",
            "campaign_title": "Sustainable Water Purification System",
            "timestamp": "2024-01-17T09:15:00Z",
            "user": "System"
        },
        {
            "id": "activity_5",
            "type": "funding",
            "description": "Mike Rodriguez backed 'Decentralized Social Media Platform'",
            "amount": 2000.0,
            "campaign_title": "Decentralized Social Media Platform",
            "timestamp": "2024-01-16T13:40:00Z",
            "user": "Mike Rodriguez"
        },
        {
            "id": "activity_6",
            "type": "milestone_started",
            "description": "Milestone 'Mobile App Development' started",
            "campaign_title": "Decentralized Social Media Platform",
            "timestamp": "2024-01-15T10:25:00Z",
            "user": "System"
        },
        {
            "id": "activity_7",
            "type": "funding",
            "description": "Anonymous backer supported 'Urban Farming Revolution'",
            "amount": 1500.0,
            "campaign_title": "Urban Farming Revolution",
            "timestamp": "2024-01-14T15:50:00Z",
            "user": "Anonymous"
        },
        {
            "id": "activity_8",
            "type": "funding",
            "description": "David Kim backed 'Quantum Computing Education Platform'",
            "amount": 2500.0,
            "campaign_title": "Quantum Computing Education Platform",
            "timestamp": "2024-01-13T12:10:00Z",
            "user": "David Kim"
        }
    ]

    return {"activities": activities[:limit]}

# Get campaigns endpoint
@app.get("/api/v1/campaigns", response_model=CampaignsResponse)
async def get_campaigns(
    page: int = 1,
    limit: int = 10,
    status: Optional[str] = None,
    category: Optional[str] = None,
    creator: Optional[str] = None
):
    # Rich mock campaigns data
    mock_campaigns = [
        # Healthcare campaigns
        Campaign(
            id="campaign_1",
            title="AI-Powered Health Monitor",
            description="Revolutionary wearable device for continuous health monitoring using advanced AI algorithms. Features real-time vital signs tracking, predictive health insights, and seamless integration with healthcare providers.",
            goal_amount=50000.0,
            total_backed=32500.0,
            status="active",
            creator_wallet="0x742d35Cc6634C0532925a3b844Bc454e4438f44e",
            category="Healthcare",
            created_at="2024-01-15T10:30:00Z",
            updated_at="2024-01-20T14:22:00Z",
            end_date="2024-04-15T23:59:59Z",
            milestones=[
                Milestone(
                    id="milestone_1_1",
                    title="Prototype Development",
                    description="Complete initial prototype with core AI algorithms",
                    amount=15000.0,
                    status="completed",
                    votes_for=45,
                    votes_against=3,
                    total_votes=48
                ),
                Milestone(
                    id="milestone_1_2",
                    title="Clinical Testing Phase 1",
                    description="Conduct initial clinical trials with 100 participants",
                    amount=20000.0,
                    status="active",
                    votes_for=38,
                    votes_against=5,
                    total_votes=43
                ),
                Milestone(
                    id="milestone_1_3",
                    title="FDA Approval Preparation",
                    description="Prepare documentation and testing for FDA approval",
                    amount=15000.0,
                    status="pending",
                    votes_for=0,
                    votes_against=0,
                    total_votes=0
                )
            ],
            backers=[
                Backer(id="backer_1_1", wallet_address="0x8ba1f109551bD432803012645261768497d", amount=500.0, timestamp="2024-01-16T09:15:00Z"),
                Backer(id="backer_1_2", wallet_address="0x9c2d4e5f6a7b8c9d0e1f2a3b4c5d6e7f8", amount=1000.0, timestamp="2024-01-17T11:30:00Z"),
                Backer(id="backer_1_3", wallet_address="0xa1b2c3d4e5f678901234567890abcdef", amount=750.0, timestamp="2024-01-18T14:45:00Z"),
                Backer(id="backer_1_4", wallet_address="0xb2c3d4e5f6789a0123456789abcdef01", amount=2500.0, timestamp="2024-01-19T16:20:00Z"),
                Backer(id="backer_1_5", wallet_address="0xc3d4e5f6789a01b23456789abcdef012", amount=300.0, timestamp="2024-01-20T10:10:00Z"),
            ]
        ),
        # Environment campaigns
        Campaign(
            id="campaign_2",
            title="Sustainable Water Purification System",
            description="Low-cost, solar-powered water purification system for developing regions. Uses advanced membrane technology and IoT sensors for real-time water quality monitoring and automated maintenance.",
            goal_amount=25000.0,
            total_backed=25000.0,
            status="funded",
            creator_wallet="0x8d4e6f2a9b1c7d5e3f8a2b6c9d4e1f5a",
            category="Environment",
            created_at="2024-02-10T08:15:00Z",
            updated_at="2024-02-25T12:30:00Z",
            end_date="2024-05-10T23:59:59Z",
            milestones=[
                Milestone(
                    id="milestone_2_1",
                    title="System Design & Prototyping",
                    description="Complete system design and build functional prototype",
                    amount=8000.0,
                    status="completed",
                    votes_for=52,
                    votes_against=2,
                    total_votes=54
                ),
                Milestone(
                    id="milestone_2_2",
                    title="Field Testing in Kenya",
                    description="Deploy and test systems in 5 villages in Kenya",
                    amount=12000.0,
                    status="completed",
                    votes_for=48,
                    votes_against=4,
                    total_votes=52
                ),
                Milestone(
                    id="milestone_2_3",
                    title="Manufacturing Setup",
                    description="Establish manufacturing facility for mass production",
                    amount=5000.0,
                    status="active",
                    votes_for=35,
                    votes_against=8,
                    total_votes=43
                )
            ],
            backers=[
                Backer(id="backer_2_1", wallet_address="0xd4e5f6789a01b2c3456789abcdef0123", amount=1000.0, timestamp="2024-02-11T13:20:00Z"),
                Backer(id="backer_2_2", wallet_address="0xe5f6789a01b2c3d456789abcdef01234", amount=2000.0, timestamp="2024-02-12T15:45:00Z"),
                Backer(id="backer_2_3", wallet_address="0xf6789a01b2c3d4e56789abcdef012345", amount=1500.0, timestamp="2024-02-13T09:30:00Z"),
                Backer(id="backer_2_4", wallet_address="0x789a01b2c3d4e5f6789abcdef0123456", amount=3000.0, timestamp="2024-02-14T11:15:00Z"),
                Backer(id="backer_2_5", wallet_address="0x89a01b2c3d4e5f6789abcdef01234567", amount=500.0, timestamp="2024-02-15T14:00:00Z"),
                Backer(id="backer_2_6", wallet_address="0x9a01b2c3d4e5f6789abcdef012345678", amount=2500.0, timestamp="2024-02-16T16:30:00Z"),
                Backer(id="backer_2_7", wallet_address="0xa01b2c3d4e5f6789abcdef0123456789", amount=800.0, timestamp="2024-02-17T10:45:00Z"),
                Backer(id="backer_2_8", wallet_address="0x01b2c3d4e5f6789abcdef0123456789a", amount=1200.0, timestamp="2024-02-18T12:20:00Z"),
                Backer(id="backer_2_9", wallet_address="0x1b2c3d4e5f6789abcdef0123456789ab", amount=4000.0, timestamp="2024-02-19T08:55:00Z"),
            ]
        ),
        # Technology campaigns
        Campaign(
            id="campaign_3",
            title="Decentralized Social Media Platform",
            description="Privacy-first social media platform built on blockchain technology. Features end-to-end encryption, decentralized content moderation, and creator-owned data.",
            goal_amount=75000.0,
            total_backed=45600.0,
            status="active",
            creator_wallet="0x3e7f1a9b5c2d8e4f6a2b7c9d1e5f3a8b",
            category="Technology",
            created_at="2024-03-01T14:20:00Z",
            updated_at="2024-03-15T16:45:00Z",
            end_date="2024-06-01T23:59:59Z",
            milestones=[
                Milestone(
                    id="milestone_3_1",
                    title="Core Protocol Development",
                    description="Develop the core blockchain protocol and smart contracts",
                    amount=25000.0,
                    status="completed",
                    votes_for=67,
                    votes_against=5,
                    total_votes=72
                ),
                Milestone(
                    id="milestone_3_2",
                    title="Mobile App Development",
                    description="Build iOS and Android mobile applications",
                    amount=30000.0,
                    status="active",
                    votes_for=42,
                    votes_against=12,
                    total_votes=54
                ),
                Milestone(
                    id="milestone_3_3",
                    title="Beta Launch & Testing",
                    description="Launch beta version and conduct user testing",
                    amount=20000.0,
                    status="pending",
                    votes_for=0,
                    votes_against=0,
                    total_votes=0
                )
            ],
            backers=[
                Backer(id="backer_3_1", wallet_address="0x2b3c4d5e6f789a0123456789abcdef01", amount=2000.0, timestamp="2024-03-02T10:30:00Z"),
                Backer(id="backer_3_2", wallet_address="0x3c4d5e6f789a01b23456789abcdef012", amount=1500.0, timestamp="2024-03-03T12:15:00Z"),
                Backer(id="backer_3_3", wallet_address="0x4d5e6f789a01b2c3456789abcdef0123", amount=3000.0, timestamp="2024-03-04T14:45:00Z"),
                Backer(id="backer_3_4", wallet_address="0x5e6f789a01b2c3d456789abcdef01234", amount=5000.0, timestamp="2024-03-05T16:20:00Z"),
                Backer(id="backer_3_5", wallet_address="0x6f789a01b2c3d4e56789abcdef012345", amount=800.0, timestamp="2024-03-06T09:10:00Z"),
                Backer(id="backer_3_6", wallet_address="0x789a01b2c3d4e5f6789abcdef0123456", amount=1200.0, timestamp="2024-03-07T11:55:00Z"),
                Backer(id="backer_3_7", wallet_address="0x89a01b2c3d4e5f6789abcdef01234567", amount=2500.0, timestamp="2024-03-08T13:30:00Z"),
            ]
        ),
        # Agriculture campaigns
        Campaign(
            id="campaign_4",
            title="Urban Farming Revolution",
            description="Vertical farming technology for urban environments. Automated hydroponic systems with AI optimization for maximum yield and minimal resource usage.",
            goal_amount=40000.0,
            total_backed=40000.0,
            status="funded",
            creator_wallet="0x5f8a2b9c1d7e3f6a4b8d2e9c5f1a7b3",
            category="Agriculture",
            created_at="2024-01-20T09:45:00Z",
            updated_at="2024-02-10T11:20:00Z",
            end_date="2024-04-20T23:59:59Z",
            milestones=[
                Milestone(
                    id="milestone_4_1",
                    title="System Design & Engineering",
                    description="Complete engineering design and prototype development",
                    amount=15000.0,
                    status="completed",
                    votes_for=58,
                    votes_against=4,
                    total_votes=62
                ),
                Milestone(
                    id="milestone_4_2",
                    title="Pilot Installation",
                    description="Install pilot systems in 3 urban locations",
                    amount=18000.0,
                    status="completed",
                    votes_for=51,
                    votes_against=7,
                    total_votes=58
                ),
                Milestone(
                    id="milestone_4_3",
                    title="Commercial Launch",
                    description="Launch commercial version and begin mass production",
                    amount=7000.0,
                    status="active",
                    votes_for=39,
                    votes_against=11,
                    total_votes=50
                )
            ],
            backers=[
                Backer(id="backer_4_1", wallet_address="0x9abcdef0123456789a01b2c3d4e5f678", amount=1500.0, timestamp="2024-01-21T14:30:00Z"),
                Backer(id="backer_4_2", wallet_address="0xabcdef0123456789a01b2c3d4e5f6789", amount=2000.0, timestamp="2024-01-22T16:45:00Z"),
                Backer(id="backer_4_3", wallet_address="0xbcdef0123456789a01b2c3d4e5f6789a", amount=1000.0, timestamp="2024-01-23T10:15:00Z"),
                Backer(id="backer_4_4", wallet_address="0xcdef0123456789a01b2c3d4e5f6789ab", amount=3000.0, timestamp="2024-01-24T12:00:00Z"),
                Backer(id="backer_4_5", wallet_address="0xdef0123456789a01b2c3d4e5f6789abc", amount=2500.0, timestamp="2024-01-25T08:30:00Z"),
                Backer(id="backer_4_6", wallet_address="0xef0123456789a01b2c3d4e5f6789abcd", amount=1800.0, timestamp="2024-01-26T15:20:00Z"),
                Backer(id="backer_4_7", wallet_address="0xf0123456789a01b2c3d4e5f6789abcde", amount=4000.0, timestamp="2024-01-27T11:45:00Z"),
                Backer(id="backer_4_8", wallet_address="0x0123456789a01b2c3d4e5f6789abcdef", amount=1200.0, timestamp="2024-01-28T13:10:00Z"),
            ]
        ),
        # Education campaigns
        Campaign(
            id="campaign_5",
            title="Quantum Computing Education Platform",
            description="Interactive online platform teaching quantum computing concepts. Features virtual quantum simulators, hands-on exercises, and certification programs for developers.",
            goal_amount=60000.0,
            total_backed=28500.0,
            status="active",
            creator_wallet="0x1e9f5a3b7c2d8e6f4a9b5c1d7e3f8a2",
            category="Education",
            created_at="2024-02-28T16:30:00Z",
            updated_at="2024-03-10T18:15:00Z",
            end_date="2024-05-28T23:59:59Z",
            milestones=[
                Milestone(
                    id="milestone_5_1",
                    title="Platform Architecture",
                    description="Design and implement core platform architecture",
                    amount=20000.0,
                    status="completed",
                    votes_for=61,
                    votes_against=3,
                    total_votes=64
                ),
                Milestone(
                    id="milestone_5_2",
                    title="Content Development",
                    description="Create comprehensive course content and exercises",
                    amount=25000.0,
                    status="active",
                    votes_for=44,
                    votes_against=9,
                    total_votes=53
                ),
                Milestone(
                    id="milestone_5_3",
                    title="Certification System",
                    description="Implement certification and assessment system",
                    amount=15000.0,
                    status="pending",
                    votes_for=0,
                    votes_against=0,
                    total_votes=0
                )
            ],
            backers=[
                Backer(id="backer_5_1", wallet_address="0x123456789abcdef0123456789abcdef0", amount=2500.0, timestamp="2024-03-01T09:00:00Z"),
                Backer(id="backer_5_2", wallet_address="0x23456789abcdef0123456789abcdef01", amount=1500.0, timestamp="2024-03-02T11:30:00Z"),
                Backer(id="backer_5_3", wallet_address="0x3456789abcdef0123456789abcdef012", amount=3000.0, timestamp="2024-03-03T14:15:00Z"),
                Backer(id="backer_5_4", wallet_address="0x456789abcdef0123456789abcdef0123", amount=1000.0, timestamp="2024-03-04T16:45:00Z"),
                Backer(id="backer_5_5", wallet_address="0x56789abcdef0123456789abcdef01234", amount=2000.0, timestamp="2024-03-05T10:20:00Z"),
            ]
        ),
        # Gaming campaigns
        Campaign(
            id="campaign_6",
            title="Blockchain Gaming Metaverse",
            description="Immersive gaming metaverse built on blockchain technology. Features true digital ownership, play-to-earn mechanics, and cross-game interoperability.",
            goal_amount=100000.0,
            total_backed=100000.0,
            status="completed",
            creator_wallet="0x7b2c9d5e1f8a3b6c9d2e5f1a8b4c7d9",
            category="Gaming",
            created_at="2023-12-01T12:00:00Z",
            updated_at="2024-01-15T14:30:00Z",
            end_date="2024-03-01T23:59:59Z",
            milestones=[
                Milestone(
                    id="milestone_6_1",
                    title="Core Engine Development",
                    description="Develop the core gaming engine and blockchain integration",
                    amount=35000.0,
                    status="completed",
                    votes_for=89,
                    votes_against=6,
                    total_votes=95
                ),
                Milestone(
                    id="milestone_6_2",
                    title="First Game World",
                    description="Create and launch the first game world",
                    amount=40000.0,
                    status="completed",
                    votes_for=76,
                    votes_against=11,
                    total_votes=87
                ),
                Milestone(
                    id="milestone_6_3",
                    title="Metaverse Expansion",
                    description="Add additional worlds and cross-game features",
                    amount=25000.0,
                    status="completed",
                    votes_for=82,
                    votes_against=8,
                    total_votes=90
                )
            ],
            backers=[
                Backer(id="backer_6_1", wallet_address="0x6789abcdef0123456789abcdef012345", amount=5000.0, timestamp="2023-12-02T15:30:00Z"),
                Backer(id="backer_6_2", wallet_address="0x789abcdef0123456789abcdef0123456", amount=3000.0, timestamp="2023-12-03T17:45:00Z"),
                Backer(id="backer_6_3", wallet_address="0x89abcdef0123456789abcdef01234567", amount=8000.0, timestamp="2023-12-04T10:15:00Z"),
                Backer(id="backer_6_4", wallet_address="0x9abcdef0123456789abcdef012345678", amount=2000.0, timestamp="2023-12-05T12:30:00Z"),
                Backer(id="backer_6_5", wallet_address="0xabcdef0123456789abcdef0123456789", amount=4000.0, timestamp="2023-12-06T14:00:00Z"),
                Backer(id="backer_6_6", wallet_address="0xbcdef0123456789abcdef0123456789a", amount=6000.0, timestamp="2023-12-07T16:20:00Z"),
                Backer(id="backer_6_7", wallet_address="0xcdef0123456789abcdef0123456789ab", amount=1500.0, timestamp="2023-12-08T09:45:00Z"),
                Backer(id="backer_6_8", wallet_address="0xdef0123456789abcdef0123456789abc", amount=7000.0, timestamp="2023-12-09T11:10:00Z"),
                Backer(id="backer_6_9", wallet_address="0xef0123456789abcdef0123456789abcd", amount=2500.0, timestamp="2023-12-10T13:25:00Z"),
                Backer(id="backer_6_10", wallet_address="0xf0123456789abcdef0123456789abcde", amount=10000.0, timestamp="2023-12-11T08:50:00Z"),
            ]
        ),
        # Logistics campaigns
        Campaign(
            id="campaign_7",
            title="AI-Powered Supply Chain Optimization",
            description="Machine learning platform for optimizing global supply chains. Features predictive analytics, automated procurement, and real-time inventory management.",
            goal_amount=80000.0,
            total_backed=62400.0,
            status="active",
            creator_wallet="0x4d8e2f6a9b1c5d7e3f8a2b6c9d4e1f5",
            category="Logistics",
            created_at="2024-03-15T11:45:00Z",
            updated_at="2024-03-20T13:20:00Z",
            end_date="2024-06-15T23:59:59Z",
            milestones=[
                Milestone(
                    id="milestone_7_1",
                    title="AI Model Development",
                    description="Develop core AI models for supply chain optimization",
                    amount=30000.0,
                    status="completed",
                    votes_for=71,
                    votes_against=4,
                    total_votes=75
                ),
                Milestone(
                    id="milestone_7_2",
                    title="Platform Integration",
                    description="Integrate with major ERP and supply chain systems",
                    amount=35000.0,
                    status="active",
                    votes_for=48,
                    votes_against=13,
                    total_votes=61
                ),
                Milestone(
                    id="milestone_7_3",
                    title="Enterprise Deployment",
                    description="Deploy platform for enterprise customers",
                    amount=15000.0,
                    status="pending",
                    votes_for=0,
                    votes_against=0,
                    total_votes=0
                )
            ],
            backers=[
                Backer(id="backer_7_1", wallet_address="0x0123456789abcdef0123456789abcdef", amount=4000.0, timestamp="2024-03-16T14:30:00Z"),
                Backer(id="backer_7_2", wallet_address="0x123456789abcdef0123456789abcdef0", amount=2500.0, timestamp="2024-03-17T16:45:00Z"),
                Backer(id="backer_7_3", wallet_address="0x23456789abcdef0123456789abcdef01", amount=6000.0, timestamp="2024-03-18T10:15:00Z"),
                Backer(id="backer_7_4", wallet_address="0x3456789abcdef0123456789abcdef012", amount=3000.0, timestamp="2024-03-19T12:00:00Z"),
                Backer(id="backer_7_5", wallet_address="0x456789abcdef0123456789abcdef0123", amount=8000.0, timestamp="2024-03-20T08:30:00Z"),
            ]
        ),
        # Energy campaigns
        Campaign(
            id="campaign_8",
            title="Renewable Energy Trading Platform",
            description="Decentralized platform for trading renewable energy credits. Features blockchain-based certificates, smart contracts, and automated settlement.",
            goal_amount=55000.0,
            total_backed=41800.0,
            status="active",
            creator_wallet="0x6e9f3a7b1c8d5e2f9a4b6c1d8e3f7a2",
            category="Energy",
            created_at="2024-02-15T13:20:00Z",
            updated_at="2024-02-28T15:45:00Z",
            end_date="2024-05-15T23:59:59Z",
            milestones=[
                Milestone(
                    id="milestone_8_1",
                    title="Smart Contract Development",
                    description="Develop smart contracts for energy credit trading",
                    amount=20000.0,
                    status="completed",
                    votes_for=63,
                    votes_against=5,
                    total_votes=68
                ),
                Milestone(
                    id="milestone_8_2",
                    title="Oracle Integration",
                    description="Integrate with energy production data oracles",
                    amount=25000.0,
                    status="active",
                    votes_for=41,
                    votes_against=14,
                    total_votes=55
                ),
                Milestone(
                    id="milestone_8_3",
                    title="Pilot Program Launch",
                    description="Launch pilot program with renewable energy producers",
                    amount=10000.0,
                    status="pending",
                    votes_for=0,
                    votes_against=0,
                    total_votes=0
                )
            ],
            backers=[
                Backer(id="backer_8_1", wallet_address="0x56789abcdef0123456789abcdef01234", amount=3500.0, timestamp="2024-02-16T09:30:00Z"),
                Backer(id="backer_8_2", wallet_address="0x6789abcdef0123456789abcdef012345", amount=2000.0, timestamp="2024-02-17T11:45:00Z"),
                Backer(id="backer_8_3", wallet_address="0x789abcdef0123456789abcdef0123456", amount=4500.0, timestamp="2024-02-18T14:15:00Z"),
                Backer(id="backer_8_4", wallet_address="0x89abcdef0123456789abcdef01234567", amount=1500.0, timestamp="2024-02-19T16:30:00Z"),
                Backer(id="backer_8_5", wallet_address="0x9abcdef0123456789abcdef012345678", amount=2800.0, timestamp="2024-02-20T10:00:00Z"),
            ]
        ),
        # More Technology campaigns
        Campaign(
            id="campaign_9",
            title="Decentralized Identity Protocol",
            description="Self-sovereign identity solution built on blockchain. Features privacy-preserving credentials, selective disclosure, and interoperability across platforms.",
            goal_amount=65000.0,
            total_backed=38750.0,
            status="active",
            creator_wallet="0x9f2e5c8b1a7d4f3e6b9c2d5e8f1a4b7",
            category="Technology",
            created_at="2024-03-10T15:30:00Z",
            updated_at="2024-03-18T17:45:00Z",
            end_date="2024-06-10T23:59:59Z",
            milestones=[
                Milestone(
                    id="milestone_9_1",
                    title="Protocol Specification",
                    description="Define the core protocol specifications and standards",
                    amount=20000.0,
                    status="completed",
                    votes_for=55,
                    votes_against=8,
                    total_votes=63
                ),
                Milestone(
                    id="milestone_9_2",
                    title="Reference Implementation",
                    description="Build reference implementation and SDK",
                    amount=30000.0,
                    status="active",
                    votes_for=38,
                    votes_against=15,
                    total_votes=53
                ),
                Milestone(
                    id="milestone_9_3",
                    title="Integration Partners",
                    description="Partner with platforms for integration and adoption",
                    amount=15000.0,
                    status="pending",
                    votes_for=0,
                    votes_against=0,
                    total_votes=0
                )
            ],
            backers=[
                Backer(id="backer_9_1", wallet_address="0xabcdef0123456789abcdef0123456789", amount=2500.0, timestamp="2024-03-11T10:20:00Z"),
                Backer(id="backer_9_2", wallet_address="0xbcdef0123456789abcdef0123456789a", amount=1800.0, timestamp="2024-03-12T12:45:00Z"),
                Backer(id="backer_9_3", wallet_address="0xcdef0123456789abcdef0123456789ab", amount=3200.0, timestamp="2024-03-13T14:30:00Z"),
                Backer(id="backer_9_4", wallet_address="0xdef0123456789abcdef0123456789abc", amount=1500.0, timestamp="2024-03-14T16:15:00Z"),
                Backer(id="backer_9_5", wallet_address="0xef0123456789abcdef0123456789abcd", amount=4000.0, timestamp="2024-03-15T09:00:00Z"),
            ]
        ),
        # More Healthcare campaigns
        Campaign(
            id="campaign_10",
            title="Telemedicine AI Assistant",
            description="AI-powered telemedicine platform for remote patient monitoring. Features predictive diagnostics, automated triage, and seamless EHR integration.",
            goal_amount=45000.0,
            total_backed=45000.0,
            status="funded",
            creator_wallet="0x2f7e9c5b1d8a4f6e3b9d2c5e8f1a4b7",
            category="Healthcare",
            created_at="2024-01-25T14:15:00Z",
            updated_at="2024-02-15T16:30:00Z",
            end_date="2024-04-25T23:59:59Z",
            milestones=[
                Milestone(
                    id="milestone_10_1",
                    title="AI Model Training",
                    description="Train and validate AI diagnostic models",
                    amount=18000.0,
                    status="completed",
                    votes_for=62,
                    votes_against=3,
                    total_votes=65
                ),
                Milestone(
                    id="milestone_10_2",
                    title="Platform Development",
                    description="Build the telemedicine platform and user interfaces",
                    amount=20000.0,
                    status="completed",
                    votes_for=58,
                    votes_against=7,
                    total_votes=65
                ),
                Milestone(
                    id="milestone_10_3",
                    title="Clinical Validation",
                    description="Conduct clinical trials and obtain regulatory approval",
                    amount=7000.0,
                    status="active",
                    votes_for=45,
                    votes_against=12,
                    total_votes=57
                )
            ],
            backers=[
                Backer(id="backer_10_1", wallet_address="0xf0123456789abcdef0123456789abcde", amount=2000.0, timestamp="2024-01-26T11:30:00Z"),
                Backer(id="backer_10_2", wallet_address="0x0123456789abcdef0123456789abcdef", amount=1500.0, timestamp="2024-01-27T13:45:00Z"),
                Backer(id="backer_10_3", wallet_address="0x123456789abcdef0123456789abcdef0", amount=3000.0, timestamp="2024-01-28T15:20:00Z"),
                Backer(id="backer_10_4", wallet_address="0x23456789abcdef0123456789abcdef01", amount=2500.0, timestamp="2024-01-29T10:10:00Z"),
                Backer(id="backer_10_5", wallet_address="0x3456789abcdef0123456789abcdef012", amount=1800.0, timestamp="2024-01-30T12:55:00Z"),
                Backer(id="backer_10_6", wallet_address="0x456789abcdef0123456789abcdef0123", amount=3500.0, timestamp="2024-01-31T14:40:00Z"),
                Backer(id="backer_10_7", wallet_address="0x56789abcdef0123456789abcdef01234", amount=1200.0, timestamp="2024-02-01T09:25:00Z"),
                Backer(id="backer_10_8", wallet_address="0x6789abcdef0123456789abcdef012345", amount=2800.0, timestamp="2024-02-02T16:15:00Z"),
            ]
        )
    ]

    # Apply filters
    filtered_campaigns = mock_campaigns

    if status:
        filtered_campaigns = [c for c in filtered_campaigns if c.status == status]

    if category:
        filtered_campaigns = [c for c in filtered_campaigns if c.category and c.category.lower() == category.lower()]

    if creator:
        if validate_wallet_address(creator):
            normalized_creator = normalize_wallet_address(creator)
            filtered_campaigns = [c for c in filtered_campaigns if c.creator_wallet == normalized_creator]
        else:
            raise HTTPException(status_code=400, detail="Invalid creator wallet address")

    # Apply pagination
    start_idx = (page - 1) * limit
    end_idx = start_idx + limit
    paginated_campaigns = filtered_campaigns[start_idx:end_idx]

    return CampaignsResponse(
        campaigns=paginated_campaigns,
        total=len(filtered_campaigns),
        page=page,
        limit=limit
    )# Get single campaign
@app.get("/api/v1/campaigns/{campaign_id}", response_model=Campaign)
async def get_campaign(campaign_id: str):
    # Mock campaign data with detailed information
    mock_campaigns = {
        "campaign_1": Campaign(
            id="campaign_1",
            title="AI-Powered Health Monitor",
            description="Revolutionary wearable device for continuous health monitoring using advanced AI algorithms. Features real-time vital signs tracking, predictive health insights, and seamless integration with healthcare providers.",
            goal_amount=50000.0,
            total_backed=32500.0,
            status="active",
            creator_wallet="0x742d35Cc6634C0532925a3b844Bc454e4438f44e",
            category="Healthcare",
            created_at="2024-01-15T10:30:00Z",
            updated_at="2024-01-20T14:22:00Z",
            end_date="2024-04-15T23:59:59Z",
            milestones=[
                Milestone(
                    id="milestone_1_1",
                    title="Prototype Development",
                    description="Complete initial prototype with core AI algorithms",
                    amount=15000.0,
                    status="completed",
                    votes_for=45,
                    votes_against=3,
                    total_votes=48
                ),
                Milestone(
                    id="milestone_1_2",
                    title="Clinical Testing Phase 1",
                    description="Conduct initial clinical trials with 100 participants",
                    amount=20000.0,
                    status="active",
                    votes_for=38,
                    votes_against=5,
                    total_votes=43
                ),
                Milestone(
                    id="milestone_1_3",
                    title="FDA Approval Preparation",
                    description="Prepare documentation and testing for FDA approval",
                    amount=15000.0,
                    status="pending",
                    votes_for=0,
                    votes_against=0,
                    total_votes=0
                )
            ],
            backers=[
                Backer(id="backer_1_1", wallet_address="0x8ba1f109551bD432803012645261768497d", amount=500.0, timestamp="2024-01-16T09:15:00Z"),
                Backer(id="backer_1_2", wallet_address="0x9c2d4e5f6a7b8c9d0e1f2a3b4c5d6e7f8", amount=1000.0, timestamp="2024-01-17T11:30:00Z"),
                Backer(id="backer_1_3", wallet_address="0xa1b2c3d4e5f678901234567890abcdef", amount=750.0, timestamp="2024-01-18T14:45:00Z"),
                Backer(id="backer_1_4", wallet_address="0xb2c3d4e5f6789a0123456789abcdef01", amount=2500.0, timestamp="2024-01-19T16:20:00Z"),
                Backer(id="backer_1_5", wallet_address="0xc3d4e5f6789a01b23456789abcdef012", amount=300.0, timestamp="2024-01-20T10:10:00Z"),
            ]
        ),
        "campaign_2": Campaign(
            id="campaign_2",
            title="Sustainable Water Purification System",
            description="Low-cost, solar-powered water purification system for developing regions. Uses advanced membrane technology and IoT sensors for real-time water quality monitoring and automated maintenance.",
            goal_amount=25000.0,
            total_backed=25000.0,
            status="funded",
            creator_wallet="0x8d4e6f2a9b1c7d5e3f8a2b6c9d4e1f5a",
            category="Environment",
            created_at="2024-02-10T08:15:00Z",
            updated_at="2024-02-25T12:30:00Z",
            end_date="2024-05-10T23:59:59Z",
            milestones=[
                Milestone(
                    id="milestone_2_1",
                    title="System Design & Prototyping",
                    description="Complete system design and build functional prototype",
                    amount=8000.0,
                    status="completed",
                    votes_for=52,
                    votes_against=2,
                    total_votes=54
                ),
                Milestone(
                    id="milestone_2_2",
                    title="Field Testing in Kenya",
                    description="Deploy and test systems in 5 villages in Kenya",
                    amount=12000.0,
                    status="completed",
                    votes_for=48,
                    votes_against=4,
                    total_votes=52
                ),
                Milestone(
                    id="milestone_2_3",
                    title="Manufacturing Setup",
                    description="Establish manufacturing facility for mass production",
                    amount=5000.0,
                    status="active",
                    votes_for=35,
                    votes_against=8,
                    total_votes=43
                )
            ],
            backers=[
                Backer(id="backer_2_1", wallet_address="0xd4e5f6789a01b2c3456789abcdef0123", amount=1000.0, timestamp="2024-02-11T13:20:00Z"),
                Backer(id="backer_2_2", wallet_address="0xe5f6789a01b2c3d456789abcdef01234", amount=2000.0, timestamp="2024-02-12T15:45:00Z"),
                Backer(id="backer_2_3", wallet_address="0xf6789a01b2c3d4e56789abcdef012345", amount=1500.0, timestamp="2024-02-13T09:30:00Z"),
                Backer(id="backer_2_4", wallet_address="0x789a01b2c3d4e5f6789abcdef0123456", amount=3000.0, timestamp="2024-02-14T11:15:00Z"),
                Backer(id="backer_2_5", wallet_address="0x89a01b2c3d4e5f6789abcdef01234567", amount=500.0, timestamp="2024-02-15T14:00:00Z"),
                Backer(id="backer_2_6", wallet_address="0x9a01b2c3d4e5f6789abcdef012345678", amount=2500.0, timestamp="2024-02-16T16:30:00Z"),
                Backer(id="backer_2_7", wallet_address="0xa01b2c3d4e5f6789abcdef0123456789", amount=800.0, timestamp="2024-02-17T10:45:00Z"),
                Backer(id="backer_2_8", wallet_address="0x01b2c3d4e5f6789abcdef0123456789a", amount=1200.0, timestamp="2024-02-18T12:20:00Z"),
                Backer(id="backer_2_9", wallet_address="0x1b2c3d4e5f6789abcdef0123456789ab", amount=4000.0, timestamp="2024-02-19T08:55:00Z"),
            ]
        )
    }

    if campaign_id not in mock_campaigns:
        raise HTTPException(status_code=404, detail="Campaign not found")

    return mock_campaigns[campaign_id]

# Skill-related mock data
mock_skill_data = {
    "0x742d35cc6634c0532925a3b844bc454e4438f44e": {
        "wallet_address": "0x742d35cc6634c0532925a3b844bc454e4438f44e",
        "skill_score": 245.8,
        "skill_level": "Intermediate",
        "skill_nft_token_id": 12345,
        "total_milestones_completed": 12,
        "total_campaigns_participated": 3,
        "average_completion_time": 8.5,
        "skill_breakdown": {
            "Healthcare": 145.2,
            "Technology": 68.3,
            "Environment": 32.3
        },
        "recent_achievements": [
            {
                "campaign_id": "campaign_1",
                "milestone_title": "Clinical Testing Phase 1",
                "score_earned": 85.5,
                "completed_at": "2024-01-20T14:30:00Z",
                "difficulty": "hard",
                "on_time": True
            },
            {
                "campaign_id": "campaign_1",
                "milestone_title": "Prototype Development",
                "score_earned": 67.2,
                "completed_at": "2024-01-15T10:30:00Z",
                "difficulty": "medium",
                "on_time": True
            }
        ],
        "next_level_threshold": 500.0
    },
    "0x8d4e6f2a9b1c7d5e3f8a2b6c9d4e1f5a": {
        "wallet_address": "0x8d4e6f2a9b1c7d5e3f8a2b6c9d4e1f5a",
        "skill_score": 387.4,
        "skill_level": "Advanced",
        "skill_nft_token_id": 12346,
        "total_milestones_completed": 18,
        "total_campaigns_participated": 4,
        "average_completion_time": 6.2,
        "skill_breakdown": {
            "Environment": 198.7,
            "Healthcare": 124.5,
            "Agriculture": 64.2
        },
        "recent_achievements": [
            {
                "campaign_id": "campaign_2",
                "milestone_title": "Field Testing in Kenya",
                "score_earned": 92.3,
                "completed_at": "2024-02-20T12:15:00Z",
                "difficulty": "hard",
                "on_time": True
            },
            {
                "campaign_id": "campaign_2",
                "milestone_title": "Manufacturing Setup",
                "score_earned": 78.9,
                "completed_at": "2024-02-25T14:45:00Z",
                "difficulty": "medium",
                "on_time": False
            }
        ],
        "next_level_threshold": 1000.0
    },
    "0x3e7f1a9b5c2d8e4f6a2b7c9d1e5f3a8b": {
        "wallet_address": "0x3e7f1a9b5c2d8e4f6a2b7c9d1e5f3a8b",
        "skill_score": 156.2,
        "skill_level": "Beginner",
        "skill_nft_token_id": None,
        "total_milestones_completed": 8,
        "total_campaigns_participated": 2,
        "average_completion_time": 12.3,
        "skill_breakdown": {
            "Technology": 98.7,
            "Healthcare": 57.5
        },
        "recent_achievements": [
            {
                "campaign_id": "campaign_3",
                "milestone_title": "Mobile App Development",
                "score_earned": 45.6,
                "completed_at": "2024-03-10T16:20:00Z",
                "difficulty": "medium",
                "on_time": True
            }
        ],
        "next_level_threshold": 200.0
    },
    "0x5f8a2b9c1d7e3f6a4b8d2e9c5f1a7b3": {
        "wallet_address": "0x5f8a2b9c1d7e3f6a4b8d2e9c5f1a7b3",
        "skill_score": 89.4,
        "skill_level": "Beginner",
        "skill_nft_token_id": None,
        "total_milestones_completed": 5,
        "total_campaigns_participated": 1,
        "average_completion_time": 15.8,
        "skill_breakdown": {
            "Agriculture": 89.4
        },
        "recent_achievements": [
            {
                "campaign_id": "campaign_4",
                "milestone_title": "Commercial Launch",
                "score_earned": 32.1,
                "completed_at": "2024-02-08T11:45:00Z",
                "difficulty": "easy",
                "on_time": True
            }
        ],
        "next_level_threshold": 200.0
    },
    "0x1e9f5a3b7c2d8e6f4a9b5c1d7e3f8a2": {
        "wallet_address": "0x1e9f5a3b7c2d8e6f4a9b5c1d7e3f8a2",
        "skill_score": 723.6,
        "skill_level": "Expert",
        "skill_nft_token_id": 12347,
        "total_milestones_completed": 25,
        "total_campaigns_participated": 6,
        "average_completion_time": 4.7,
        "skill_breakdown": {
            "Education": 245.8,
            "Technology": 198.3,
            "Healthcare": 156.2,
            "Environment": 123.3
        },
        "recent_achievements": [
            {
                "campaign_id": "campaign_5",
                "milestone_title": "Content Development",
                "score_earned": 87.4,
                "completed_at": "2024-03-12T13:30:00Z",
                "difficulty": "hard",
                "on_time": True
            }
        ],
        "next_level_threshold": 1000.0
    }
}

# Skill API endpoints
@app.get("/api/v1/users/skill-score/{wallet_address}")
async def get_user_skill_score(wallet_address: str):
    """Get skill score data for a user"""
    if not validate_wallet_address(wallet_address):
        raise HTTPException(status_code=400, detail="Invalid wallet address")

    normalized_address = normalize_wallet_address(wallet_address)

    # Return mock skill data if available, otherwise return default
    skill_data = mock_skill_data.get(normalized_address, {
        "wallet_address": normalized_address,
        "skill_score": 0.0,
        "skill_level": "Novice",
        "skill_nft_token_id": None,
        "total_milestones_completed": 0,
        "total_campaigns_participated": 0,
        "average_completion_time": None,
        "skill_breakdown": {},
        "recent_achievements": [],
        "next_level_threshold": 50.0
    })

    return skill_data

@app.post("/api/v1/users/skill-activity/{wallet_address}")
async def add_skill_activity(wallet_address: str, activity_data: dict):
    """Add a skill-earning activity for a user"""
    if not validate_wallet_address(wallet_address):
        raise HTTPException(status_code=400, detail="Invalid wallet address")

    normalized_address = normalize_wallet_address(wallet_address)

    # Mock response - in real implementation this would update the user's skill data
    return {
        "message": "Skill activity added successfully",
        "new_skill_score": 150.5,
        "new_skill_level": "Beginner"
    }

@app.post("/api/v1/users/mint-skill-nft/{wallet_address}")
async def mint_skill_nft(wallet_address: str):
    """Mint a skill NFT for a user"""
    if not validate_wallet_address(wallet_address):
        raise HTTPException(status_code=400, detail="Invalid wallet address")

    normalized_address = normalize_wallet_address(wallet_address)

    # Mock NFT minting response
    return {
        "message": "Skill NFT minted successfully",
        "nft_data": {
            "nft_id": "nft_123",
            "token_id": 12348,
            "skill_level": "Intermediate",
            "skill_score": 245.8,
            "color": "#10B981",
            "description": "Gaining expertise",
            "updated": False
        }
    }

@app.get("/api/v1/users/skill-nft/{wallet_address}")
async def get_skill_nft(wallet_address: str):
    """Get skill NFT information for a user"""
    if not validate_wallet_address(wallet_address):
        raise HTTPException(status_code=400, detail="Invalid wallet address")

    normalized_address = normalize_wallet_address(wallet_address)

    skill_data = mock_skill_data.get(normalized_address)
    if skill_data and skill_data.get("skill_nft_token_id"):
        return {
            "skill_nft": {
                "nft_id": f"nft_{skill_data['skill_nft_token_id']}",
                "token_id": skill_data["skill_nft_token_id"],
                "skill_level": skill_data["skill_level"],
                "skill_score": skill_data["skill_score"],
                "color": "#10B981",
                "description": "Gaining expertise"
            }
        }
    else:
        return {"message": "No skill NFT found for user"}

@app.put("/api/v1/users/skill-score/update/{wallet_address}")
async def update_user_skill_score(wallet_address: str):
    """Update user's skill score"""
    if not validate_wallet_address(wallet_address):
        raise HTTPException(status_code=400, detail="Invalid wallet address")

    normalized_address = normalize_wallet_address(wallet_address)

    skill_data = mock_skill_data.get(normalized_address, {
        "skill_score": 0.0,
        "skill_level": "Novice"
    })

    return {
        "message": "Skill score updated successfully",
        "skill_score": skill_data["skill_score"],
        "skill_level": skill_data["skill_level"]
    }

@app.get("/api/v1/users/skill-leaderboard")
async def get_skill_leaderboard(limit: int = 50):
    """Get skill leaderboard"""
    # Sort users by skill score
    leaderboard_entries = []
    for wallet, data in mock_skill_data.items():
        leaderboard_entries.append({
            "wallet_address": wallet,
            "username": None,  # Could be populated from user data
            "skill_score": data["skill_score"],
            "skill_level": data["skill_level"],
            "total_milestones_completed": data["total_milestones_completed"],
            "total_campaigns_participated": data["total_campaigns_participated"],
            "rank": 0  # Will be set after sorting
        })

    # Sort by skill score descending
    leaderboard_entries.sort(key=lambda x: x["skill_score"], reverse=True)

    # Assign ranks
    for i, entry in enumerate(leaderboard_entries, 1):
        entry["rank"] = i

    return {"leaderboard": leaderboard_entries[:limit]}

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)