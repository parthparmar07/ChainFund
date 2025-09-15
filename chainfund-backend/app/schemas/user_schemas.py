from typing import Optional
from pydantic import BaseModel, EmailStr


class UserRegisterRequest(BaseModel):
    wallet_address: str
    email: Optional[EmailStr] = None


class UserResponse(BaseModel):
    id: str
    wallet_address: str
    email: Optional[EmailStr] = None
    created_at: str
    updated_at: str


class AuthRequest(BaseModel):
    wallet_address: str
    signature: str
    message: str


class AuthResponse(BaseModel):
    access_token: str
    token_type: str
    user: UserResponse