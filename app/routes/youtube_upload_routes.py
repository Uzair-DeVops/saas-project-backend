from typing import Dict, Any, Optional
from uuid import UUID
from fastapi import APIRouter, HTTPException, Depends, Path, Body, Query
from sqlmodel import Session
from pydantic import BaseModel

from ..controllers.youtube_upload_controller import upload_video_controller
from ..utils.database_dependency import get_database_session
from ..controllers.user_controller import get_current_user
from ..models.user_model import UserSignUp
from ..utils.my_logger import get_logger

logger = get_logger("YOUTUBE_UPLOAD_ROUTES")

router = APIRouter(prefix="/youtube-upload", tags=["youtube-upload"])

# Request/Response models
class UploadResponse(BaseModel):
    """Response model for upload operations"""
    success: bool
    message: str
    data: Dict[str, Any]

@router.post("/{video_id}/upload", response_model=UploadResponse)
async def upload_video(
    video_id: UUID = Path(..., description="The ID of the video to upload"),
    current_user: UserSignUp = Depends(get_current_user),
    db: Session = Depends(get_database_session)
) -> UploadResponse:
    """
    Upload a video to YouTube.
    
    This endpoint uploads a video to YouTube with all the metadata from the database:
    - Title, description, and transcript
    - Privacy settings and scheduling
    - Automatic playlist addition (if playlist_name is set in database)
    - Automatic custom thumbnail upload (if thumbnail_path exists in database)
    
    Args:
        video_id: The UUID of the video to upload
        current_user: The authenticated user from JWT token
        db: Database session dependency
    
    Returns:
        UploadResponse: Upload result with YouTube video ID and URL
        
    Raises:
        HTTPException: If upload fails or other errors occur
    """
    try:
        logger.info(f"Upload video request received for video_id: {video_id}, user_id: {current_user.id}")
        
        # Upload video to YouTube
        result = upload_video_controller(video_id, current_user.id, db)
        
        return UploadResponse(
            success=True,
            message=result.get('message', 'Video uploaded successfully'),
            data=result
        )
        
    except HTTPException:
        # Re-raise HTTP exceptions as they are already properly formatted
        raise
    except Exception as e:
        logger.error(f"Unexpected error in upload_video route for video_id {video_id}, user_id {current_user.id}: {e}")
        raise HTTPException(
            status_code=500,
            detail="Internal server error while uploading video"
        ) 