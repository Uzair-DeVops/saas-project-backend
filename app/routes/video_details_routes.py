from typing import Dict, Any
from uuid import UUID
from fastapi import APIRouter, HTTPException, Depends, Path, Body
from sqlmodel import Session

from ..controllers.video_details_controller import get_complete_video_details_controller, update_video_details_controller
from ..utils.database_dependency import get_database_session
from ..controllers.user_controller import get_current_user
from ..models.user_model import UserSignUp
from ..models.video_details_model import VideoDetailsResponse, UpdateVideoDetailsRequest, UpdateVideoDetailsResponse
from ..utils.my_logger import get_logger

logger = get_logger("VIDEO_DETAILS_ROUTES")

router = APIRouter(prefix="/video-details", tags=["video-details"])

@router.get("/{video_id}/complete", response_model=VideoDetailsResponse)
async def get_complete_video_details(
    video_id: UUID = Path(..., description="The ID of the video"),
    current_user: UserSignUp = Depends(get_current_user),
    db: Session = Depends(get_database_session)
) -> VideoDetailsResponse:
    """
    Get complete video details that will be uploaded to YouTube.
    
    This endpoint shows the final video details including:
    - Title
    - Description merged with timestamps
    - Thumbnail information
    - Video file path
    - All other video metadata
    
    Args:
        video_id: The UUID of the video
        current_user: The authenticated user from JWT token
        db: Database session dependency
    
    Returns:
        VideoDetailsResponse: Complete video details with merged description and timestamps
        
    Raises:
        HTTPException: If video not found or other errors occur
    """
    try:
        logger.info(f"Complete video details request received for video_id: {video_id}, user_id: {current_user.id}")
        
        # Get complete video details
        video_details = get_complete_video_details_controller(video_id, current_user.id, db)
        
        return VideoDetailsResponse(
            success=True,
            message=f"Successfully retrieved complete video details for video: {video_details.title or 'Untitled'}",
            data=video_details
        )
        
    except HTTPException:
        # Re-raise HTTP exceptions as they are already properly formatted
        raise
    except Exception as e:
        logger.error(f"Unexpected error in get_complete_video_details route for video_id {video_id}, user_id {current_user.id}: {e}")
        raise HTTPException(
            status_code=500,
            detail="Internal server error while retrieving video details"
        )

@router.put("/{video_id}/update", response_model=UpdateVideoDetailsResponse)
async def update_video_details(
    video_id: UUID = Path(..., description="The ID of the video"),
    update_data: UpdateVideoDetailsRequest = Body(..., description="Video details to update"),
    current_user: UserSignUp = Depends(get_current_user),
    db: Session = Depends(get_database_session)
) -> UpdateVideoDetailsResponse:
    """
    Update video details (title, description, timestamps) for a specific video.
    
    This endpoint allows users to modify:
    - Title
    - Description
    - Timestamps
    
    Only the fields provided in the request will be updated.
    
    Args:
        video_id: The UUID of the video
        update_data: UpdateVideoDetailsRequest containing the changes
        current_user: The authenticated user from JWT token
        db: Database session dependency
    
    Returns:
        UpdateVideoDetailsResponse: Updated video details with merged description and timestamps
        
    Raises:
        HTTPException: If video not found or other errors occur
    """
    try:
        logger.info(f"Update video details request received for video_id: {video_id}, user_id: {current_user.id}")
        
        # Update video details
        video_details = update_video_details_controller(video_id, current_user.id, update_data, db)
        
        return UpdateVideoDetailsResponse(
            success=True,
            message=f"Successfully updated video details for video: {video_details.title or 'Untitled'}",
            data=video_details
        )
        
    except HTTPException:
        # Re-raise HTTP exceptions as they are already properly formatted
        raise
    except Exception as e:
        logger.error(f"Unexpected error in update_video_details route for video_id {video_id}, user_id {current_user.id}: {e}")
        raise HTTPException(
            status_code=500,
            detail="Internal server error while updating video details"
        ) 