from datetime import datetime
from typing import Optional, List
from sqlmodel import SQLModel, Field, Relationship
from uuid import UUID, uuid4

class UserBase(SQLModel):
    """Base user model with common fields"""
    email: str = Field(unique=True, index=True)
    username: str = Field(unique=True, index=True)
    full_name: str = Field(max_length=100)
    is_active: bool = Field(default=True)
    created_at: datetime = Field(default_factory=datetime.utcnow)
    updated_at: datetime = Field(default_factory=datetime.utcnow)

class UserSignUp(UserBase, table=True):
    """User model for signup with password"""
    __tablename__ = "users"
    
    id: UUID = Field(default_factory=uuid4, primary_key=True)
    password: str
    
class UserSignIn(SQLModel):
    """User model for signin"""
    email: str
    password: str

class UserResponse(UserBase):
    """User response model without sensitive data"""
    id: UUID
