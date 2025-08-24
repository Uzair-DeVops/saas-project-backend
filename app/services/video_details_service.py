from typing import Optional, Dict, Any
from uuid import UUID
from sqlmodel import Session, select
from ..models.video_model import Video
from ..models.video_details_model import CompleteVideoDetails, UpdateVideoDetailsRequest
from ..utils.my_logger import get_logger

logger = get_logger("VIDEO_DETAILS_SERVICE")

def merge_timestamps_with_description(description: str, timestamps: str) -> str:
    """
    Merge timestamps with description to create a complete description for YouTube.
    
    Args:
        description: The original video description
        timestamps: The generated timestamps
    
    Returns:
        str: Merged description with timestamps
    """
    try:
        if not description and not timestamps:
            return ""
        
        if not timestamps:
            return description or ""
        
        if not description:
            return f"Timestamps:\n{timestamps}"
        
        # Merge description and timestamps
        merged_description = f"{description}\n\nTimestamps:\n{timestamps}"
        
        logger.info("Successfully merged timestamps with description")
        return merged_description
        
    except Exception as e:
        logger.error(f"Error merging timestamps with description: {e}")
        return description or ""

def get_complete_video_details(video_id: UUID, db: Session) -> Optional[CompleteVideoDetails]:
    """
    Get complete video details including merged description with timestamps.
    
    Args:
        video_id: UUID of the video
        db: Database session
    
    Returns:
        CompleteVideoDetails: Complete video details or None if not found
    """
    try:
        # Get video from database
        statement = select(Video).where(Video.id == video_id)
        video = db.exec(statement).first()
        
        if not video:
            logger.warning(f"Video not found with ID: {video_id}")
            return None
        
        # Merge timestamps with description
        description_with_timestamps = merge_timestamps_with_description(
            video.description, 
            video.timestamps
        )
        
        # Create complete video details
        complete_details = CompleteVideoDetails(
            video_id=video.id,
            title=video.title,
            description_with_timestamps=description_with_timestamps,
            thumbnail_path=video.thumbnail_path,
            thumbnail_url=video.thumbnail_url,
            video_path=video.video_path,
            youtube_video_id=video.youtube_video_id,
            created_at=video.created_at,
            original_description=video.description,
            timestamps=video.timestamps,
            transcript=video.transcript
        )
        
        logger.info(f"Successfully prepared complete video details for video ID: {video_id}")
        return complete_details
        
    except Exception as e:
        logger.error(f"Error getting complete video details for video ID {video_id}: {e}")
        return None

def get_video_details_for_user(video_id: UUID, user_id: UUID, db: Session) -> Optional[CompleteVideoDetails]:
    """
    Get complete video details for a specific user's video.
    
    Args:
        video_id: UUID of the video
        user_id: UUID of the user
        db: Database session
    
    Returns:
        CompleteVideoDetails: Complete video details or None if not found or not owned by user
    """
    try:
        # Get video from database with user ownership check
        statement = select(Video).where(Video.id == video_id, Video.user_id == user_id)
        video = db.exec(statement).first()
        
        if not video:
            logger.warning(f"Video not found with ID: {video_id} for user: {user_id}")
            return None
        
        # Get complete details
        return get_complete_video_details(video_id, db)
        
    except Exception as e:
        logger.error(f"Error getting video details for user {user_id}, video {video_id}: {e}")
        return None

def update_video_details(video_id: UUID, user_id: UUID, update_data: UpdateVideoDetailsRequest, db: Session) -> Optional[CompleteVideoDetails]:
    """
    Update video details (title, description, timestamps) for a specific user's video.
    
    Args:
        video_id: UUID of the video
        user_id: UUID of the user
        update_data: UpdateVideoDetailsRequest containing the changes
        db: Database session
    
    Returns:
        CompleteVideoDetails: Updated video details or None if not found or not owned by user
    """
    try:
        # Get video from database with user ownership check
        statement = select(Video).where(Video.id == video_id, Video.user_id == user_id)
        video = db.exec(statement).first()
        
        if not video:
            logger.warning(f"Video not found with ID: {video_id} for user: {user_id}")
            return None
        
        # Update fields if provided
        if update_data.title is not None:
            video.title = update_data.title.strip()
            logger.info(f"Updated title for video {video_id}: {video.title}")
        
        if update_data.description is not None:
            video.description = update_data.description.strip()
            logger.info(f"Updated description for video {video_id}")
        
        if update_data.timestamps is not None:
            video.timestamps = update_data.timestamps.strip()
            logger.info(f"Updated timestamps for video {video_id}")
        
        # Save changes to database
        db.add(video)
        db.commit()
        db.refresh(video)
        
        logger.info(f"Successfully updated video details for video {video_id}, user {user_id}")
        
        # Return updated complete video details
        return get_complete_video_details(video_id, db)
        
    except Exception as e:
        logger.error(f"Error updating video details for user {user_id}, video {video_id}: {e}")
        db.rollback()
        return None 