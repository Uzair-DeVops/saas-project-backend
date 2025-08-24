from typing import List, Dict, Any
from uuid import UUID
from fastapi import APIRouter, HTTPException, Depends, Path
from sqlmodel import Session
from pydantic import BaseModel

from ..controllers.dashboard_controller import (
    get_playlists_controller,
    get_playlist_videos_controller,
    get_playlist_analytics_controller,
    get_all_user_videos_controller,
    get_video_details_controller
)
from ..utils.database_dependency import get_database_session
from ..controllers.user_controller import get_current_user
from ..models.user_model import UserSignUp
from ..utils.my_logger import get_logger

logger = get_logger("DASHBOARD_ROUTES")

router = APIRouter(prefix="/dashboard", tags=["dashboard"])

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

@router.get("/playlists", response_model=PlaylistsResponse)
async def get_dashboard_playlists(
    current_user: UserSignUp = Depends(get_current_user),
    db: Session = Depends(get_database_session)
) -> PlaylistsResponse:
    """
    Get all playlists for dashboard with enhanced metadata.
    
    This endpoint provides a comprehensive list of all user's playlists
    with additional statistics like total views, likes, comments, and more.
    
    Args:
        current_user: The authenticated user from JWT token
        db: Database session dependency
    
    Returns:
        PlaylistsResponse: List of playlists with enhanced metadata
        
    Raises:
        HTTPException: If error occurs
    """
    try:
        logger.info(f"Dashboard playlists request received for user_id: {current_user.id}")
        
        # Get playlists with enhanced data
        playlists = get_playlists_controller(current_user.id, db)
        
        return PlaylistsResponse(
            success=True,
            message=f"Successfully retrieved {len(playlists)} playlists",
            data=playlists,
            count=len(playlists)
        )
        
    except HTTPException:
        # Re-raise HTTP exceptions as they are already properly formatted
        raise
    except Exception as e:
        logger.error(f"Unexpected error in get_dashboard_playlists route for user_id {current_user.id}: {e}")
        raise HTTPException(
            status_code=500,
            detail="Internal server error while retrieving playlists"
        )

@router.get("/videos", response_model=VideosResponse)
async def get_dashboard_videos(
    current_user: UserSignUp = Depends(get_current_user),
    db: Session = Depends(get_database_session)
) -> VideosResponse:
    """
    Get all videos for dashboard with detailed analytics.
    
    This endpoint provides comprehensive information about all user's videos
    including views, likes, comments, engagement rates, and performance scores.
    
    Args:
        current_user: The authenticated user from JWT token
        db: Database session dependency
    
    Returns:
        VideosResponse: List of all videos with detailed analytics
        
    Raises:
        HTTPException: If error occurs
    """
    try:
        logger.info(f"Dashboard videos request received for user_id: {current_user.id}")
        
        # Get all videos with analytics
        videos = get_all_user_videos_controller(current_user.id, db)
        
        return VideosResponse(
            success=True,
            message=f"Successfully retrieved {len(videos)} videos",
            data=videos,
            count=len(videos)
        )
        
    except HTTPException:
        # Re-raise HTTP exceptions as they are already properly formatted
        raise
    except Exception as e:
        logger.error(f"Unexpected error in get_dashboard_videos route for user_id {current_user.id}: {e}")
        raise HTTPException(
            status_code=500,
            detail="Internal server error while retrieving videos"
        )

@router.get("/videos/{video_id}", response_model=VideoDetailResponse)
async def get_dashboard_video_details(
    video_id: str = Path(..., description="The YouTube video ID"),
    current_user: UserSignUp = Depends(get_current_user),
    db: Session = Depends(get_database_session)
) -> VideoDetailResponse:
    """
    Get detailed analytics for a specific video.
    
    This endpoint provides comprehensive analytics for a single video including:
    - View count, like count, comment count
    - Engagement rate and performance score
    - Video metadata (title, description, duration, etc.)
    - Publishing information
    - Privacy status and category
    
    Args:
        video_id: The YouTube video ID
        current_user: The authenticated user from JWT token
        db: Database session dependency
    
    Returns:
        VideoDetailResponse: Detailed video analytics
        
    Raises:
        HTTPException: If error occurs
    """
    try:
        logger.info(f"Dashboard video details request received for video_id: {video_id}, user_id: {current_user.id}")
        
        # Get detailed video analytics
        video_details = get_video_details_controller(current_user.id, video_id, db)
        
        if not video_details:
            raise HTTPException(
                status_code=404,
                detail="Video not found or you don't have permission to access it"
            )
        
        return VideoDetailResponse(
            success=True,
            message=f"Successfully retrieved details for video: {video_details.get('title', 'Unknown')}",
            data=video_details
        )
        
    except HTTPException:
        # Re-raise HTTP exceptions as they are already properly formatted
        raise
    except Exception as e:
        logger.error(f"Unexpected error in get_dashboard_video_details route for video_id {video_id}, user_id {current_user.id}: {e}")
        raise HTTPException(
            status_code=500,
            detail="Internal server error while retrieving video details"
        )

@router.get("/playlists/{playlist_id}/videos", response_model=VideosResponse)
async def get_dashboard_playlist_videos(
    playlist_id: str = Path(..., description="The YouTube playlist ID"),
    current_user: UserSignUp = Depends(get_current_user),
    db: Session = Depends(get_database_session)
) -> VideosResponse:
    """
    Get all videos in a playlist with detailed analytics for dashboard.
    
    This endpoint provides comprehensive information about each video in a playlist
    including views, likes, comments, engagement rates, and performance scores.
    
    Args:
        playlist_id: The YouTube playlist ID
        current_user: The authenticated user from JWT token
        db: Database session dependency
    
    Returns:
        VideosResponse: List of videos with detailed analytics
        
    Raises:
        HTTPException: If error occurs
    """
    try:
        logger.info(f"Dashboard playlist videos request received for playlist_id: {playlist_id}, user_id: {current_user.id}")
        
        # Get videos with analytics
        videos = get_playlist_videos_controller(current_user.id, playlist_id, db)
        
        return VideosResponse(
            success=True,
            message=f"Successfully retrieved {len(videos)} videos from playlist",
            data=videos,
            count=len(videos)
        )
        
    except HTTPException:
        # Re-raise HTTP exceptions as they are already properly formatted
        raise
    except Exception as e:
        logger.error(f"Unexpected error in get_dashboard_playlist_videos route for playlist_id {playlist_id}, user_id {current_user.id}: {e}")
        raise HTTPException(
            status_code=500,
            detail="Internal server error while retrieving playlist videos"
        )

@router.get("/playlists/{playlist_id}/analytics", response_model=AnalyticsResponse)
async def get_dashboard_playlist_analytics(
    playlist_id: str = Path(..., description="The YouTube playlist ID"),
    current_user: UserSignUp = Depends(get_current_user),
    db: Session = Depends(get_database_session)
) -> AnalyticsResponse:
    """
    Get comprehensive analytics for all videos in a playlist.
    
    This endpoint provides detailed analytics including:
    - Total views, likes, comments across all videos
    - Average engagement rates
    - Top performing videos
    - Performance summaries
    - Best and worst performing videos
    
    Args:
        playlist_id: The YouTube playlist ID
        current_user: The authenticated user from JWT token
        db: Database session dependency
    
    Returns:
        AnalyticsResponse: Comprehensive analytics data
        
    Raises:
        HTTPException: If error occurs
    """
    try:
        logger.info(f"Dashboard playlist analytics request received for playlist_id: {playlist_id}, user_id: {current_user.id}")
        
        # Get comprehensive analytics
        analytics = get_playlist_analytics_controller(current_user.id, playlist_id, db)
        
        return AnalyticsResponse(
            success=True,
            message=f"Successfully generated analytics for playlist with {analytics.get('total_videos', 0)} videos",
            data=analytics
        )
        
    except HTTPException:
        # Re-raise HTTP exceptions as they are already properly formatted
        raise
    except Exception as e:
        logger.error(f"Unexpected error in get_dashboard_playlist_analytics route for playlist_id {playlist_id}, user_id {current_user.id}: {e}")
        raise HTTPException(
            status_code=500,
            detail="Internal server error while generating analytics"
        )

@router.get("/overview", response_model=DashboardResponse)
async def get_dashboard_overview(
    current_user: UserSignUp = Depends(get_current_user),
    db: Session = Depends(get_database_session)
) -> DashboardResponse:
    """
    Get dashboard overview with summary statistics.
    
    This endpoint provides a high-level overview of the user's YouTube channel
    including total playlists, total videos, overall performance metrics, etc.
    
    Args:
        current_user: The authenticated user from JWT token
        db: Database session dependency
    
    Returns:
        DashboardResponse: Dashboard overview data
        
    Raises:
        HTTPException: If error occurs
    """
    try:
        logger.info(f"Dashboard overview request received for user_id: {current_user.id}")
        
        # Get playlists for overview
        playlists = get_playlists_controller(current_user.id, db)
        
        # Calculate overview statistics
        total_playlists = len(playlists)
        total_videos = sum(playlist.get('total_videos', 0) for playlist in playlists)
        total_views = sum(playlist.get('total_views', 0) for playlist in playlists)
        total_likes = sum(playlist.get('total_likes', 0) for playlist in playlists)
        total_comments = sum(playlist.get('total_comments', 0) for playlist in playlists)
        
        # Calculate averages
        average_views_per_playlist = total_views / total_playlists if total_playlists > 0 else 0
        average_videos_per_playlist = total_videos / total_playlists if total_playlists > 0 else 0
        
        overview_data = {
            'total_playlists': total_playlists,
            'total_videos': total_videos,
            'total_views': total_views,
            'total_likes': total_likes,
            'total_comments': total_comments,
            'average_views_per_playlist': round(average_views_per_playlist, 2),
            'average_videos_per_playlist': round(average_videos_per_playlist, 2),
            'top_playlists': sorted(playlists, key=lambda x: x.get('total_views', 0), reverse=True)[:5],
            'recent_playlists': sorted(playlists, key=lambda x: x.get('last_updated') or '', reverse=True)[:5]
        }
        
        return DashboardResponse(
            success=True,
            message=f"Dashboard overview generated successfully",
            data=overview_data
        )
        
    except HTTPException:
        # Re-raise HTTP exceptions as they are already properly formatted
        raise
    except Exception as e:
        logger.error(f"Unexpected error in get_dashboard_overview route for user_id {current_user.id}: {e}")
        raise HTTPException(
            status_code=500,
            detail="Internal server error while generating dashboard overview"
        ) 