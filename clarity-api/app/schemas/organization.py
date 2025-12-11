from pydantic import BaseModel, EmailStr, ConfigDict
from typing import Optional
from datetime import datetime
from uuid import UUID


class OrganizationBase(BaseModel):
    """Base organization schema"""
    name: str
    country: Optional[str] = "US"
    currency: Optional[str] = "USD"


class OrganizationCreate(OrganizationBase):
    """Schema for creating an organization"""
    pass


class OrganizationUpdate(BaseModel):
    """Schema for updating an organization"""
    name: Optional[str] = None
    country: Optional[str] = None
    currency: Optional[str] = None
    default_gl_account: Optional[str] = None


class OrganizationInDB(OrganizationBase):
    """Organization schema as stored in database"""
    model_config = ConfigDict(from_attributes=True)

    id: UUID
    slug: str
    email: str
    default_gl_account: str
    is_active: bool
    created_at: datetime
    updated_at: datetime


class Organization(OrganizationInDB):
    """Organization schema for API responses"""
    pass
