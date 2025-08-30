from typing import List, Dict, Any
from uuid import UUID
from fastapi import APIRouter, HTTPException, Depends, Path
from sqlmodel import Session
from pydantic import BaseModel
import json

from ..utils.database_dependency import get_database_session
from ..controllers.user_controller import get_current_user
from ..models.user_model import UserSignUp
from ..utils.my_logger import get_logger
from ..services.smart_dashboard_service import SmartDashboardService
from fastapi import Query

logger = get_logger("DASHBOARD_ROUTES")

router = APIRouter(prefix="/dashboard", tags=["dashboard-get"])

# Response models
class DashboardResponse(BaseModel):
    """Response model for dashboard operations"""
    success: bool
    message: str
    data: Dict[str, Any]

class PlaylistsResponse(BaseModel):
    """Response model for playlists"""
    success: bool
    message: str
    data: List[Dict[str, Any]]
    count: int

class VideosResponse(BaseModel):
    """Response model for videos"""
    success: bool
    message: str
    data: List[Dict[str, Any]]
    count: int

class VideoDetailResponse(BaseModel):
    """Response model for individual video details"""
    success: bool
    message: str
    data: Dict[str, Any]

class AnalyticsResponse(BaseModel):
    """Response model for analytics"""
    success: bool
    message: str
    data: Dict[str, Any]



@router.get("/overview", response_model=DashboardResponse)
async def get_dashboard_overview(
    refresh: bool = Query(False, description="Force refresh data from YouTube"),
    current_user: UserSignUp = Depends(get_current_user),
    db: Session = Depends(get_database_session)
) -> DashboardResponse:
    """
    Get dashboard overview data with persistent caching.
    
    This endpoint intelligently handles data retrieval:
    - If no data exists: Fetches from YouTube and stores in database
    - If cached data exists: Returns cached data (fast response, persists until refresh)
    - If refresh=true: Forces fresh data from YouTube and updates cache
    
    Cache persists until user explicitly requests refresh - no automatic expiration.
    
    Args:
        refresh: Force refresh data from YouTube (default: false)
        current_user: The authenticated user from JWT token
        db: Database session dependency
    
    Returns:
        DashboardResponse: Overview data with cache information
        
    Raises:
        HTTPException: If error occurs
    """
    try:
        logger.info(f"Smart overview request for user_id: {current_user.id}, refresh: {refresh}")
        
        result = SmartDashboardService.get_overview_data(current_user.id, db, refresh)
        
        return DashboardResponse(
            success=result["success"],
            message=result["message"],
            data=result["data"]
        )
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Unexpected error in smart overview route for user_id {current_user.id}: {e}")
        raise HTTPException(
            status_code=500,
            detail="Internal server error while getting overview data"
        )


@router.get("/videos", response_model=VideosResponse)
async def get_dashboard_videos(
    refresh: bool = Query(False, description="Force refresh data from YouTube"),
    current_user: UserSignUp = Depends(get_current_user),
    db: Session = Depends(get_database_session)
) -> VideosResponse:
    """
    Get all videos with persistent caching.
    
    This endpoint intelligently handles data retrieval:
    - If no data exists: Fetches from YouTube and stores in database
    - If cached data exists: Returns cached data (fast response, persists until refresh)
    - If refresh=true: Forces fresh data from YouTube and updates cache
    
    Cache persists until user explicitly requests refresh - no automatic expiration.
    
    Args:
        refresh: Force refresh data from YouTube (default: false)
        current_user: The authenticated user from JWT token
        db: Database session dependency
    
    Returns:
        VideosResponse: List of videos with cache information
        
    Raises:
        HTTPException: If error occurs
    """
    try:
        logger.info(f"Smart videos request for user_id: {current_user.id}, refresh: {refresh}")
        
        result = SmartDashboardService.get_videos_data(current_user.id, db, refresh)
        
        return VideosResponse(
            success=result["success"],
            message=result["message"],
            data=result["data"],
            count=result.get("count", 0)
        )
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Unexpected error in smart videos route for user_id {current_user.id}: {e}")
        raise HTTPException(
            status_code=500,
            detail="Internal server error while getting videos data"
        )


@router.get("/videos/{video_id}", response_model=VideoDetailResponse)
async def get_dashboard_video(
    video_id: str = Path(..., description="The YouTube video ID"),
    refresh: bool = Query(False, description="Force refresh data from YouTube"),
    current_user: UserSignUp = Depends(get_current_user),
    db: Session = Depends(get_database_session)
) -> VideoDetailResponse:
    """
    Get specific video data with smart caching.
    
    This endpoint intelligently handles data retrieval:
    - If no data exists: Fetches from YouTube and stores in database
    - If cached data exists: Returns cached data (fast response)
    - If refresh=true: Forces fresh data from YouTube
    
    Args:
        video_id: The YouTube video ID
        refresh: Force refresh data from YouTube (default: false)
        current_user: The authenticated user from JWT token
        db: Database session dependency
    
    Returns:
        VideoDetailResponse: Video data with cache information
        
    Raises:
        HTTPException: If error occurs
    """
    try:
        logger.info(f"Smart video request for user_id: {current_user.id}, video_id: {video_id}, refresh: {refresh}")
        
        result = SmartDashboardService.get_video_data(current_user.id, video_id, db, refresh)
        
        return VideoDetailResponse(
            success=result["success"],
            message=result["message"],
            data=result["data"]
        )
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Unexpected error in smart video route for user_id {current_user.id}, video_id {video_id}: {e}")
        raise HTTPException(
            status_code=500,
            detail="Internal server error while getting video data"
        )

@router.get("/playlists/{playlist_id}/comprehensive", response_model=AnalyticsResponse)
async def get_dashboard_playlist_comprehensive(
    playlist_id: str = Path(..., description="The YouTube playlist ID"),
    refresh: bool = Query(False, description="Force refresh data from YouTube"),
    current_user: UserSignUp = Depends(get_current_user),
    db: Session = Depends(get_database_session)
) -> AnalyticsResponse:
    """
    Get comprehensive analytics for a specific playlist with persistent caching.
    
    This endpoint intelligently handles data retrieval:
    - If no data exists: Fetches from YouTube and stores in database
    - If cached data exists: Returns cached data (fast response, persists until refresh)
    - If refresh=true: Forces fresh data from YouTube and updates cache
    
    Cache persists until user explicitly requests refresh - no automatic expiration.
    
    This endpoint provides extremely detailed analytics for a single playlist including:
    - Complete playlist information and metadata
    - All videos with detailed analytics
    - Performance metrics and distributions
    - Content analysis and growth insights
    - Top performing videos by multiple criteria
    - Playlist health assessment
    - Recent activity analysis
    - Duration and engagement distributions
    - Content recommendations
    
    Args:
        playlist_id: The YouTube playlist ID
        refresh: Force refresh data from YouTube (default: false)
        current_user: The authenticated user from JWT token
        db: Database session dependency
    
    Returns:
        AnalyticsResponse: Comprehensive playlist analytics data with cache information
        
    Raises:
        HTTPException: If error occurs
    """
    try:
        logger.info(f"Smart playlist comprehensive request for user_id: {current_user.id}, playlist_id: {playlist_id}, refresh: {refresh}")
        
        result = SmartDashboardService.get_playlist_data(current_user.id, playlist_id, db, refresh)
        
        return AnalyticsResponse(
            success=result["success"],
            message=result["message"],
            data=result["data"]
        )
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Unexpected error in smart playlist comprehensive route for user_id {current_user.id}, playlist_id {playlist_id}: {e}")
        raise HTTPException(
            status_code=500,
            detail="Internal server error while getting playlist comprehensive data"
        )


@router.get("/playlists/{playlist_id}/videos", response_model=VideosResponse)
async def get_dashboard_playlist_videos(
    playlist_id: str = Path(..., description="The YouTube playlist ID"),
    refresh: bool = Query(False, description="Force refresh data from YouTube"),
    current_user: UserSignUp = Depends(get_current_user),
    db: Session = Depends(get_database_session)
) -> VideosResponse:
    """
    Get all videos in a playlist with detailed analytics and persistent caching.
    
    This endpoint intelligently handles data retrieval:
    - If no data exists: Fetches from YouTube and stores in database
    - If cached data exists: Returns cached data (fast response, persists until refresh)
    - If refresh=true: Forces fresh data from YouTube and updates cache
    
    Cache persists until user explicitly requests refresh - no automatic expiration.
    
    This endpoint provides comprehensive information about each video in a playlist
    including views, likes, comments, engagement rates, and performance scores.
    
    Args:
        playlist_id: The YouTube playlist ID
        refresh: Force refresh data from YouTube (default: false)
        current_user: The authenticated user from JWT token
        db: Database session dependency
    
    Returns:
        VideosResponse: List of videos with detailed analytics and cache information
        
    Raises:
        HTTPException: If error occurs
    """
    try:
        logger.info(f"Smart playlist videos request for user_id: {current_user.id}, playlist_id: {playlist_id}, refresh: {refresh}")
        
        result = SmartDashboardService.get_playlist_videos_data(current_user.id, playlist_id, db, refresh)
        
        return VideosResponse(
            success=result["success"],
            message=result["message"],
            data=result["data"],
            count=result.get("count", 0)
        )
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Unexpected error in smart playlist videos route for user_id {current_user.id}, playlist_id {playlist_id}: {e}")
        raise HTTPException(
            status_code=500,
            detail="Internal server error while getting playlist videos data"
        )
