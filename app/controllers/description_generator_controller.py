from typing import Optional
from uuid import UUID
from sqlmodel import Session
from fastapi import HTTPException
from ..services.decription_generator_service import video_summary_generator_agent
from ..utils.my_logger import get_logger
from ..models.video_model import Video
from sqlmodel import select
from ..utils.transcript_dependency import get_video_transcript
from ..utils.gemini_dependency import get_user_gemini_api_key
logger = get_logger("DESCRIPTION_GENERATOR_CONTROLLER")

class DescriptionResponse:
    def __init__(self, video_id: UUID, generated_description: str, success: bool, message: str):
        self.video_id = video_id
        self.generated_description = generated_description
        self.success = success
        self.message = message


async def generate_description_for_video(
    video_id: UUID,
    user_id: UUID,
    db: Session,
    custom_template: Optional[str] = None
) -> DescriptionResponse:
    """
    Generate description for a video using its transcript
    """
    try:
        logger.info(f"Generating description for video {video_id} by user {user_id}")
        
        # Get video transcript
        transcript = get_video_transcript(video_id, user_id, db)
        
        if not transcript:
            logger.error(f"Video transcript not found for video {video_id}")
            raise HTTPException(status_code=400, detail="Video transcript not found or not generated yet")
        
        # Use default template if none provided
        if not custom_template:
            custom_template = """
🔔 Subscribe for more educational content!
👍 Like this video if it helped you
💬 Comment below with your questions
📱 Follow us on social media for updates

#Education #Learning #Tutorial
"""
        api_key = get_user_gemini_api_key(user_id, db)
        # Generate description
        description = await video_summary_generator_agent(transcript, custom_template,api_key)
        
        logger.info(f"Description generated successfully for video {video_id}")
        return DescriptionResponse(
            video_id=video_id,
            generated_description=description,
            success=True,
            message="Description generated successfully"
        )
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error generating description for video {video_id}: {e}")
        raise HTTPException(status_code=500, detail="Failed to generate description")

async def save_video_description(
    video_id: UUID,
    user_id: UUID,
    description: str,
    db: Session
) -> dict:
    """
    Save the generated description to the video record
    """
    try:
        logger.info(f"Saving description for video {video_id} by user {user_id}")
        
        statement = select(Video).where(
            Video.id == video_id,
            Video.user_id == user_id
        )
        video = db.exec(statement).first()
        
        if not video:
            logger.error(f"Video not found: {video_id}")
            raise HTTPException(status_code=404, detail="Video not found")
        
        # Update video description
        video.description = description
        db.add(video)
        db.commit()
        
        logger.info(f"Description saved successfully for video {video_id}")
        return {
            "success": True,
            "message": "Description saved successfully",
            "video_id": str(video_id),
            "description": description
        }
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error saving description for video {video_id}: {e}")
        raise HTTPException(status_code=500, detail="Failed to save description")

async def regenerate_video_description(
    video_id: UUID,
    user_id: UUID,
    db: Session,
    custom_template: Optional[str] = None
) -> DescriptionResponse:
    """
    Regenerate description for a video
    """
    try:
        logger.info(f"Regenerating description for video {video_id} by user {user_id}")
        
        result = await generate_description_for_video(video_id, user_id, db, custom_template)
        
        logger.info(f"Description regenerated successfully for video {video_id}")
        return result
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error regenerating description for video {video_id}: {e}")
        raise HTTPException(status_code=500, detail="Failed to regenerate description") 