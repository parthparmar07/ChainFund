import hashlib
import hmac
from typing import Optional
from eth_account import Account
from eth_account.messages import encode_defunct


def verify_wallet_signature(wallet_address: str, signature: str, message: str) -> bool:
    """Verify that a signature was created by the specified wallet address"""
    try:
        encoded_message = encode_defunct(text=message)
        recovered_address = Account.recover_message(encoded_message, signature=signature)
        return recovered_address.lower() == wallet_address.lower()
    except Exception as e:
        print(f"Signature verification error: {str(e)}")
        return False


def create_signing_message(wallet_address: str, action: str, timestamp: Optional[str] = None) -> str:
    """Create a standardized message for wallet signing"""
    if not timestamp:
        from datetime import datetime
        timestamp = datetime.utcnow().isoformat()

    message = f"""ChainFund Lite - {action}

Wallet Address: {wallet_address}
Timestamp: {timestamp}

Please sign this message to {action.lower()}."""

    return message


def hash_message(message: str) -> str:
    """Create SHA256 hash of a message"""
    return hashlib.sha256(message.encode('utf-8')).hexdigest()


def validate_wallet_address(wallet_address: str) -> bool:
    """Validate that the provided string is a valid Ethereum address"""
    try:
        return Account.is_address(wallet_address)
    except:
        return False


def normalize_wallet_address(wallet_address: str) -> str:
    """Normalize wallet address to checksum format"""
    try:
        return Account.checksum_address(wallet_address)
    except:
        return wallet_address