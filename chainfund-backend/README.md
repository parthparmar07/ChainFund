# ChainFund Backend API

A decentralized crowdfunding dApp backend built with FastAPI, MongoDB, and web3.py for BNB Chain integration.

## Features

-  **FastAPI Backend**: High-performance async API with automatic OpenAPI documentation
-  **Decentralized Crowdfunding**: Milestone-based funding with smart contract integration
-  **NFT Rewards**: Automatic NFT minting for campaign backers based on contribution tiers
-  **MetaMask Authentication**: Wallet signature verification for secure user authentication
-  **IPFS Storage**: Decentralized file storage for milestone proof documents
-  **BNB Chain Integration**: Full web3.py integration with smart contract deployment and interactions

## Tech Stack

- **Backend**: Python 3.9+, FastAPI, Uvicorn
- **Database**: MongoDB with Motor (async driver)
- **Blockchain**: BNB Chain, Solidity smart contracts, web3.py
- **Storage**: IPFS (Pinata SDK or web3.storage)
- **Authentication**: MetaMask wallet signatures
- **Deployment**: Docker-ready

## Project Structure

```
chainfund-backend/
│
├── app/
│   ├── main.py                # FastAPI entry point
│   ├── config.py              # Environment configuration
│   ├── db.py                  # MongoDB connection
│   │
│   ├── models/                # Pydantic + Beanie models
│   │   ├── user.py
│   │   ├── campaign.py
│   │   └── nft.py
│   │
│   ├── routers/               # API route handlers
│   │   ├── users.py
│   │   ├── campaigns.py
│   │   ├── funding.py
│   │   ├── milestones.py
│   │   └── votes.py
│   │
│   ├── services/              # Core business logic
│   │   ├── web3_service.py
│   │   ├── ipfs_service.py
│   │   ├── nft_service.py
│   │   └── auth_service.py
│   │
│   ├── utils/                 # Helper utilities
│   │   ├── signature.py
│   │   └── responses.py
│   │
│   └── schemas/               # API request/response schemas
│       ├── user_schemas.py
│       ├── campaign_schemas.py
│       └── milestone_schemas.py
│
├── requirements.txt
├── .env
└── README.md
```

## Quick Start
### Prerequisites

- Python 3.9+
- MongoDB
- Node.js (for MetaMask integration)
- BNB Chain RPC access

### Installation

1. **Clone the repository**
   ```bash
   git clone <repository-url>
   cd chainfund-backend
   ```

2. **Create virtual environment**
   ```bash
   python -m venv venv
   source venv/bin/activate  # On Windows: venv\Scripts\activate
   ```

3. **Install dependencies**
   ```bash
   pip install -r requirements.txt
   ```

4. **Configure environment variables**
   ```bash
   cp .env.example .env
   # Edit .env with your configuration
   ```

5. **Start MongoDB**
   ```bash
   mongod  # Or use your preferred MongoDB setup
   ```

6. **Run the application**
   ```bash
   uvicorn app.main:app --reload
   ```

The API will be available at `http://localhost:8000`

## Environment Configuration

Create a `.env` file with the following variables:

```env
# MongoDB Configuration
MONGODB_URL=mongodb://localhost:27017
DATABASE_NAME=chainfund_lite

# BNB Chain Configuration
BNB_RPC_URL=https://bsc-dataseed1.binance.org/
PRIVATE_KEY=your_private_key_here
CHAIN_ID=56

# IPFS Configuration (Pinata)
PINATA_API_KEY=your_pinata_api_key
PINATA_SECRET_KEY=your_pinata_secret_key

# Alternative IPFS (web3.storage)
WEB3_STORAGE_TOKEN=your_web3_storage_token

# JWT Configuration
JWT_SECRET_KEY=your_jwt_secret_key
JWT_ALGORITHM=HS256
ACCESS_TOKEN_EXPIRE_MINUTES=30

# CORS Configuration
ALLOWED_ORIGINS=http://localhost:3000,http://localhost:8080

# Contract Addresses (filled after deployment)
CAMPAIGN_FACTORY_ADDRESS=0x0000000000000000000000000000000000000000
NFT_CONTRACT_ADDRESS=0x0000000000000000000000000000000000000000
```

## API Documentation

### Authentication

All API endpoints require MetaMask signature authentication. Use the `/api/v1/users/auth` endpoint to authenticate and receive a JWT token.

### Core Endpoints

#### Users
- `POST /api/v1/users/register` - Register new user
- `POST /api/v1/users/auth` - Authenticate with MetaMask signature
- `GET /api/v1/users/me` - Get current user info

#### Campaigns
- `POST /api/v1/campaigns` - Create new campaign
- `GET /api/v1/campaigns` - List all campaigns
- `GET /api/v1/campaigns/{id}` - Get campaign details
- `GET /api/v1/campaigns/{id}/progress` - Get campaign progress

#### Funding
- `POST /api/v1/campaigns/{id}/fund` - Fund a campaign
- `GET /api/v1/campaigns/{id}/backers` - Get campaign backers

#### Milestones
- `POST /api/v1/campaigns/{id}/milestones/{index}/proof` - Submit milestone proof
- `GET /api/v1/campaigns/{id}/milestones/{index}` - Get milestone details
- `GET /api/v1/campaigns/{id}/milestones` - Get all campaign milestones

#### Voting
- `POST /api/v1/campaigns/{id}/milestones/{index}/vote` - Vote on milestone
- `GET /api/v1/campaigns/{id}/milestones/{index}/votes` - Get milestone votes

## Smart Contract Integration

### Campaign Contract
The campaign contract handles:
- Fund collection and distribution
- Milestone-based payment releases
- Backer management
- Voting mechanisms

### NFT Contract
The NFT contract provides:
- Tiered NFT rewards for backers
- Transferable tokens representing contributions
- Metadata storage on IPFS

## Development

### Running Tests
```bash
pytest
```

### Code Formatting
```bash
black .
isort .
```

### API Documentation
Visit `http://localhost:8000/docs` for interactive API documentation.

## Deployment

### Docker
```dockerfile
FROM python:3.9-slim

WORKDIR /app
COPY requirements.txt .
RUN pip install -r requirements.txt

COPY . .
EXPOSE 8000

CMD ["uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "8000"]
```

### Production Considerations
- Use environment-specific configuration
- Implement rate limiting
- Add comprehensive logging
- Set up monitoring and alerts
- Use HTTPS in production
- Implement proper error handling

## Contributing

1. Fork the repository
2. Create a feature branch
3. Make your changes
4. Add tests
5. Submit a pull request

## License

MIT License - see LICENSE file for details

## Support

For questions and support:
- Create an issue on GitHub
- Check the API documentation at `/docs`
- Review the code comments for implementation details