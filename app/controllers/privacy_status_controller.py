from typing import Optional, Dict, Any
from uuid import UUID
from fastapi import HTTPException, Depends
from sqlmodel import Session

from ..services.privacy_status_service import set_video_privacy_status, get_video_privacy_status
from ..models.privacy_status_model import PrivacyStatusRequest
from ..utils.database_dependency import get_database_session
from ..utils.my_logger import get_logger

logger = get_logger("PRIVACY_STATUS_CONTROLLER")

def set_privacy_status_controller(video_id: UUID, user_id: UUID, privacy_data: PrivacyStatusRequest, db: Session) -> Dict[str, Any]:
    """
    Controller function to set privacy status for a user's video.
    
    Args:
        video_id: UUID of the video
        user_id: UUID of the user (from current_user.id)
        privacy_data: PrivacyStatusRequest containing privacy status and schedule
        db: Database session
    
    Returns:
        Dict[str, Any]: Privacy status response
    
    Raises:
        HTTPException: If video not found or other errors occur
    """
    try:
        # Set privacy status
        privacy_status = set_video_privacy_status(video_id, user_id, privacy_data, db)
        
        if not privacy_status:
            logger.error(f"Failed to set privacy status for video_id: {video_id}, user_id: {user_id}")
            raise HTTPException(
                status_code=404,
                detail="Video not found or you don't have permission to update it"
            )
        
        logger.info(f"Successfully set privacy status for video_id: {video_id}, user_id: {user_id}")
        return privacy_status
        
    except HTTPException:
        # Re-raise HTTP exceptions as they are already properly formatted
        raise
    except Exception as e:
        logger.error(f"Error in set_privacy_status_controller for video_id {video_id}, user_id {user_id}: {e}")
        raise HTTPException(
            status_code=500,
            detail=f"Failed to set privacy status: {str(e)}"
        )

def get_privacy_status_controller(video_id: UUID, user_id: UUID, db: Session) -> Dict[str, Any]:
    """
    Controller function to get privacy status for a user's video.
    
    Args:
        video_id: UUID of the video
        user_id: UUID of the user (from current_user.id)
        db: Database session
    
    Returns:
        Dict[str, Any]: Privacy status response
    
    Raises:
        HTTPException: If video not found or other errors occur
    """
    try:
        # Get privacy status
        privacy_status = get_video_privacy_status(video_id, user_id, db)
        
        if not privacy_status:
            logger.error(f"Privacy status not found for video_id: {video_id}, user_id: {user_id}")
            raise HTTPException(
                status_code=404,
                detail="Video not found or you don't have permission to access it"
            )
        
        logger.info(f"Successfully retrieved privacy status for video_id: {video_id}, user_id: {user_id}")
        return privacy_status
        
    except HTTPException:
        # Re-raise HTTP exceptions as they are already properly formatted
        raise
    except Exception as e:
        logger.error(f"Error in get_privacy_status_controller for video_id {video_id}, user_id {user_id}: {e}")
        raise HTTPException(
            status_code=500,
            detail=f"Failed to get privacy status: {str(e)}"
        ) 