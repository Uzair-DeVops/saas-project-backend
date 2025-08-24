from typing import Optional, Dict, Any
from uuid import UUID
from sqlmodel import Session, select
from ..models.video_model import Video
from ..models.privacy_status_model import PrivacyStatusRequest
from ..utils.my_logger import get_logger

logger = get_logger("PRIVACY_STATUS_SERVICE")

def set_video_privacy_status(video_id: UUID, user_id: UUID, privacy_data: PrivacyStatusRequest, db: Session) -> Optional[Dict[str, Any]]:
    """
    Set privacy status for a video.
    
    Args:
        video_id: UUID of the video
        user_id: UUID of the user
        privacy_data: PrivacyStatusRequest containing privacy status
        db: Database session
    
    Returns:
        Dict[str, Any]: Updated video privacy status or None if not found
    """
    try:
        # Get video from database with user ownership check
        statement = select(Video).where(Video.id == video_id, Video.user_id == user_id)
        video = db.exec(statement).first()
        
        if not video:
            logger.warning(f"Video not found with ID: {video_id} for user: {user_id}")
            return None
        
        # Update privacy status in the database
        video.privacy_status = privacy_data.privacy_status.value
        
        # Save changes to database
        db.add(video)
        db.commit()
        db.refresh(video)
        
        # Create privacy status data for response
        privacy_status_data = {
            "privacy_status": video.privacy_status,
            "video_id": str(video_id),
            "user_id": str(user_id)
        }
        
        logger.info(f"Successfully set privacy status for video {video_id}, user {user_id}: {privacy_data.privacy_status.value}")
        
        return privacy_status_data
        
    except Exception as e:
        logger.error(f"Error setting privacy status for user {user_id}, video {video_id}: {e}")
        return None

def get_video_privacy_status(video_id: UUID, user_id: UUID, db: Session) -> Optional[Dict[str, Any]]:
    """
    Get current privacy status for a video.
    
    Args:
        video_id: UUID of the video
        user_id: UUID of the user
        db: Database session
    
    Returns:
        Dict[str, Any]: Current privacy status or None if not found
    """
    try:
        # Get video from database with user ownership check
        statement = select(Video).where(Video.id == video_id, Video.user_id == user_id)
        video = db.exec(statement).first()
        
        if not video:
            logger.warning(f"Video not found with ID: {video_id} for user: {user_id}")
            return None
        
        # Return actual privacy status from database
        privacy_status_data = {
            "video_id": str(video_id),
            "user_id": str(user_id),
            "video_status": video.video_status or "not_set",
            "privacy_status": video.privacy_status,
            "schedule_datetime": video.schedule_datetime,
            "video_title": video.title,
            "video_path": video.video_path
        }
        
        logger.info(f"Successfully retrieved privacy status for video {video_id}, user {user_id}")
        return privacy_status_data
        
    except Exception as e:
        logger.error(f"Error getting privacy status for user {user_id}, video {video_id}: {e}")
        return None 