from sqlmodel import SQLModel, Field
from sqlalchemy import Column, Text
from datetime import datetime
from typing import Optional
from uuid import UUID

class DashboardVideo(SQLModel, table=True):
    """Database model for storing dashboard video data"""
    
    __tablename__ = "dashboard_videos"
    
    id: Optional[int] = Field(default=None, primary_key=True)
    user_id: UUID = Field(foreign_key="users.id", index=True)
    video_id: str = Field(max_length=100, index=True)
    
    # Video Info
    title: str = Field(max_length=255)
    description: str = Field(sa_column=Column(Text), default="")
    thumbnail_url: str = Field(max_length=500, default="")
    published_at: datetime = Field(default_factory=datetime.utcnow)
    duration: str = Field(max_length=50, default="")
    duration_seconds: int = Field(default=0)
    
    # Channel Info
    channel_id: str = Field(max_length=100)
    channel_title: str = Field(max_length=255)
    
    # Statistics
    view_count: int = Field(default=0)
    like_count: int = Field(default=0)
    comment_count: int = Field(default=0)
    
    # Status
    privacy_status: str = Field(max_length=50, default="public")
    upload_status: str = Field(max_length=50, default="processed")
    license: str = Field(max_length=50, default="youtube")
    made_for_kids: bool = Field(default=False)
    
    # Category and Tags
    category_id: str = Field(max_length=50, default="")
    tags: str = Field(sa_column=Column(Text), default="[]")  # JSON array string
    default_language: str = Field(max_length=10, default="")
    default_audio_language: str = Field(max_length=10, default="")
    
    # Analytics Data (JSON fields for complex data)
    analytics: str = Field(sa_column=Column(Text), default="{}")  # JSON string containing all analytics
    
    # Timestamps
    data_created_at: datetime = Field(default_factory=datetime.utcnow)
    data_updated_at: datetime = Field(default_factory=datetime.utcnow)
    
    class Config:
        arbitrary_types_allowed = True
