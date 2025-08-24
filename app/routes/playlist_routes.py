from typing import List, Dict, Any
from uuid import UUID
from fastapi import APIRouter, HTTPException, Depends, Path, Body, Query
from sqlmodel import Session
from pydantic import BaseModel

from ..controllers.playlist_controller import get_playlists_controller, create_playlist_controller, get_playlist_videos_controller
from ..controllers.playlist_selection_controller import select_playlist_controller, get_video_playlist_controller
from ..utils.database_dependency import get_database_session
from ..controllers.user_controller import get_current_user
from ..models.user_model import UserSignUp
from ..models.playlist_model import PlaylistCreateRequest, PlaylistResponse, PlaylistCreateResponse
from ..utils.my_logger import get_logger

logger = get_logger("PLAYLIST_ROUTES")

router = APIRouter(prefix="/playlists", tags=["playlists"])

# Request/Response models for playlist selection
class PlaylistSelectionResponse(BaseModel):
    """Response model for playlist selection operations"""
    success: bool
    message: str
    data: Dict[str, Any]

@router.get("/my-playlists")
async def get_my_playlists(
    current_user: UserSignUp = Depends(get_current_user),
    db: Session = Depends(get_database_session)
) -> Dict[str, Any]:
    """
    Get all playlists for the authenticated user.
    
    Args:
        current_user: The authenticated user from JWT token
        db: Database session dependency
    
    Returns:
        Dict[str, Any]: Response with success status, message, data, and count
        
    Raises:
        HTTPException: If authentication fails or other errors occur
    """
    try:
        logger.info(f"Playlist request received for user_id: {current_user.id}")
        playlists = get_playlists_controller(current_user.id, db)
        
        return {
            "success": True,
            "message": f"Successfully retrieved {len(playlists)} playlists",
            "data": playlists,
            "count": len(playlists)
        }
        
    except HTTPException:
        # Re-raise HTTP exceptions as they are already properly formatted
        raise
    except Exception as e:
        logger.error(f"Unexpected error in get_my_playlists route for user_id {current_user.id}: {e}")
        raise HTTPException(
            status_code=500,
            detail="Internal server error while retrieving playlists"
        )

@router.get("/count")
async def get_playlists_count(
    current_user: UserSignUp = Depends(get_current_user),
    db: Session = Depends(get_database_session)
) -> Dict[str, Any]:
    """
    Get the count of playlists for the authenticated user.
    
    Args:
        current_user: The authenticated user from JWT token
        db: Database session dependency
    
    Returns:
        Dict[str, Any]: Count of playlists
        
    Raises:
        HTTPException: If authentication fails or other errors occur
    """
    try:
        logger.info(f"Playlist count request received for user_id: {current_user.id}")
        playlists = get_playlists_controller(current_user.id, db)
        
        return {
            "success": True,
            "message": f"Successfully retrieved playlist count",
            "count": len(playlists),
            "user_id": str(current_user.id)
        }
        
    except HTTPException:
        # Re-raise HTTP exceptions as they are already properly formatted
        raise
    except Exception as e:
        logger.error(f"Unexpected error in get_playlists_count route for user_id {current_user.id}: {e}")
        raise HTTPException(
            status_code=500,
            detail="Internal server error while retrieving playlist count"
        )

@router.post("/create", response_model=Dict[str, Any])
async def create_playlist(
    playlist_data: PlaylistCreateRequest,
    current_user: UserSignUp = Depends(get_current_user),
    db: Session = Depends(get_database_session)
) -> Dict[str, Any]:
    """
    Create a new playlist for the authenticated user.
    
    Args:
        playlist_data: PlaylistCreateRequest containing playlist_name and optional description
        current_user: The authenticated user from JWT token
        db: Database session dependency
    
    Returns:
        Dict[str, Any]: Playlist creation response with success status and playlist details
        
    Raises:
        HTTPException: If authentication fails or other errors occur
    """
    try:
        logger.info(f"Playlist creation request received for user_id: {current_user.id}")
        
        # Extract playlist data from Pydantic model
        playlist_name = playlist_data.playlist_name.strip()
        description = playlist_data.description.strip() if playlist_data.description else ""
        privacy_status = playlist_data.privacy_status.value if playlist_data.privacy_status else "private"
        
        # Create playlist
        result = create_playlist_controller(current_user.id, playlist_name, description, privacy_status, db)
        
        return {
            "success": True,
            "message": f"Successfully created playlist '{playlist_name}'",
            "data": result
        }
        
    except HTTPException:
        # Re-raise HTTP exceptions as they are already properly formatted
        raise
    except Exception as e:
        logger.error(f"Unexpected error in create_playlist route for user_id {current_user.id}: {e}")
        raise HTTPException(
            status_code=500,
            detail="Internal server error while creating playlist"
        )

@router.get("/{playlist_id}/videos")
async def get_playlist_videos(
    playlist_id: str = Path(..., description="The YouTube playlist ID"),
    current_user: UserSignUp = Depends(get_current_user),
    db: Session = Depends(get_database_session)
) -> Dict[str, Any]:
    """
    Get all videos from a specific playlist using playlist ID.
    
    Args:
        playlist_id: The YouTube playlist ID
        current_user: The authenticated user from JWT token
        db: Database session dependency
    
    Returns:
        Dict[str, Any]: List of videos with their details
        
    Raises:
        HTTPException: If authentication fails or other errors occur
    """
    try:
        logger.info(f"Playlist videos request received for playlist_id: {playlist_id}, user_id: {current_user.id}")
        
        # Get playlist videos
        videos = get_playlist_videos_controller(current_user.id, playlist_id, db)
        
        return {
            "success": True,
            "message": f"Successfully retrieved {len(videos)} videos from playlist",
            "data": videos,
            "playlist_id": playlist_id,
            "total_videos": len(videos)
        }
        
    except HTTPException:
        # Re-raise HTTP exceptions as they are already properly formatted
        raise
    except Exception as e:
        logger.error(f"Unexpected error in get_playlist_videos route for playlist_id {playlist_id}, user_id {current_user.id}: {e}")
        raise HTTPException(
            status_code=500,
            detail="Internal server error while retrieving playlist videos"
        )

# Playlist selection routes
@router.post("/{video_id}/select-playlist")
async def select_playlist_for_video(
    video_id: UUID = Path(..., description="The ID of the video"),
    playlist_name: str = Query(..., description="Name of the playlist to select"),
    current_user: UserSignUp = Depends(get_current_user),
    db: Session = Depends(get_database_session)
) -> PlaylistSelectionResponse:
    """
    Select a playlist for a video.
    
    This endpoint allows users to select an existing playlist or create a new one
    and save it to the video model for later use during upload.
    
    Args:
        video_id: The UUID of the video
        playlist_name: Name of the playlist to select
        current_user: The authenticated user from JWT token
        db: Database session dependency
    
    Returns:
        PlaylistSelectionResponse: Playlist selection result
        
    Raises:
        HTTPException: If selection fails or other errors occur
    """
    try:
        logger.info(f"Select playlist request received for video_id: {video_id}, playlist: {playlist_name}, user_id: {current_user.id}")
        
        # Select playlist for video
        result = select_playlist_controller(video_id, current_user.id, playlist_name, db)
        
        return PlaylistSelectionResponse(
            success=True,
            message=result.get('message', 'Playlist selected successfully'),
            data=result
        )
        
    except HTTPException:
        # Re-raise HTTP exceptions as they are already properly formatted
        raise
    except Exception as e:
        logger.error(f"Unexpected error in select_playlist_for_video route for video_id {video_id}, user_id {current_user.id}: {e}")
        raise HTTPException(
            status_code=500,
            detail="Internal server error while selecting playlist"
        )

@router.get("/{video_id}/playlist", response_model=PlaylistSelectionResponse)
async def get_video_playlist(
    video_id: UUID = Path(..., description="The ID of the video"),
    current_user: UserSignUp = Depends(get_current_user),
    db: Session = Depends(get_database_session)
) -> PlaylistSelectionResponse:
    """
    Get the selected playlist for a video.
    
    Args:
        video_id: The UUID of the video
        current_user: The authenticated user from JWT token
        db: Database session dependency
    
    Returns:
        PlaylistSelectionResponse: Current playlist information
        
    Raises:
        HTTPException: If video not found or other errors occur
    """
    try:
        logger.info(f"Get video playlist request received for video_id: {video_id}, user_id: {current_user.id}")
        
        # Get video playlist
        result = get_video_playlist_controller(video_id, current_user.id, db)
        
        return PlaylistSelectionResponse(
            success=True,
            message=result.get('message', 'Playlist information retrieved successfully'),
            data=result
        )
        
    except HTTPException:
        # Re-raise HTTP exceptions as they are already properly formatted
        raise
    except Exception as e:
        logger.error(f"Unexpected error in get_video_playlist route for video_id {video_id}, user_id {current_user.id}: {e}")
        raise HTTPException(
            status_code=500,
            detail="Internal server error while retrieving playlist information"
        ) 