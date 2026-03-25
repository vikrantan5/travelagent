from pydantic import BaseModel, EmailStr
from typing import Optional
from datetime import datetime


class UserCreate(BaseModel):
    """Model for user registration"""
    email: EmailStr
    password: str
    name: str


class UserLogin(BaseModel):
    """Model for user login"""
    email: EmailStr
    password: str


class UserResponse(BaseModel):
    """Model for user response (without password)"""
    id: str
    email: str
    name: str
    created_at: datetime
    subscription_type: str = "free"
    has_used_free_planner: bool = False
    total_planners_created: int = 0
    is_premium: bool = False


class TokenResponse(BaseModel):
    """Model for token response"""
    access_token: str
    token_type: str = "bearer"
    user: UserResponse
