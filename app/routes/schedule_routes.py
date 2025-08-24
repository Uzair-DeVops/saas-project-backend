from typing import Dict, Any, List
from uuid import UUID
from fastapi import APIRouter, HTTPException, Depends, Path, Body
from sqlmodel import Session

from ..controllers.schedule_controller import (
    schedule_video_controller, 
    get_scheduled_videos_controller, 
    cancel_schedule_controller,
    get_schedule_recommendations_controller
)
from ..utils.database_dependency import get_database_session
from ..controllers.user_controller import get_current_user
from ..models.user_model import UserSignUp
from ..models.schedule_model import ScheduleRequest, ScheduleResponse
from ..utils.my_logger import get_logger

logger = get_logger("SCHEDULE_ROUTES")

router = APIRouter(prefix="/schedule", tags=["schedule"])

@router.post("/{video_id}/schedule", response_model=ScheduleResponse)
async def schedule_video(
    video_id: UUID = Path(..., description="The ID of the video"),
    schedule_data: ScheduleRequest = Body(..., description="Schedule date, time, and privacy status"),
    current_user: UserSignUp = Depends(get_current_user),
    db: Session = Depends(get_database_session)
) -> ScheduleResponse:
    """
    Schedule a video for upload at a specific date and time.
    
    This endpoint allows users to schedule their videos with:
    - Specific date (YYYY-MM-DD)
    - Specific time (HH:MM in 24-hour format)
    - Privacy status (private, public, unlisted)
    
    Args:
        video_id: The UUID of the video
        schedule_data: ScheduleRequest containing date, time, and privacy status
        current_user: The authenticated user from JWT token
        db: Database session dependency
    
    Returns:
        ScheduleResponse: Schedule information with formatted display
    
    Raises:
        HTTPException: If video not found or other errors occur
    """
    try:
        logger.info(f"Schedule video request received for video_id: {video_id}, user_id: {current_user.id}")
        
        # Schedule the video
        result = schedule_video_controller(video_id, current_user.id, schedule_data, db)
        
        return ScheduleResponse(
            success=True,
            message=f"Successfully scheduled video '{result.get('video_title', 'Untitled')}' for {result.get('formatted_schedule', 'unknown time')}",
            data=result
        )
        
    except HTTPException:
        # Re-raise HTTP exceptions as they are already properly formatted
        raise
    except Exception as e:
        logger.error(f"Unexpected error in schedule_video route for video_id {video_id}, user_id {current_user.id}: {e}")
        raise HTTPException(
            status_code=500,
            detail="Internal server error while scheduling video"
        )

@router.get("/my-scheduled-videos")
async def get_my_scheduled_videos(
    current_user: UserSignUp = Depends(get_current_user),
    db: Session = Depends(get_database_session)
) -> Dict[str, Any]:
    """
    Get all scheduled videos for the authenticated user.
    
    Args:
        current_user: The authenticated user from JWT token
        db: Database session dependency
    
    Returns:
        Dict[str, Any]: List of scheduled videos with timing information
        
    Raises:
        HTTPException: If retrieval fails or other errors occur
    """
    try:
        logger.info(f"Get scheduled videos request received for user_id: {current_user.id}")
        
        # Get scheduled videos
        scheduled_videos = get_scheduled_videos_controller(current_user.id, db)
        
        return {
            "success": True,
            "message": f"Successfully retrieved {len(scheduled_videos)} scheduled videos",
            "data": scheduled_videos,
            "total_scheduled": len(scheduled_videos)
        }
        
    except HTTPException:
        # Re-raise HTTP exceptions as they are already properly formatted
        raise
    except Exception as e:
        logger.error(f"Unexpected error in get_my_scheduled_videos route for user_id {current_user.id}: {e}")
        raise HTTPException(
            status_code=500,
            detail="Internal server error while retrieving scheduled videos"
        )

@router.delete("/{video_id}/cancel")
async def cancel_scheduled_video(
    video_id: UUID = Path(..., description="The ID of the video"),
    current_user: UserSignUp = Depends(get_current_user),
    db: Session = Depends(get_database_session)
) -> Dict[str, Any]:
    """
    Cancel a scheduled video upload.
    
    Args:
        video_id: The UUID of the video
        current_user: The authenticated user from JWT token
        db: Database session dependency
    
    Returns:
        Dict[str, Any]: Cancellation confirmation
        
    Raises:
        HTTPException: If video not found or other errors occur
    """
    try:
        logger.info(f"Cancel schedule request received for video_id: {video_id}, user_id: {current_user.id}")
        
        # Cancel the schedule
        result = cancel_schedule_controller(video_id, current_user.id, db)
        
        return result
        
    except HTTPException:
        # Re-raise HTTP exceptions as they are already properly formatted
        raise
    except Exception as e:
        logger.error(f"Unexpected error in cancel_scheduled_video route for video_id {video_id}, user_id {current_user.id}: {e}")
        raise HTTPException(
            status_code=500,
            detail="Internal server error while cancelling schedule"
        )

@router.get("/recommendations")
async def get_schedule_recommendations(
    current_user: UserSignUp = Depends(get_current_user)
) -> Dict[str, Any]:
    """
    Get schedule time recommendations for better engagement.
    
    Args:
        current_user: The authenticated user from JWT token
    
    Returns:
        Dict[str, Any]: Schedule time recommendations
        
    Raises:
        HTTPException: If retrieval fails or other errors occur
    """
    try:
        logger.info(f"Schedule recommendations request received for user_id: {current_user.id}")
        
        # Get recommendations
        recommendations = get_schedule_recommendations_controller()
        
        return {
            "success": True,
            "message": "Successfully retrieved schedule recommendations",
            "data": recommendations
        }
        
    except HTTPException:
        # Re-raise HTTP exceptions as they are already properly formatted
        raise
    except Exception as e:
        logger.error(f"Unexpected error in get_schedule_recommendations route for user_id {current_user.id}: {e}")
        raise HTTPException(
            status_code=500,
            detail="Internal server error while retrieving recommendations"
        ) 