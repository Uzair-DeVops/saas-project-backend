from sqlmodel import SQLModel, Field
from sqlalchemy import Column, Text
from datetime import datetime
from typing import Optional
from uuid import UUID

class DashboardOverview(SQLModel, table=True):
    """Database model for storing dashboard overview data"""
    
    __tablename__ = "dashboard_overview"
    
    id: Optional[int] = Field(default=None, primary_key=True)
    user_id: UUID = Field(foreign_key="users.id", index=True)
    
    # Channel Info
    channel_title: str = Field(max_length=255)
    channel_description: str = Field(sa_column=Column(Text))
    subscriber_count: int = Field(default=0)
    total_views: int = Field(default=0)
    total_videos: int = Field(default=0)
    total_likes: int = Field(default=0)
    total_comments: int = Field(default=0)
    total_duration: int = Field(default=0)
    created_at: datetime = Field(default_factory=datetime.utcnow)
    thumbnail_url: str = Field(max_length=500)
    country: str = Field(max_length=100, default="")
    custom_url: str = Field(max_length=100, default="")
    keywords: str = Field(sa_column=Column(Text), default="")
    featured_channels_title: str = Field(max_length=255, default="")
    featured_channels_urls: str = Field(sa_column=Column(Text), default="[]")  # JSON array as string
    
    # Performance Metrics
    avg_views_per_video: float = Field(default=0.0)
    avg_likes_per_video: float = Field(default=0.0)
    avg_comments_per_video: float = Field(default=0.0)
    avg_duration_per_video: float = Field(default=0.0)
    overall_engagement_rate: float = Field(default=0.0)
    videos_per_month: float = Field(default=0.0)
    views_per_month: float = Field(default=0.0)
    subscribers_per_month: float = Field(default=0.0)
    days_since_created: int = Field(default=0)
    channel_age_months: float = Field(default=0.0)
    
    # Recent Performance
    recent_videos_count: int = Field(default=0)
    recent_views: int = Field(default=0)
    recent_likes: int = Field(default=0)
    recent_comments: int = Field(default=0)
    recent_engagement_rate: float = Field(default=0.0)
    recent_avg_views: float = Field(default=0.0)
    
    # Top Performing Content (JSON fields for complex data)
    top_performing_content: str = Field(sa_column=Column(Text), default="{}")  # JSON string
    
    # Monthly Analytics (JSON field for complex data)
    monthly_analytics: str = Field(sa_column=Column(Text), default="{}")  # JSON string
    
    # Content Analysis (JSON field for complex data)
    content_analysis: str = Field(sa_column=Column(Text), default="{}")  # JSON string
    
    # Channel Status
    is_active: bool = Field(default=True)
    engagement_level: str = Field(max_length=50, default="Low")
    growth_stage: str = Field(max_length=50, default="New")
    content_quality: str = Field(max_length=50, default="Low")
    upload_consistency: str = Field(max_length=50, default="Low")
    
    # Summary Stats
    total_watch_time_hours: float = Field(default=0.0)
    avg_video_length_minutes: float = Field(default=0.0)
    total_interactions: int = Field(default=0)
    interaction_rate: float = Field(default=0.0)
    subscriber_to_view_ratio: float = Field(default=0.0)
    
    # Growth Insights
    subscriber_growth_rate: float = Field(default=0.0)
    view_growth_rate: float = Field(default=0.0)
    video_upload_frequency: float = Field(default=0.0)
    engagement_growth: float = Field(default=0.0)
    
    # Advanced Analytics (JSON field for complex data)
    advanced_analytics: str = Field(sa_column=Column(Text), default="{}")  # JSON string
    
    # Performance Scoring (JSON field for complex data)
    performance_scoring: str = Field(sa_column=Column(Text), default="{}")  # JSON string
    
    # Weekly Analytics (JSON field for complex data)
    weekly_analytics: str = Field(sa_column=Column(Text), default="{}")  # JSON string
    
    # Content Insights (JSON field for complex data)
    content_insights: str = Field(sa_column=Column(Text), default="{}")  # JSON string
    
    # Competitive Analysis
    channel_health_score: float = Field(default=0.0)
    growth_potential: str = Field(max_length=50, default="Low")
    audience_loyalty: str = Field(max_length=50, default="Low")
    content_consistency: str = Field(max_length=50, default="Low")
    
    # Enhanced Channel Info (JSON fields for complex data)
    enhanced_channel_info: str = Field(sa_column=Column(Text), default="{}")  # JSON string
    monetization_data: str = Field(sa_column=Column(Text), default="{}")  # JSON string
    audience_insights: str = Field(sa_column=Column(Text), default="{}")  # JSON string
    seo_metrics: str = Field(sa_column=Column(Text), default="{}")  # JSON string
    content_strategy: str = Field(sa_column=Column(Text), default="{}")  # JSON string
    technical_metrics: str = Field(sa_column=Column(Text), default="{}")  # JSON string
    business_metrics: str = Field(sa_column=Column(Text), default="{}")  # JSON string
    
    # Timestamps
    data_created_at: datetime = Field(default_factory=datetime.utcnow)
    data_updated_at: datetime = Field(default_factory=datetime.utcnow)
    
    class Config:
        arbitrary_types_allowed = True
