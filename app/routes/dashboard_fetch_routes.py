"""
Dashboard Fetch Routes - Handles fetching dashboard data
"""
from typing import Dict, Any
from fastapi import APIRouter, HTTPException, Depends, Path
from sqlmodel import Session
from pydantic import BaseModel

from ..controllers.dashboard_fetch_controller import (
    fetch_and_store_overview_data,
    fetch_and_store_playlists_data,
    fetch_and_store_videos_data,
    fetch_and_store_single_playlist_data,
    fetch_and_store_single_video_data,
    fetch_and_store_playlist_videos_data,
    fetch_and_store_single_playlist_video_data
)
from ..services.dashboard_data_service import DashboardDataService
from ..utils.database_dependency import get_database_session
from ..controllers.user_controller import get_current_user
from ..models.user_model import UserSignUp
from ..utils.my_logger import get_logger

logger = get_logger("DASHBOARD_FETCH_ROUTES")

router = APIRouter(prefix="/dashboard", tags=["dashboard-fetch"])

# Response models
class FetchResponse(BaseModel):
    """Response model for fetch operations"""
    success: bool
    message: str
    data: Dict[str, Any] = {}

# Fetch & Store APIs
@router.post("/overview/fetch", response_model=FetchResponse)
async def fetch_dashboard_overview(
    current_user: UserSignUp = Depends(get_current_user),
    db: Session = Depends(get_database_session)
) -> FetchResponse:
    """
    Fetch overview data from YouTube and store in database.
    
    This endpoint fetches fresh overview data from YouTube API and stores it in the database.
    The data will be available for subsequent GET requests.
    
    Args:
        current_user: The authenticated user from JWT token
        db: Database session dependency
    
    Returns:
        FetchResponse: Success status and fetched data
        
    Raises:
        HTTPException: If error occurs during fetch or storage
    """
    try:
        logger.info(f"Fetch overview data request received for user_id: {current_user.id}")
        
        result = fetch_and_store_overview_data(current_user.id, db)
        
        return FetchResponse(
            success=result["success"],
            message=result["message"],
            data=result.get("data", {})
        )
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Unexpected error in fetch_overview_data route for user_id {current_user.id}: {e}")
        raise HTTPException(
            status_code=500,
            detail="Internal server error while fetching overview data"
        )

@router.post("/playlists/fetch", response_model=FetchResponse)
async def fetch_dashboard_playlists(
    current_user: UserSignUp = Depends(get_current_user),
    db: Session = Depends(get_database_session)
) -> FetchResponse:
    """
    Fetch all playlists data from YouTube and store in database.
    
    This endpoint fetches fresh playlists data from YouTube API and stores it in the database.
    The data will be available for subsequent GET requests.
    
    Args:
        current_user: The authenticated user from JWT token
        db: Database session dependency
    
    Returns:
        FetchResponse: Success status and fetched data
        
    Raises:
        HTTPException: If error occurs during fetch or storage
    """
    try:
        logger.info(f"Fetch playlists data request received for user_id: {current_user.id}")
        
        result = fetch_and_store_playlists_data(current_user.id, db)
        
        return FetchResponse(
            success=result["success"],
            message=result["message"],
            data={"count": result.get("count", 0)}
        )
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Unexpected error in fetch_playlists_data route for user_id {current_user.id}: {e}")
        raise HTTPException(
            status_code=500,
            detail="Internal server error while fetching playlists data"
        )

@router.post("/videos/fetch", response_model=FetchResponse)
async def fetch_dashboard_videos(
    current_user: UserSignUp = Depends(get_current_user),
    db: Session = Depends(get_database_session)
) -> FetchResponse:
    """
    Fetch all videos data from YouTube and store in database.
    
    This endpoint fetches fresh videos data from YouTube API and stores it in the database.
    The data will be available for subsequent GET requests.
    
    Args:
        current_user: The authenticated user from JWT token
        db: Database session dependency
    
    Returns:
        FetchResponse: Success status and fetched data
        
    Raises:
        HTTPException: If error occurs during fetch or storage
    """
    try:
        logger.info(f"Fetch videos data request received for user_id: {current_user.id}")
        
        result = fetch_and_store_videos_data(current_user.id, db)
        
        return FetchResponse(
            success=result["success"],
            message=result["message"],
            data={"count": result.get("count", 0)}
        )
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Unexpected error in fetch_videos_data route for user_id {current_user.id}: {e}")
        raise HTTPException(
            status_code=500,
            detail="Internal server error while fetching videos data"
        )

@router.post("/playlists/{playlist_id}/fetch", response_model=FetchResponse)
async def fetch_dashboard_playlist_comprehensive(
    playlist_id: str = Path(..., description="The YouTube playlist ID"),
    current_user: UserSignUp = Depends(get_current_user),
    db: Session = Depends(get_database_session)
) -> FetchResponse:
    """
    Fetch specific playlist data from YouTube and store in database.
    
    This endpoint fetches fresh data for a specific playlist from YouTube API and stores it in the database.
    The data will be available for subsequent GET requests.
    
    Args:
        playlist_id: The YouTube playlist ID
        current_user: The authenticated user from JWT token
        db: Database session dependency
    
    Returns:
        FetchResponse: Success status and fetched data
        
    Raises:
        HTTPException: If error occurs during fetch or storage
    """
    try:
        logger.info(f"Fetch single playlist data request received for playlist_id: {playlist_id}, user_id: {current_user.id}")
        
        result = fetch_and_store_single_playlist_data(current_user.id, playlist_id, db)
        
        return FetchResponse(
            success=result["success"],
            message=result["message"],
            data=result.get("data", {})
        )
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Unexpected error in fetch_single_playlist_data route for playlist_id {playlist_id}, user_id {current_user.id}: {e}")
        raise HTTPException(
            status_code=500,
            detail="Internal server error while fetching playlist data"
        )

@router.post("/videos/{video_id}/fetch", response_model=FetchResponse)
async def fetch_dashboard_video_details(
    video_id: str = Path(..., description="The YouTube video ID"),
    current_user: UserSignUp = Depends(get_current_user),
    db: Session = Depends(get_database_session)
) -> FetchResponse:
    """
    Fetch specific video data from YouTube and store in database.
    
    This endpoint fetches fresh data for a specific video from YouTube API and stores it in the database.
    The data will be available for subsequent GET requests.
    
    Args:
        video_id: The YouTube video ID
        current_user: The authenticated user from JWT token
        db: Database session dependency
    
    Returns:
        FetchResponse: Success status and fetched data
        
    Raises:
        HTTPException: If error occurs during fetch or storage
    """
    try:
        logger.info(f"Fetch single video data request received for video_id: {video_id}, user_id: {current_user.id}")
        
        result = fetch_and_store_single_video_data(current_user.id, video_id, db)
        
        return FetchResponse(
            success=result["success"],
            message=result["message"],
            data=result.get("data", {})
        )
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Unexpected error in fetch_single_video_data route for video_id {video_id}, user_id {current_user.id}: {e}")
        raise HTTPException(
            status_code=500,
            detail="Internal server error while fetching video data"
        )

@router.post("/playlists/{playlist_id}/videos/fetch", response_model=FetchResponse)
async def fetch_dashboard_playlist_videos(
    playlist_id: str = Path(..., description="The YouTube playlist ID"),
    current_user: UserSignUp = Depends(get_current_user),
    db: Session = Depends(get_database_session)
) -> FetchResponse:
    """
    Fetch all videos in a specific playlist from YouTube and store in database.
    
    This endpoint fetches all videos in a playlist from YouTube API and stores them in the database.
    The videos will be available for subsequent GET requests.
    
    Args:
        playlist_id: The YouTube playlist ID
        current_user: The authenticated user from JWT token
        db: Database session dependency
    
    Returns:
        FetchResponse: Success status and fetched data
        
    Raises:
        HTTPException: If error occurs during fetch or storage
    """
    try:
        logger.info(f"Fetch playlist videos data request received for playlist_id: {playlist_id}, user_id: {current_user.id}")
        
        result = fetch_and_store_playlist_videos_data(current_user.id, playlist_id, db)
        
        return FetchResponse(
            success=result["success"],
            message=result["message"],
            data=result.get("data", {})
        )
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Unexpected error in fetch_playlist_videos_data route for playlist_id {playlist_id}, user_id {current_user.id}: {e}")
        raise HTTPException(
            status_code=500,
            detail="Internal server error while fetching playlist videos data"
        )

@router.post("/playlists/{playlist_id}/videos/{video_id}/fetch", response_model=FetchResponse)
async def fetch_dashboard_playlist_video_details(
    playlist_id: str = Path(..., description="The YouTube playlist ID"),
    video_id: str = Path(..., description="The YouTube video ID"),
    current_user: UserSignUp = Depends(get_current_user),
    db: Session = Depends(get_database_session)
) -> FetchResponse:
    """
    Fetch specific video data within a playlist from YouTube and store in database.
    
    This endpoint fetches fresh data for a specific video in a playlist from YouTube API and stores it in the database.
    The data will be available for subsequent GET requests.
    
    Args:
        playlist_id: The YouTube playlist ID
        video_id: The YouTube video ID
        current_user: The authenticated user from JWT token
        db: Database session dependency
    
    Returns:
        FetchResponse: Success status and fetched data
        
    Raises:
        HTTPException: If error occurs during fetch or storage
    """
    try:
        logger.info(f"Fetch playlist video data request received for playlist_id: {playlist_id}, video_id: {video_id}, user_id: {current_user.id}")
        
        result = fetch_and_store_single_playlist_video_data(current_user.id, playlist_id, video_id, db)
        
        return FetchResponse(
            success=result["success"],
            message=result["message"],
            data=result.get("data", {})
        )
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Unexpected error in fetch_playlist_video_data route for playlist_id {playlist_id}, video_id {video_id}, user_id {current_user.id}: {e}")
        raise HTTPException(
            status_code=500,
            detail="Internal server error while fetching playlist video data"
        )
