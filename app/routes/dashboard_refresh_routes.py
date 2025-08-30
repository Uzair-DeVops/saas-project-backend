"""
Dashboard Refresh Routes - Handles refreshing dashboard data
"""
from typing import Dict, Any
from fastapi import APIRouter, HTTPException, Depends, Path
from sqlmodel import Session
from pydantic import BaseModel

from ..controllers.dashboard_refresh_controller import (
    force_refresh_overview_data,
    force_refresh_playlists_data,
    force_refresh_videos_data,
    force_refresh_single_playlist_data,
    force_refresh_single_video_data,
    force_refresh_playlist_videos_data,
    force_refresh_single_playlist_video_data
)
from ..services.dashboard_data_service import DashboardDataService
from ..utils.database_dependency import get_database_session
from ..controllers.user_controller import get_current_user
from ..models.user_model import UserSignUp
from ..utils.my_logger import get_logger

logger = get_logger("DASHBOARD_REFRESH_ROUTES")

router = APIRouter(prefix="/dashboard", tags=["dashboard-refresh"])

# Response models
class RefreshResponse(BaseModel):
    """Response model for refresh operations"""
    success: bool
    message: str
    data: Dict[str, Any] = {}

# Refresh APIs (Delete old data + Fetch new data)
@router.post("/overview/refresh", response_model=RefreshResponse)
async def refresh_dashboard_overview(
    current_user: UserSignUp = Depends(get_current_user),
    db: Session = Depends(get_database_session)
) -> RefreshResponse:
    """
    Refresh overview data by deleting old data and fetching fresh data from YouTube.
    
    This endpoint first deletes existing overview data from the database, then fetches fresh data
    from YouTube API and stores it. This ensures completely fresh data.
    
    Args:
        current_user: The authenticated user from JWT token
        db: Database session dependency
    
    Returns:
        RefreshResponse: Success status and refreshed data
        
    Raises:
        HTTPException: If error occurs during refresh
    """
    try:
        logger.info(f"Refresh overview data request received for user_id: {current_user.id}")
        
        result = force_refresh_overview_data(current_user.id, db)
        
        return RefreshResponse(
            success=result["success"],
            message=f"Overview data refreshed successfully: {result['message']}",
            data=result.get("data", {})
        )
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Unexpected error in refresh_overview_data route for user_id {current_user.id}: {e}")
        raise HTTPException(
            status_code=500,
            detail="Internal server error while refreshing overview data"
        )

@router.post("/playlists/refresh", response_model=RefreshResponse)
async def refresh_dashboard_playlists(
    current_user: UserSignUp = Depends(get_current_user),
    db: Session = Depends(get_database_session)
) -> RefreshResponse:
    """
    Refresh playlists data by deleting old data and fetching fresh data from YouTube.
    
    This endpoint first deletes existing playlists data from the database, then fetches fresh data
    from YouTube API and stores it. This ensures completely fresh data.
    
    Args:
        current_user: The authenticated user from JWT token
        db: Database session dependency
    
    Returns:
        RefreshResponse: Success status and refreshed data
        
    Raises:
        HTTPException: If error occurs during refresh
    """
    try:
        logger.info(f"Refresh playlists data request received for user_id: {current_user.id}")
        
        result = force_refresh_playlists_data(current_user.id, db)
        
        return RefreshResponse(
            success=result["success"],
            message=f"Playlists data refreshed successfully: {result['message']}",
            data={"count": result.get("count", 0)}
        )
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Unexpected error in refresh_playlists_data route for user_id {current_user.id}: {e}")
        raise HTTPException(
            status_code=500,
            detail="Internal server error while refreshing playlists data"
        )

@router.post("/videos/refresh", response_model=RefreshResponse)
async def refresh_dashboard_videos(
    current_user: UserSignUp = Depends(get_current_user),
    db: Session = Depends(get_database_session)
) -> RefreshResponse:
    """
    Refresh videos data by deleting old data and fetching fresh data from YouTube.
    
    This endpoint first deletes existing videos data from the database, then fetches fresh data
    from YouTube API and stores it. This ensures completely fresh data.
    
    Args:
        current_user: The authenticated user from JWT token
        db: Database session dependency
    
    Returns:
        RefreshResponse: Success status and refreshed data
        
    Raises:
        HTTPException: If error occurs during refresh
    """
    try:
        logger.info(f"Refresh videos data request received for user_id: {current_user.id}")
        
        result = force_refresh_videos_data(current_user.id, db)
        
        return RefreshResponse(
            success=result["success"],
            message=f"Videos data refreshed successfully: {result['message']}",
            data={"count": result.get("count", 0)}
        )
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Unexpected error in refresh_videos_data route for user_id {current_user.id}: {e}")
        raise HTTPException(
            status_code=500,
            detail="Internal server error while refreshing videos data"
        )

@router.post("/playlists/{playlist_id}/refresh", response_model=RefreshResponse)
async def refresh_dashboard_playlist_comprehensive(
    playlist_id: str = Path(..., description="The YouTube playlist ID"),
    current_user: UserSignUp = Depends(get_current_user),
    db: Session = Depends(get_database_session)
) -> RefreshResponse:
    """
    Refresh specific playlist data by deleting old data and fetching fresh data from YouTube.
    
    This endpoint first deletes existing data for the specific playlist from the database, then fetches fresh data
    from YouTube API and stores it. This ensures completely fresh data.
    
    Args:
        playlist_id: The YouTube playlist ID
        current_user: The authenticated user from JWT token
        db: Database session dependency
    
    Returns:
        RefreshResponse: Success status and refreshed data
        
    Raises:
        HTTPException: If error occurs during refresh
    """
    try:
        logger.info(f"Refresh single playlist data request received for playlist_id: {playlist_id}, user_id: {current_user.id}")
        
        result = force_refresh_single_playlist_data(current_user.id, playlist_id, db)
        
        return RefreshResponse(
            success=result["success"],
            message=f"Playlist data refreshed successfully: {result['message']}",
            data=result.get("data", {})
        )
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Unexpected error in refresh_single_playlist_data route for playlist_id {playlist_id}, user_id {current_user.id}: {e}")
        raise HTTPException(
            status_code=500,
            detail="Internal server error while refreshing playlist data"
        )

@router.post("/videos/{video_id}/refresh", response_model=RefreshResponse)
async def refresh_dashboard_video_details(
    video_id: str = Path(..., description="The YouTube video ID"),
    current_user: UserSignUp = Depends(get_current_user),
    db: Session = Depends(get_database_session)
) -> RefreshResponse:
    """
    Refresh specific video data by deleting old data and fetching fresh data from YouTube.
    
    This endpoint first deletes existing data for the specific video from the database, then fetches fresh data
    from YouTube API and stores it. This ensures completely fresh data.
    
    Args:
        video_id: The YouTube video ID
        current_user: The authenticated user from JWT token
        db: Database session dependency
    
    Returns:
        RefreshResponse: Success status and refreshed data
        
    Raises:
        HTTPException: If error occurs during refresh
    """
    try:
        logger.info(f"Refresh single video data request received for video_id: {video_id}, user_id: {current_user.id}")
        
        result = force_refresh_single_video_data(current_user.id, video_id, db)
        
        return RefreshResponse(
            success=result["success"],
            message=f"Video data refreshed successfully: {result['message']}",
            data=result.get("data", {})
        )
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Unexpected error in refresh_single_video_data route for video_id {video_id}, user_id {current_user.id}: {e}")
        raise HTTPException(
            status_code=500,
            detail="Internal server error while refreshing video data"
        )

@router.post("/playlists/{playlist_id}/videos/refresh", response_model=RefreshResponse)
async def refresh_dashboard_playlist_videos(
    playlist_id: str = Path(..., description="The YouTube playlist ID"),
    current_user: UserSignUp = Depends(get_current_user),
    db: Session = Depends(get_database_session)
) -> RefreshResponse:
    """
    Refresh all videos in a specific playlist by deleting old data and fetching fresh data from YouTube.
    
    This endpoint first deletes existing videos data for the specific playlist from the database, then fetches fresh data
    from YouTube API and stores it. This ensures completely fresh data.
    
    Args:
        playlist_id: The YouTube playlist ID
        current_user: The authenticated user from JWT token
        db: Database session dependency
    
    Returns:
        RefreshResponse: Success status and refreshed data
        
    Raises:
        HTTPException: If error occurs during refresh
    """
    try:
        logger.info(f"Refresh playlist videos data request received for playlist_id: {playlist_id}, user_id: {current_user.id}")
        
        result = force_refresh_playlist_videos_data(current_user.id, playlist_id, db)
        
        return RefreshResponse(
            success=result["success"],
            message=f"Playlist videos data refreshed successfully: {result['message']}",
            data=result.get("data", {})
        )
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Unexpected error in refresh_playlist_videos_data route for playlist_id {playlist_id}, user_id {current_user.id}: {e}")
        raise HTTPException(
            status_code=500,
            detail="Internal server error while refreshing playlist videos data"
        )

@router.post("/playlists/{playlist_id}/videos/{video_id}/refresh", response_model=RefreshResponse)
async def refresh_dashboard_playlist_video_details(
    playlist_id: str = Path(..., description="The YouTube playlist ID"),
    video_id: str = Path(..., description="The YouTube video ID"),
    current_user: UserSignUp = Depends(get_current_user),
    db: Session = Depends(get_database_session)
) -> RefreshResponse:
    """
    Refresh specific video data within a playlist by deleting old data and fetching fresh data from YouTube.
    
    This endpoint first deletes existing data for the specific video in the playlist from the database, then fetches fresh data
    from YouTube API and stores it. This ensures completely fresh data.
    
    Args:
        playlist_id: The YouTube playlist ID
        video_id: The YouTube video ID
        current_user: The authenticated user from JWT token
        db: Database session dependency
    
    Returns:
        RefreshResponse: Success status and refreshed data
        
    Raises:
        HTTPException: If error occurs during refresh
    """
    try:
        logger.info(f"Refresh playlist video data request received for playlist_id: {playlist_id}, video_id: {video_id}, user_id: {current_user.id}")
        
        result = force_refresh_single_playlist_video_data(current_user.id, playlist_id, video_id, db)
        
        return RefreshResponse(
            success=result["success"],
            message=f"Playlist video data refreshed successfully: {result['message']}",
            data=result.get("data", {})
        )
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Unexpected error in refresh_playlist_video_data route for playlist_id {playlist_id}, video_id {video_id}, user_id {current_user.id}: {e}")
        raise HTTPException(
            status_code=500,
            detail="Internal server error while refreshing playlist video data"
        )
