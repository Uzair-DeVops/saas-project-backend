from typing import Optional, Dict, Any
from uuid import UUID
from fastapi import HTTPException, Depends
from sqlmodel import Session

from ..services.video_details_service import get_video_details_for_user, update_video_details
from ..models.video_details_model import CompleteVideoDetails, UpdateVideoDetailsRequest
from ..utils.database_dependency import get_database_session
from ..utils.my_logger import get_logger

logger = get_logger("VIDEO_DETAILS_CONTROLLER")

def get_complete_video_details_controller(video_id: UUID, user_id: UUID, db: Session) -> CompleteVideoDetails:
    """
    Controller function to get complete video details for a user's video.
    
    Args:
        video_id: UUID of the video
        user_id: UUID of the user (from current_user.id)
        db: Database session
    
    Returns:
        CompleteVideoDetails: Complete video details with merged description and timestamps
    
    Raises:
        HTTPException: If video not found or other errors occur
    """
    try:
        # Get complete video details
        video_details = get_video_details_for_user(video_id, user_id, db)
        
        if not video_details:
            logger.error(f"Video details not found for video_id: {video_id}, user_id: {user_id}")
            raise HTTPException(
                status_code=404,
                detail="Video not found or you don't have permission to access it"
            )
        
        logger.info(f"Successfully retrieved complete video details for video_id: {video_id}, user_id: {user_id}")
        return video_details
        
    except HTTPException:
        # Re-raise HTTP exceptions as they are already properly formatted
        raise
    except Exception as e:
        logger.error(f"Error in get_complete_video_details_controller for video_id {video_id}, user_id {user_id}: {e}")
        raise HTTPException(
            status_code=500,
            detail=f"Failed to retrieve video details: {str(e)}"
        )

def update_video_details_controller(video_id: UUID, user_id: UUID, update_data: UpdateVideoDetailsRequest, db: Session) -> CompleteVideoDetails:
    """
    Controller function to update video details for a user's video.
    
    Args:
        video_id: UUID of the video
        user_id: UUID of the user (from current_user.id)
        update_data: UpdateVideoDetailsRequest containing the changes
        db: Database session
    
    Returns:
        CompleteVideoDetails: Updated video details with merged description and timestamps
    
    Raises:
        HTTPException: If video not found or other errors occur
    """
    try:
        # Update video details
        video_details = update_video_details(video_id, user_id, update_data, db)
        
        if not video_details:
            logger.error(f"Failed to update video details for video_id: {video_id}, user_id: {user_id}")
            raise HTTPException(
                status_code=404,
                detail="Video not found or you don't have permission to update it"
            )
        
        logger.info(f"Successfully updated video details for video_id: {video_id}, user_id: {user_id}")
        return video_details
        
    except HTTPException:
        # Re-raise HTTP exceptions as they are already properly formatted
        raise
    except Exception as e:
        logger.error(f"Error in update_video_details_controller for video_id {video_id}, user_id {user_id}: {e}")
        raise HTTPException(
            status_code=500,
            detail=f"Failed to update video details: {str(e)}"
        ) 