from pydantic import BaseModel, EmailStr, Field, field_validator
from typing import Optional
import re


class RegisterRequest(BaseModel):
    """Schema for user registration"""
    email: EmailStr
    password: str = Field(..., min_length=8)
    first_name: str = Field(..., min_length=1)
    last_name: str = Field(..., min_length=1)
    company_name: str = Field(..., min_length=1)

    @field_validator('password')
    @classmethod
    def validate_password(cls, v):
        """Validate password strength"""
        if len(v) < 8:
            raise ValueError('Password must be at least 8 characters long')
        if not re.search(r'[A-Za-z]', v):
            raise ValueError('Password must contain at least one letter')
        if not re.search(r'\d', v):
            raise ValueError('Password must contain at least one digit')
        return v


class LoginRequest(BaseModel):
    """Schema for user login"""
    email: EmailStr
    password: str


class TokenResponse(BaseModel):
    """Schema for token response"""
    access_token: str
    token_type: str = "bearer"


class AuthResponse(BaseModel):
    """Schema for authentication response"""
    success: bool
    data: dict
    message: str


class UserResponse(BaseModel):
    """Schema for user info in auth responses"""
    id: str
    email: str
    first_name: str
    last_name: str
    organization_id: str
    is_active: bool


class OrganizationResponse(BaseModel):
    """Schema for organization info in auth responses"""
    id: str
    name: str
    slug: str
    email: str
    country: str
    currency: str
