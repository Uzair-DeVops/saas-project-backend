from typing import Optional, Dict, Any, List
from uuid import UUID
from fastapi import HTTPException, Depends
from sqlmodel import Session

from ..services.schedule_service import schedule_video, get_scheduled_videos, cancel_schedule, get_schedule_recommendations
from ..models.schedule_model import ScheduleRequest
from ..utils.database_dependency import get_database_session
from ..utils.my_logger import get_logger

logger = get_logger("SCHEDULE_CONTROLLER")

def schedule_video_controller(video_id: UUID, user_id: UUID, schedule_data: ScheduleRequest, db: Session) -> Dict[str, Any]:
    """
    Controller function to schedule a video for upload.
    
    Args:
        video_id: UUID of the video
        user_id: UUID of the user (from current_user.id)
        schedule_data: ScheduleRequest containing date, time, and privacy status
        db: Database session
    
    Returns:
        Dict[str, Any]: Schedule information
    
    Raises:
        HTTPException: If video not found or scheduling fails
    """
    try:
        # Schedule the video
        schedule_info = schedule_video(video_id, user_id, schedule_data, db)
        
        if not schedule_info:
            logger.error(f"Failed to schedule video for video_id: {video_id}, user_id: {user_id}")
            raise HTTPException(
                status_code=404,
                detail="Video not found or you don't have permission to schedule it"
            )
        
        logger.info(f"Successfully scheduled video for video_id: {video_id}, user_id: {user_id}")
        return schedule_info
        
    except HTTPException:
        # Re-raise HTTP exceptions as they are already properly formatted
        raise
    except Exception as e:
        logger.error(f"Error in schedule_video_controller for video_id {video_id}, user_id {user_id}: {e}")
        raise HTTPException(
            status_code=500,
            detail=f"Failed to schedule video: {str(e)}"
        )

def get_scheduled_videos_controller(user_id: UUID, db: Session) -> List[Dict[str, Any]]:
    """
    Controller function to get all scheduled videos for a user.
    
    Args:
        user_id: UUID of the user (from current_user.id)
        db: Database session
    
    Returns:
        List[Dict[str, Any]]: List of scheduled videos
    
    Raises:
        HTTPException: If retrieval fails
    """
    try:
        # Get scheduled videos
        scheduled_videos = get_scheduled_videos(user_id, db)
        
        logger.info(f"Successfully retrieved {len(scheduled_videos)} scheduled videos for user_id: {user_id}")
        return scheduled_videos
        
    except Exception as e:
        logger.error(f"Error in get_scheduled_videos_controller for user_id {user_id}: {e}")
        raise HTTPException(
            status_code=500,
            detail=f"Failed to retrieve scheduled videos: {str(e)}"
        )

def cancel_schedule_controller(video_id: UUID, user_id: UUID, db: Session) -> Dict[str, Any]:
    """
    Controller function to cancel a scheduled video upload.
    
    Args:
        video_id: UUID of the video
        user_id: UUID of the user (from current_user.id)
        db: Database session
    
    Returns:
        Dict[str, Any]: Cancellation response
    
    Raises:
        HTTPException: If video not found or cancellation fails
    """
    try:
        # Cancel the schedule
        success = cancel_schedule(video_id, user_id, db)
        
        if not success:
            logger.error(f"Failed to cancel schedule for video_id: {video_id}, user_id: {user_id}")
            raise HTTPException(
                status_code=404,
                detail="Video not found or you don't have permission to cancel its schedule"
            )
        
        logger.info(f"Successfully cancelled schedule for video_id: {video_id}, user_id: {user_id}")
        return {
            "success": True,
            "message": "Schedule cancelled successfully",
            "video_id": str(video_id)
        }
        
    except HTTPException:
        # Re-raise HTTP exceptions as they are already properly formatted
        raise
    except Exception as e:
        logger.error(f"Error in cancel_schedule_controller for video_id {video_id}, user_id {user_id}: {e}")
        raise HTTPException(
            status_code=500,
            detail=f"Failed to cancel schedule: {str(e)}"
        )

def get_schedule_recommendations_controller() -> Dict[str, Any]:
    """
    Controller function to get schedule time recommendations.
    
    Returns:
        Dict[str, Any]: Schedule recommendations
    
    Raises:
        HTTPException: If retrieval fails
    """
    try:
        # Get schedule recommendations
        recommendations = get_schedule_recommendations()
        
        logger.info("Successfully retrieved schedule recommendations")
        return recommendations
        
    except Exception as e:
        logger.error(f"Error in get_schedule_recommendations_controller: {e}")
        raise HTTPException(
            status_code=500,
            detail=f"Failed to retrieve schedule recommendations: {str(e)}"
        ) 