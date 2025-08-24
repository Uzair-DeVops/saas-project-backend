from typing import Optional, Dict, Any
from uuid import UUID
from fastapi import HTTPException
from sqlmodel import Session

from ..services.playlist_service import select_and_save_playlist_for_video, get_video_playlist
from ..utils.my_logger import get_logger

logger = get_logger("PLAYLIST_SELECTION_CONTROLLER")

def select_playlist_controller(video_id: UUID, user_id: UUID, playlist_name: str, db: Session) -> Dict[str, Any]:
    """
    Controller function to select and save a playlist for a video.
    
    Args:
        video_id: UUID of the video
        user_id: UUID of the user
        playlist_name: Name of the playlist to select
        db: Database session
    
    Returns:
        Dict[str, Any]: Playlist selection result
    
    Raises:
        HTTPException: If selection fails or other errors occur
    """
    try:
        logger.info(f"Selecting playlist '{playlist_name}' for video_id: {video_id}, user_id: {user_id}")
        
        # Select and save playlist
        result = select_and_save_playlist_for_video(video_id, user_id, playlist_name, db)
        
        if not result:
            logger.error(f"Failed to select playlist for video_id: {video_id}, user_id: {user_id}")
            raise HTTPException(
                status_code=500,
                detail="Failed to select playlist. Please check your YouTube API credentials and try again."
            )
        
        logger.info(f"Successfully selected playlist for video_id: {video_id}, user_id: {user_id}")
        return result
        
    except HTTPException:
        # Re-raise HTTP exceptions as they are already properly formatted
        raise
    except Exception as e:
        logger.error(f"Error in select_playlist_controller for video_id {video_id}, user_id {user_id}: {e}")
        raise HTTPException(
            status_code=500,
            detail=f"Failed to select playlist: {str(e)}"
        )

def get_video_playlist_controller(video_id: UUID, user_id: UUID, db: Session) -> Dict[str, Any]:
    """
    Controller function to get the selected playlist for a video.
    
    Args:
        video_id: UUID of the video
        user_id: UUID of the user
        db: Database session
    
    Returns:
        Dict[str, Any]: Playlist information
    
    Raises:
        HTTPException: If video not found or other errors occur
    """
    try:
        logger.info(f"Getting playlist for video_id: {video_id}, user_id: {user_id}")
        
        # Get video playlist
        result = get_video_playlist(video_id, user_id, db)
        
        if result is None:
            logger.info(f"No playlist found for video_id: {video_id}, user_id: {user_id}")
            return {
                'playlist_name': None,
                'playlist_id': None,
                'video_id': str(video_id),
                'playlist_exists': False,
                'message': 'No playlist selected for this video'
            }
        
        logger.info(f"Successfully retrieved playlist for video_id: {video_id}, user_id: {user_id}")
        return result
        
    except Exception as e:
        logger.error(f"Error in get_video_playlist_controller for video_id {video_id}, user_id {user_id}: {e}")
        raise HTTPException(
            status_code=500,
            detail=f"Failed to get video playlist: {str(e)}"
        ) 