from typing import List, Dict, Any
from uuid import UUID
from fastapi import HTTPException, Depends
from sqlmodel import Session

from ..services.playlist_service import get_user_playlists, create_new_playlist, get_playlist_videos_by_id
from ..services.youtube_auth_service import get_youtube_client
from ..utils.database_dependency import get_database_session
from ..utils.my_logger import get_logger

logger = get_logger("PLAYLIST_CONTROLLER")

def get_playlists_controller(user_id: UUID, db: Session = Depends(get_database_session)) -> List[Dict[str, Any]]:
    """
    Controller function to get user's YouTube playlists.
    
    Args:
        user_id: UUID of the user
        db: Database session
    
    Returns:
        List[Dict[str, Any]]: List of playlists with their details
    
    Raises:
        HTTPException: If authentication fails or no playlists found
    """
    try:
        # Get YouTube client
        youtube_client = get_youtube_client(user_id, db)
        
        if not youtube_client:
            logger.error(f"Failed to get YouTube client for user_id: {user_id}")
            raise HTTPException(
                status_code=401,
                detail="YouTube authentication failed. Please authenticate with YouTube first."
            )
        
        # Get playlists
        playlists = get_user_playlists(youtube_client)
        
        if not playlists:
            logger.warning(f"No playlists found for user_id: {user_id}")
            return []
        
        logger.info(f"Successfully retrieved {len(playlists)} playlists for user_id: {user_id}")
        return playlists
        
    except Exception as e:
        logger.error(f"Error in get_playlists_controller for user_id {user_id}: {e}")
        raise HTTPException(
            status_code=500,
            detail=f"Failed to retrieve playlists: {str(e)}"
        )

def create_playlist_controller(user_id: UUID, playlist_name: str, description: str = "", privacy_status: str = "private", db: Session = Depends(get_database_session)) -> Dict[str, Any]:
    """
    Controller function to create a new YouTube playlist.
    
    Args:
        user_id: UUID of the user
        playlist_name: Name of the playlist to create
        description: Description for the playlist (optional)
        db: Database session
    
    Returns:
        Dict[str, Any]: Playlist creation response with playlist details
    
    Raises:
        HTTPException: If authentication fails or playlist creation fails
    """
    try:
        # Validate input
        if not playlist_name or not playlist_name.strip():
            raise HTTPException(
                status_code=400,
                detail="Playlist name is required"
            )
        
        # Get YouTube client
        youtube_client = get_youtube_client(user_id, db)
        
        if not youtube_client:
            logger.error(f"Failed to get YouTube client for user_id: {user_id}")
            raise HTTPException(
                status_code=401,
                detail="YouTube authentication failed. Please authenticate with YouTube first."
            )
        
        # Create playlist
        playlist_id = create_new_playlist(youtube_client, playlist_name.strip(), description.strip(), privacy_status)
        
        logger.info(f"Successfully created playlist '{playlist_name}' with ID {playlist_id} and privacy '{privacy_status}' for user_id: {user_id}")
        
        return {
            "playlist_id": playlist_id,
            "playlist_name": playlist_name,
            "description": description,
            "privacy_status": privacy_status,
            "status": "created"
        }
        
    except HTTPException:
        # Re-raise HTTP exceptions as they are already properly formatted
        raise
    except Exception as e:
        logger.error(f"Error in create_playlist_controller for user_id {user_id}: {e}")
        raise HTTPException(
            status_code=500,
            detail=f"Failed to create playlist: {str(e)}"
        )

def get_playlist_videos_controller(user_id: UUID, playlist_id: str, db: Session = Depends(get_database_session)) -> List[Dict[str, Any]]:
    """
    Controller function to get videos from a specific playlist.
    
    Args:
        user_id: UUID of the user
        playlist_id: YouTube playlist ID
        db: Database session
    
    Returns:
        List[Dict[str, Any]]: List of videos with their details
    
    Raises:
        HTTPException: If authentication fails or playlist not found
    """
    try:
        # Validate playlist ID
        if not playlist_id or not playlist_id.strip():
            raise HTTPException(
                status_code=400,
                detail="Playlist ID is required"
            )
        
        # Get YouTube client
        youtube_client = get_youtube_client(user_id, db)
        
        if not youtube_client:
            logger.error(f"Failed to get YouTube client for user_id: {user_id}")
            raise HTTPException(
                status_code=401,
                detail="YouTube authentication failed. Please authenticate with YouTube first."
            )
        
        # Get playlist videos
        videos = get_playlist_videos_by_id(youtube_client, playlist_id.strip())
        
        logger.info(f"Successfully retrieved {len(videos)} videos from playlist {playlist_id} for user_id: {user_id}")
        return videos
        
    except HTTPException:
        # Re-raise HTTP exceptions as they are already properly formatted
        raise
    except Exception as e:
        logger.error(f"Error in get_playlist_videos_controller for user_id {user_id}, playlist_id {playlist_id}: {e}")
        raise HTTPException(
            status_code=500,
            detail=f"Failed to retrieve playlist videos: {str(e)}"
        ) 