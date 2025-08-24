from typing import Dict, Any
from uuid import UUID
from fastapi import APIRouter, HTTPException, Depends, Path, Body
from sqlmodel import Session
from pydantic import BaseModel

from ..controllers.privacy_status_controller import set_privacy_status_controller, get_privacy_status_controller
from ..utils.database_dependency import get_database_session
from ..controllers.user_controller import get_current_user
from ..models.user_model import UserSignUp
from ..models.privacy_status_model import PrivacyStatusRequest, PrivacyStatusResponse
from ..utils.my_logger import get_logger

logger = get_logger("PRIVACY_STATUS_ROUTES")

router = APIRouter(prefix="/privacy-status", tags=["privacy-status"])

@router.post("/{video_id}/privacy-status", response_model=PrivacyStatusResponse)
async def set_video_privacy_status(
    video_id: UUID = Path(..., description="The ID of the video"),
    privacy_data: PrivacyStatusRequest = Body(..., description="Privacy status settings"),
    current_user: UserSignUp = Depends(get_current_user),
    db: Session = Depends(get_database_session)
) -> PrivacyStatusResponse:
    """
    Set privacy status for a video.
    
    This endpoint allows users to set:
    - Privacy status (private, public, unlisted)
    
    Args:
        video_id: The UUID of the video
        privacy_data: PrivacyStatusRequest containing privacy status
        current_user: The authenticated user from JWT token
        db: Database session dependency
    
    Returns:
        PrivacyStatusResponse: Privacy status response
        
    Raises:
        HTTPException: If video not found or other errors occur
    """
    try:
        logger.info(f"Set privacy status request received for video_id: {video_id}, user_id: {current_user.id}")
        
        # Set privacy status
        result = set_privacy_status_controller(video_id, current_user.id, privacy_data, db)
        
        return PrivacyStatusResponse(
            success=True,
            message=f"Successfully set privacy status for video: {result.get('privacy_status', 'unknown')}",
            data=result
        )
        
    except HTTPException:
        # Re-raise HTTP exceptions as they are already properly formatted
        raise
    except Exception as e:
        logger.error(f"Unexpected error in set_video_privacy_status route for video_id {video_id}, user_id {current_user.id}: {e}")
        raise HTTPException(
            status_code=500,
            detail="Internal server error while setting privacy status"
        )

@router.get("/{video_id}/privacy-status", response_model=PrivacyStatusResponse)
async def get_video_privacy_status(
    video_id: UUID = Path(..., description="The ID of the video"),
    current_user: UserSignUp = Depends(get_current_user),
    db: Session = Depends(get_database_session)
) -> PrivacyStatusResponse:
    """
    Get current privacy status for a video.
    
    Args:
        video_id: The UUID of the video
        current_user: The authenticated user from JWT token
        db: Database session dependency
    
    Returns:
        PrivacyStatusResponse: Current privacy status
        
    Raises:
        HTTPException: If video not found or other errors occur
    """
    try:
        logger.info(f"Get privacy status request received for video_id: {video_id}, user_id: {current_user.id}")
        
        # Get privacy status
        result = get_privacy_status_controller(video_id, current_user.id, db)
        
        return PrivacyStatusResponse(
            success=True,
            message=f"Successfully retrieved privacy status for video: {result.get('video_title', 'Untitled')}",
            data=result
        )
        
    except HTTPException:
        # Re-raise HTTP exceptions as they are already properly formatted
        raise
    except Exception as e:
        logger.error(f"Unexpected error in get_video_privacy_status route for video_id {video_id}, user_id {current_user.id}: {e}")
        raise HTTPException(
            status_code=500,
            detail="Internal server error while retrieving privacy status"
        ) 