from sqlmodel import SQLModel, Field
from sqlalchemy import Column, Text
from datetime import datetime
from typing import Optional
from uuid import UUID

class DashboardPlaylist(SQLModel, table=True):
    """Database model for storing dashboard playlist data"""
    
    __tablename__ = "dashboard_playlists"
    
    id: Optional[int] = Field(default=None, primary_key=True)
    user_id: UUID = Field(foreign_key="users.id", index=True)
    playlist_id: str = Field(max_length=100, index=True)
    
    # Playlist Info
    title: str = Field(max_length=255)
    description: str = Field(sa_column=Column(Text), default="")
    playlist_url: str = Field(max_length=500)
    embed_html: str = Field(sa_column=Column(Text), default="")
    embed_url: str = Field(max_length=500, default="")
    playlist_type: str = Field(max_length=50, default="")
    is_editable: bool = Field(default=True)
    is_public: bool = Field(default=True)
    is_unlisted: bool = Field(default=False)
    is_private: bool = Field(default=False)
    
    # Thumbnails
    default_thumbnail: str = Field(max_length=500, default="")
    high_thumbnail: str = Field(max_length=500, default="")
    maxres_thumbnail: str = Field(max_length=500, default="")
    standard_thumbnail: str = Field(max_length=500, default="")
    
    # Content Details
    item_count: int = Field(default=0)
    video_count: int = Field(default=0)
    published_at: datetime = Field(default_factory=datetime.utcnow)
    channel_id: str = Field(max_length=100)
    channel_title: str = Field(max_length=255)
    
    # Analytics Data (JSON fields for complex data)
    analytics: str = Field(sa_column=Column(Text), default="{}")  # JSON string containing all analytics
    
    # Timestamps
    data_created_at: datetime = Field(default_factory=datetime.utcnow)
    data_updated_at: datetime = Field(default_factory=datetime.utcnow)
    
    class Config:
        arbitrary_types_allowed = True
