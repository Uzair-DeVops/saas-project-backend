from pydantic import BaseModel, Field
from typing import Optional
from datetime import datetime
from uuid import UUID

class CompleteVideoDetails(BaseModel):
    """Complete video details that will be uploaded to YouTube"""
    video_id: UUID
    title: Optional[str] = Field(description="Generated video title")
    description_with_timestamps: Optional[str] = Field(description="Description merged with timestamps")
    thumbnail_path: Optional[str] = Field(description="Local thumbnail file path")
    thumbnail_url: Optional[str] = Field(description="Original thumbnail URL")
    video_path: str = Field(description="Path to stored video file")
    youtube_video_id: Optional[str] = Field(description="YouTube video ID (if already uploaded)")
    created_at: datetime = Field(description="When the video was created")
    
    # Separate fields for reference
    original_description: Optional[str] = Field(description="Original description without timestamps")
    timestamps: Optional[str] = Field(description="Generated timestamps")
    transcript: Optional[str] = Field(description="Video transcript")

class VideoDetailsResponse(BaseModel):
    """Response model for complete video details"""
    success: bool
    message: str
    data: CompleteVideoDetails

class UpdateVideoDetailsRequest(BaseModel):
    """Request model for updating video details"""
    title: Optional[str] = Field(default=None, description="Updated video title", max_length=200)
    description: Optional[str] = Field(default=None, description="Updated video description")
    timestamps: Optional[str] = Field(default=None, description="Updated timestamps")

class UpdateVideoDetailsResponse(BaseModel):
    """Response model for video details update"""
    success: bool
    message: str
    data: CompleteVideoDetails 