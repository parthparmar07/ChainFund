import hashlib
import hmac
from datetime import datetime, timedelta
from typing import Optional
from eth_account import Account
from eth_account.messages import encode_defunct
from jose import JWTError, jwt
from app.config import settings


class AuthService:
    def __init__(self):
        self.secret_key = settings.jwt_secret_key
        self.algorithm = settings.jwt_algorithm
        self.access_token_expire_minutes = settings.access_token_expire_minutes

    def verify_signature(self, wallet_address: str, signature: str, message: str) -> bool:
        """Verify MetaMask signature"""
        try:
            # Encode the message for verification
            encoded_message = encode_defunct(text=message)

            # Recover the address from the signature
            recovered_address = Account.recover_message(encoded_message, signature=signature)

            # Compare with the provided wallet address (case-insensitive)
            return recovered_address.lower() == wallet_address.lower()

        except Exception as e:
            print(f"Signature verification failed: {str(e)}")
            return False

    def create_access_token(self, data: dict) -> str:
        """Create JWT access token"""
        to_encode = data.copy()
        expire = datetime.utcnow() + timedelta(minutes=self.access_token_expire_minutes)
        to_encode.update({"exp": expire})

        encoded_jwt = jwt.encode(to_encode, self.secret_key, algorithm=self.algorithm)
        return encoded_jwt

    def verify_token(self, token: str) -> Optional[dict]:
        """Verify JWT token"""
        try:
            payload = jwt.decode(token, self.secret_key, algorithms=[self.algorithm])
            return payload
        except JWTError:
            return None

    def get_wallet_from_token(self, token: str) -> Optional[str]:
        """Extract wallet address from JWT token"""
        payload = self.verify_token(token)
        if payload:
            return payload.get("sub")
        return None

    def create_auth_message(self, wallet_address: str) -> str:
        """Create a standardized authentication message for signing"""
        timestamp = datetime.utcnow().isoformat()
        message = f"ChainFund Lite Authentication\nWallet: {wallet_address}\nTimestamp: {timestamp}\n\nPlease sign this message to authenticate with ChainFund Lite."
        return message

    def hash_message(self, message: str) -> str:
        """Create a hash of the message for additional security"""
        return hashlib.sha256(message.encode()).hexdigest()

    async def authenticate_user(self, wallet_address: str, signature: str, message: str) -> Optional[dict]:
        """Complete authentication flow"""
        # Verify the signature
        if not self.verify_signature(wallet_address, signature, message):
            return None

        # Create access token
        access_token = self.create_access_token({"sub": wallet_address})

        return {
            "access_token": access_token,
            "token_type": "bearer",
            "wallet_address": wallet_address
        }


# Global instance
auth_service = AuthService()