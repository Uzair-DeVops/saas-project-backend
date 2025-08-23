from datetime import datetime
from sqlmodel import SQLModel, Field
from uuid import UUID, uuid4
from typing import Optional
from sqlalchemy import Column
from sqlalchemy.dialects.mysql import LONGTEXT


class Video(SQLModel, table=True):
    """Simple video model to store video path and video ID"""
    __tablename__ = "videos"
    
    id: UUID = Field(default_factory=uuid4, primary_key=True)
    user_id: UUID = Field(foreign_key="users.id", index=True)
    video_path: str = Field(max_length=500)  # Path to stored video file
    youtube_video_id: Optional[str] = Field(default=None, max_length=50)  # YouTube video ID
    transcript: Optional[str] = Field(default=None, sa_column=Column(LONGTEXT))  # Unlimited transcript
    title: Optional[str] = Field(default=None, max_length=200)  # Generated video title
    timestamps: Optional[str] = Field(default=None, sa_column=Column(LONGTEXT))  # Generated timestamps
    description: Optional[str] = Field(default=None, sa_column=Column(LONGTEXT))  # Generated description
    thumbnail_path: Optional[str] = Field(default=None, max_length=500)  # Local thumbnail file path
    thumbnail_url: Optional[str] = Field(default=None, max_length=1000)  # Original thumbnail URL
    created_at: datetime = Field(default_factory=datetime.utcnow)


class VideoCreate(SQLModel):
    """Video creation model"""
    video_path: str


class VideoResponse(SQLModel):
    """Video response model"""
    id: UUID
    user_id: UUID
    video_path: str
    youtube_video_id: Optional[str] = None
    transcript: Optional[str] = None
    title: Optional[str] = None
    timestamps: Optional[str] = None
    description: Optional[str] = None
    thumbnail_path: Optional[str] = None
    thumbnail_url: Optional[str] = None
    created_at: datetime
