from typing import Optional
from uuid import UUID
from sqlmodel import Session
from fastapi import HTTPException
from ..services.title_generator_service import (
    generate_video_title,
    update_video_title,
    regenerate_title,
    TitleResponse
)
from ..utils.my_logger import get_logger

logger = get_logger("TITLE_GENERATOR_CONTROLLER")

async def generate_title_for_video(
    video_id: UUID,
    user_id: UUID,
    db: Session,
    user_requirements: Optional[str] = None,
    selected_title: Optional[str] = None,
    api_key: Optional[str] = None
) -> TitleResponse:
    """
    Generate title for a video using its transcript
    """
    try:
        logger.info(f"Generating title for video {video_id} by user {user_id}")
        
        result = await generate_video_title(video_id, user_id, db, user_requirements, selected_title, api_key)
        
        if not result.success:
            logger.error(f"Failed to generate title for video {video_id}: {result.message}")
            raise HTTPException(status_code=400, detail=result.message)
        
        logger.info(f"Title generated successfully for video {video_id}: {result.generated_titles}")
        return result
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error generating title for video {video_id}: {e}")
        raise HTTPException(status_code=500, detail="Failed to generate title")

async def save_video_title(
    video_id: UUID,
    user_id: UUID,
    title: str,
    db: Session
) -> dict:
    """
    Save the generated title to the video record
    """
    try:
        logger.info(f"Saving title for video {video_id} by user {user_id}")
        logger.info(f"Title to save: '{title}' (type: {type(title)}, length: {len(title) if title else 0})")
        
        # Validate that title is not empty or just whitespace
        if not title or not title.strip():
            logger.error(f"Empty or invalid title provided: '{title}'")
            raise HTTPException(status_code=400, detail="Title cannot be empty")
        
        # Check if title looks like a UUID (which would be wrong)
        if len(title) == 36 and title.count('-') == 4:
            logger.warning(f"Title appears to be a UUID: '{title}' - this might be incorrect")
        
        success = await update_video_title(video_id, user_id, title, db)
        
        if not success:
            logger.error(f"Failed to save title for video {video_id}")
            raise HTTPException(status_code=400, detail="Failed to save title")
        
        logger.info(f"Title saved successfully for video {video_id}: '{title}'")
        return {
            "success": True,
            "message": "Title saved successfully",
            "video_id": str(video_id),
            "title": title
        }
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error saving title for video {video_id}: {e}")
        raise HTTPException(status_code=500, detail="Failed to save title")

async def regenerate_video_title(
    video_id: UUID,
    user_id: UUID,
    db: Session,
    selected_title: Optional[str] = None
) -> TitleResponse:
    """
    Regenerate title for a video
    """
    try:
        logger.info(f"Regenerating title for video {video_id} by user {user_id}")
        
        result = await regenerate_title(video_id, user_id, db, selected_title)
        
        if not result.success:
            logger.error(f"Failed to regenerate title for video {video_id}: {result.message}")
            raise HTTPException(status_code=400, detail=result.message)
        
        logger.info(f"Title regenerated successfully for video {video_id}: {result.generated_titles}")
        return result
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error regenerating title for video {video_id}: {e}")
        raise HTTPException(status_code=500, detail="Failed to regenerate title") 