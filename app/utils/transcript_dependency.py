from typing import Optional, Dict, Any, List
from uuid import UUID
from sqlmodel import Session, select
import json
from ..models.video_model import Video
from ..utils.my_logger import get_logger

logger = get_logger("TRANSCRIPT_DEPENDENCY")

def get_video_transcript(video_id: UUID, user_id: UUID, db: Session) -> Optional[str]:
    """
    Get the transcript for a specific video.
    
    Args:
        video_id: The video's UUID
        user_id: The user's UUID (for authorization)
        db: Database session
        
    Returns:
        The transcript as a string, or None if not found/not authorized
    """
    try:
        logger.info(f"Fetching transcript for video {video_id} by user {user_id}")
        
        # Get video with transcript
        statement = select(Video).where(
            Video.id == video_id,
            Video.user_id == user_id
        )
        video = db.exec(statement).first()
        
        if not video:
            logger.warning(f"Video {video_id} not found for user {user_id}")
            return None
        
        if not video.transcript:
            logger.warning(f"No transcript available for video {video_id}")
            return None
        
        logger.info(f"Transcript retrieved successfully for video {video_id}")
        return video.transcript
        
    except Exception as e:
        logger.error(f"Error fetching transcript for video {video_id}: {e}")
        return None

def get_video_transcript_parsed(video_id: UUID, user_id: UUID, db: Session) -> Optional[Dict[str, Any]]:
    """
    Get the transcript for a video and parse it as JSON.
    
    Args:
        video_id: The video's UUID
        user_id: The user's UUID (for authorization)
        db: Database session
        
    Returns:
        Parsed transcript as a dictionary, or None if not found/invalid
    """
    try:
        transcript_json = get_video_transcript(video_id, user_id, db)
        
        if not transcript_json:
            return None
        
        # Parse the JSON transcript
        transcript_data = json.loads(transcript_json)
        
        logger.info(f"Transcript parsed successfully for video {video_id}")
        return transcript_data
        
    except json.JSONDecodeError as e:
        logger.error(f"Error parsing transcript JSON for video {video_id}: {e}")
        return None
    except Exception as e:
        logger.error(f"Error getting parsed transcript for video {video_id}: {e}")
        return None

def get_video_transcript_text_only(video_id: UUID, user_id: UUID, db: Session) -> Optional[str]:
    """
    Get the transcript text only (without timestamps) for a video.
    
    Args:
        video_id: The video's UUID
        user_id: The user's UUID (for authorization)
        db: Database session
        
    Returns:
        Plain text transcript, or None if not found
    """
    try:
        transcript_data = get_video_transcript_parsed(video_id, user_id, db)
        
        if not transcript_data:
            return None
        
        # Extract text from segments
        segments = transcript_data.get('segments', [])
        text_parts = []
        
        for segment in segments:
            if isinstance(segment, dict) and 'text' in segment:
                text_parts.append(segment['text'])
        
        full_text = ' '.join(text_parts)
        
        logger.info(f"Text-only transcript extracted for video {video_id}")
        return full_text
        
    except Exception as e:
        logger.error(f"Error extracting text-only transcript for video {video_id}: {e}")
        return None

def get_video_transcript_segments(video_id: UUID, user_id: UUID, db: Session) -> Optional[List[Dict[str, str]]]:
    """
    Get the transcript segments with timestamps for a video.
    
    Args:
        video_id: The video's UUID
        user_id: The user's UUID (for authorization)
        db: Database session
        
    Returns:
        List of segments with timestamps and text, or None if not found
    """
    try:
        transcript_data = get_video_transcript_parsed(video_id, user_id, db)
        
        if not transcript_data:
            return None
        
        segments = transcript_data.get('segments', [])
        
        logger.info(f"Transcript segments retrieved for video {video_id}")
        return segments
        
    except Exception as e:
        logger.error(f"Error getting transcript segments for video {video_id}: {e}")
        return None

def check_transcript_availability(video_id: UUID, user_id: UUID, db: Session) -> Dict[str, Any]:
    """
    Check if a transcript is available for a video.
    
    Args:
        video_id: The video's UUID
        user_id: The user's UUID (for authorization)
        db: Database session
        
    Returns:
        Dictionary with availability status and metadata
    """
    try:
        logger.info(f"Checking transcript availability for video {video_id}")
        
        # Get video
        statement = select(Video).where(
            Video.id == video_id,
            Video.user_id == user_id
        )
        video = db.exec(statement).first()
        
        if not video:
            return {
                "available": False,
                "reason": "Video not found or not authorized",
                "has_transcript": False,
                "transcript_length": 0
            }
        
        if not video.transcript:
            return {
                "available": False,
                "reason": "No transcript available",
                "has_transcript": False,
                "transcript_length": 0
            }
        
        # Try to parse transcript to get more info
        try:
            transcript_data = json.loads(video.transcript)
            segments = transcript_data.get('segments', [])
            text_parts = [seg.get('text', '') for seg in segments if isinstance(seg, dict)]
            full_text = ' '.join(text_parts)
            
            return {
                "available": True,
                "reason": "Transcript available",
                "has_transcript": True,
                "transcript_length": len(full_text),
                "segment_count": len(segments),
                "first_segment": segments[0] if segments else None,
                "last_segment": segments[-1] if segments else None
            }
            
        except json.JSONDecodeError:
            return {
                "available": False,
                "reason": "Invalid transcript format",
                "has_transcript": True,
                "transcript_length": len(video.transcript)
            }
        
    except Exception as e:
        logger.error(f"Error checking transcript availability for video {video_id}: {e}")
        return {
            "available": False,
            "reason": f"Error: {str(e)}",
            "has_transcript": False,
            "transcript_length": 0
        }

def get_transcript_for_ai_processing(video_id: UUID, user_id: UUID, db: Session) -> Optional[str]:
    """
    Get transcript optimized for AI processing (cleaned and formatted).
    
    Args:
        video_id: The video's UUID
        user_id: The user's UUID (for authorization)
        db: Database session
        
    Returns:
        Cleaned transcript text optimized for AI processing
    """
    try:
        transcript_text = get_video_transcript_text_only(video_id, user_id, db)
        
        if not transcript_text:
            return None
        
        # Clean the transcript for AI processing
        cleaned_text = transcript_text.strip()
        
        # Remove extra whitespace
        cleaned_text = ' '.join(cleaned_text.split())
        
        # Basic cleaning for better AI processing
        cleaned_text = cleaned_text.replace('  ', ' ')  # Remove double spaces
        
        logger.info(f"Transcript prepared for AI processing for video {video_id}")
        return cleaned_text
        
    except Exception as e:
        logger.error(f"Error preparing transcript for AI processing for video {video_id}: {e}")
        return None 