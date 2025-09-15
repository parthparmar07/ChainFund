import os
from typing import List
from pydantic_settings import BaseSettings
from dotenv import load_dotenv

load_dotenv()


class Settings(BaseSettings):
    # MongoDB Configuration
    mongodb_url: str = "mongodb://localhost:27017"
    database_name: str = "chainfund_lite"

    # BNB Chain Configuration
    bnb_rpc_url: str = "https://bsc-dataseed1.binance.org/"
    private_key: str = ""
    chain_id: int = 56

    # IPFS Configuration
    pinata_api_key: str = ""
    pinata_secret_key: str = ""
    web3_storage_token: str = ""

    # JWT Configuration
    jwt_secret_key: str = "your-secret-key-change-in-production"
    jwt_algorithm: str = "HS256"
    access_token_expire_minutes: int = 30

    # CORS Configuration - Using List directly
    allowed_origins: List[str] = [
        "http://localhost:3000",
        "http://localhost:8080", 
        "http://127.0.0.1:3000",
        "http://127.0.0.1:8080"
    ]

    # Contract Addresses
    campaign_factory_address: str = ""
    nft_contract_address: str = ""

    class Config:
        env_file = ".env"


settings = Settings()