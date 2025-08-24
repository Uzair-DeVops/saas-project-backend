from typing import Optional, Dict, Any
from uuid import UUID
from fastapi import HTTPException
from sqlmodel import Session

from ..services.youtube_upload_service import upload_video_to_youtube
from ..utils.my_logger import get_logger

logger = get_logger("YOUTUBE_UPLOAD_CONTROLLER")

def upload_video_controller(video_id: UUID, user_id: UUID, db: Session) -> Dict[str, Any]:
    """
    Controller function to upload a video to YouTube.
    
    Args:
        video_id: UUID of the video to upload
        user_id: UUID of the user
        db: Database session
    
    Returns:
        Dict[str, Any]: Upload result response
    
    Raises:
        HTTPException: If upload fails or other errors occur
    """
    try:
        logger.info(f"Starting video upload for video_id: {video_id}, user_id: {user_id}")
        
        # Upload video to YouTube
        result = upload_video_to_youtube(video_id, user_id, db)
        
        if not result:
            logger.error(f"Failed to upload video for video_id: {video_id}, user_id: {user_id}")
            raise HTTPException(
                status_code=500,
                detail="Failed to upload video to YouTube. Please check your YouTube API credentials and try again."
            )
        
        logger.info(f"Successfully uploaded video for video_id: {video_id}, user_id: {user_id}")
        return result
        
    except HTTPException:
        # Re-raise HTTP exceptions as they are already properly formatted
        raise
    except Exception as e:
        logger.error(f"Error in upload_video_controller for video_id {video_id}, user_id {user_id}: {e}")
        raise HTTPException(
            status_code=500,
            detail=f"Failed to upload video: {str(e)}"
        ) 