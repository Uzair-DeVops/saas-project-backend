from typing import Optional
from uuid import UUID
from sqlmodel import Session
from fastapi import HTTPException
from ..services.time_stamps_generator_service import time_stamps_generator
from ..utils.my_logger import get_logger
from ..models.video_model import Video
from sqlmodel import select
from ..utils.transcript_dependency import get_video_transcript
from ..utils.gemini_dependency import get_user_gemini_api_key
logger = get_logger("TIME_STAMPS_GENERATOR_CONTROLLER")

class TimeStampsResponse:
    def __init__(self, video_id: UUID, generated_timestamps: str, success: bool, message: str):
        self.video_id = video_id
        self.generated_timestamps = generated_timestamps
        self.success = success
        self.message = message


async def generate_timestamps_for_video(
    video_id: UUID,
    user_id: UUID,
    db: Session
) -> TimeStampsResponse:
    """
    Generate timestamps for a video using its transcript
    """
    try:
        logger.info(f"Generating timestamps for video {video_id} by user {user_id}")
        
        # Get video transcript
        transcript = get_video_transcript(video_id, user_id, db)
        
        if not transcript:
            logger.error(f"Video transcript not found for video {video_id}")
            raise HTTPException(status_code=400, detail="Video transcript not found or not generated yet")
        
        # Generate timestamps
        api_key = get_user_gemini_api_key(user_id, db)
        timestamps = await time_stamps_generator(transcript,api_key)
        
        logger.info(f"Timestamps generated successfully for video {video_id}")
        return TimeStampsResponse(
            video_id=video_id,
            generated_timestamps=timestamps,
            success=True,
            message="Timestamps generated successfully"
        )
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error generating timestamps for video {video_id}: {e}")
        raise HTTPException(status_code=500, detail="Failed to generate timestamps")

async def save_video_timestamps(
    video_id: UUID,
    user_id: UUID,
    timestamps: str,
    db: Session
) -> dict:
    """
    Save the generated timestamps to the video record
    """
    try:
        logger.info(f"Saving timestamps for video {video_id} by user {user_id}")
        
        statement = select(Video).where(
            Video.id == video_id,
            Video.user_id == user_id
        )
        video = db.exec(statement).first()
        
        if not video:
            logger.error(f"Video not found: {video_id}")
            raise HTTPException(status_code=404, detail="Video not found")
        
        # Update video timestamps
        video.timestamps = timestamps
        db.add(video)
        db.commit()
        
        logger.info(f"Timestamps saved successfully for video {video_id}")
        return {
            "success": True,
            "message": "Timestamps saved successfully",
            "video_id": str(video_id),
            "timestamps": timestamps
        }
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error saving timestamps for video {video_id}: {e}")
        raise HTTPException(status_code=500, detail="Failed to save timestamps")

async def regenerate_video_timestamps(
    video_id: UUID,
    user_id: UUID,
    db: Session
) -> TimeStampsResponse:
    """
    Regenerate timestamps for a video
    """
    try:
        logger.info(f"Regenerating timestamps for video {video_id} by user {user_id}")
        
        result = await generate_timestamps_for_video(video_id, user_id, db)
        
        logger.info(f"Timestamps regenerated successfully for video {video_id}")
        return result
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error regenerating timestamps for video {video_id}: {e}")
        raise HTTPException(status_code=500, detail="Failed to regenerate timestamps")
