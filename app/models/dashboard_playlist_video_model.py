from sqlmodel import SQLModel, Field
from datetime import datetime
from typing import Optional
from uuid import UUID

class DashboardPlaylistVideo(SQLModel, table=True):
    """Database model for storing playlist-video relationships"""
    
    __tablename__ = "dashboard_playlist_videos"
    
    id: Optional[int] = Field(default=None, primary_key=True)
    user_id: UUID = Field(foreign_key="users.id", index=True)
    playlist_id: str = Field(max_length=100, index=True)
    video_id: str = Field(max_length=100, index=True)
    
    # Position in playlist
    position: int = Field(default=0)
    
    # Timestamps
    data_created_at: datetime = Field(default_factory=datetime.utcnow)
    data_updated_at: datetime = Field(default_factory=datetime.utcnow)
    
    class Config:
        arbitrary_types_allowed = True
