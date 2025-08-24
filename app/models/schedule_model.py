from pydantic import BaseModel, Field, validator
from typing import Optional
from enum import Enum
from datetime import datetime, timedelta
from uuid import UUID

class PrivacyStatus(str, Enum):
    """Privacy status options for scheduled videos"""
    PRIVATE = "private"
    PUBLIC = "public"
    UNLISTED = "unlisted"

class ScheduleRequest(BaseModel):
    """Request model for scheduling a video"""
    schedule_date: str = Field(..., description="Schedule date in YYYY-MM-DD format")
    schedule_time: str = Field(..., description="Schedule time in HH:MM format (24-hour)")
    privacy_status: PrivacyStatus = Field(..., description="Privacy status for the scheduled video")
    
    @validator('schedule_date')
    def validate_date(cls, v):
        try:
            datetime.strptime(v, '%Y-%m-%d')
            return v
        except ValueError:
            raise ValueError('Date must be in YYYY-MM-DD format')
    
    @validator('schedule_time')
    def validate_time(cls, v):
        try:
            datetime.strptime(v, '%H:%M')
            return v
        except ValueError:
            raise ValueError('Time must be in HH:MM format (24-hour)')
    
    def get_schedule_datetime(self) -> str:
        """Convert date and time to ISO datetime string"""
        datetime_str = f"{self.schedule_date} {self.schedule_time}:00"
        schedule_dt = datetime.strptime(datetime_str, '%Y-%m-%d %H:%M:%S')
        
        # Check if time is in the future
        if schedule_dt <= datetime.now():
            raise ValueError('Schedule time must be in the future')
        
        # Format as ISO string with timezone
        return schedule_dt.isoformat()

class ScheduleResponse(BaseModel):
    """Response model for scheduling"""
    success: bool
    message: str
    data: dict

class ScheduleInfo(BaseModel):
    """Schedule information model"""
    video_id: UUID
    schedule_datetime: str
    privacy_status: str
    video_status: str
    formatted_schedule: str
    time_until_schedule: str 