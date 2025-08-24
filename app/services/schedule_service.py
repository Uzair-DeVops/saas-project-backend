from typing import Optional, Dict, Any, List
from uuid import UUID
from datetime import datetime, timedelta
from sqlmodel import Session, select
from ..models.video_model import Video
from ..models.schedule_model import ScheduleRequest, ScheduleInfo
from ..utils.my_logger import get_logger

logger = get_logger("SCHEDULE_SERVICE")

def schedule_video(video_id: UUID, user_id: UUID, schedule_data: ScheduleRequest, db: Session) -> Optional[Dict[str, Any]]:
    """
    Schedule a video for upload at a specific date and time.
    
    Args:
        video_id: UUID of the video
        user_id: UUID of the user
        schedule_data: ScheduleRequest containing date, time, and privacy status
        db: Database session
    
    Returns:
        Dict[str, Any]: Schedule information or None if error
    """
    try:
        # Get video from database with user ownership check
        statement = select(Video).where(Video.id == video_id, Video.user_id == user_id)
        video = db.exec(statement).first()
        
        if not video:
            logger.warning(f"Video not found with ID: {video_id} for user: {user_id}")
            return None
        
        # Get schedule datetime
        try:
            schedule_datetime = schedule_data.get_schedule_datetime()
        except ValueError as e:
            logger.error(f"Invalid schedule datetime: {e}")
            return None
        
        # Update video with schedule information
        video.schedule_datetime = schedule_datetime
        video.privacy_status = schedule_data.privacy_status.value
        video.video_status = "scheduled"
        
        # Save changes to database
        db.add(video)
        db.commit()
        db.refresh(video)
        
        # Create schedule response
        schedule_info = create_schedule_info(video, schedule_datetime)
        
        logger.info(f"Successfully scheduled video {video_id} for {schedule_datetime} with privacy {schedule_data.privacy_status.value}")
        return schedule_info
        
    except Exception as e:
        logger.error(f"Error scheduling video for user {user_id}, video {video_id}: {e}")
        db.rollback()
        return None

def get_scheduled_videos(user_id: UUID, db: Session) -> List[Dict[str, Any]]:
    """
    Get all scheduled videos for a user.
    
    Args:
        user_id: UUID of the user
        db: Database session
    
    Returns:
        List[Dict[str, Any]]: List of scheduled videos
    """
    try:
        # Get all scheduled videos for the user
        statement = select(Video).where(
            Video.user_id == user_id,
            Video.video_status == "scheduled",
            Video.schedule_datetime.is_not(None)
        ).order_by(Video.schedule_datetime)
        
        videos = db.exec(statement).all()
        
        scheduled_videos = []
        for video in videos:
            schedule_info = create_schedule_info(video, video.schedule_datetime)
            scheduled_videos.append(schedule_info)
        
        logger.info(f"Successfully retrieved {len(scheduled_videos)} scheduled videos for user {user_id}")
        return scheduled_videos
        
    except Exception as e:
        logger.error(f"Error getting scheduled videos for user {user_id}: {e}")
        return []

def cancel_schedule(video_id: UUID, user_id: UUID, db: Session) -> bool:
    """
    Cancel a scheduled video upload.
    
    Args:
        video_id: UUID of the video
        user_id: UUID of the user
        db: Database session
    
    Returns:
        bool: True if successfully cancelled, False otherwise
    """
    try:
        # Get video from database with user ownership check
        statement = select(Video).where(Video.id == video_id, Video.user_id == user_id)
        video = db.exec(statement).first()
        
        if not video:
            logger.warning(f"Video not found with ID: {video_id} for user: {user_id}")
            return False
        
        # Reset schedule information
        video.schedule_datetime = None
        video.video_status = "ready"
        # Keep privacy status as it might be set separately
        
        # Save changes to database
        db.add(video)
        db.commit()
        db.refresh(video)
        
        logger.info(f"Successfully cancelled schedule for video {video_id}, user {user_id}")
        return True
        
    except Exception as e:
        logger.error(f"Error cancelling schedule for user {user_id}, video {video_id}: {e}")
        db.rollback()
        return False

def create_schedule_info(video: Video, schedule_datetime: str) -> Dict[str, Any]:
    """
    Create schedule information for a video.
    
    Args:
        video: Video object
        schedule_datetime: Schedule datetime string
    
    Returns:
        Dict[str, Any]: Schedule information
    """
    try:
        # Parse schedule datetime
        schedule_dt = datetime.fromisoformat(schedule_datetime.replace('Z', '+00:00'))
        current_dt = datetime.now()
        
        # Calculate time until schedule
        time_diff = schedule_dt - current_dt
        time_until_schedule = format_time_difference(time_diff)
        
        # Format schedule for display
        formatted_schedule = schedule_dt.strftime("%B %d, %Y at %I:%M %p")
        
        return {
            "video_id": str(video.id),
            "video_title": video.title or "Untitled",
            "schedule_datetime": schedule_datetime,
            "privacy_status": video.privacy_status,
            "video_status": video.video_status,
            "formatted_schedule": formatted_schedule,
            "time_until_schedule": time_until_schedule,
            "video_path": video.video_path
        }
        
    except Exception as e:
        logger.error(f"Error creating schedule info: {e}")
        return {}

def format_time_difference(time_diff: timedelta) -> str:
    """
    Format time difference in a human-readable format.
    
    Args:
        time_diff: Time difference
    
    Returns:
        str: Formatted time difference
    """
    total_seconds = int(time_diff.total_seconds())
    
    if total_seconds < 0:
        return "Past due"
    
    days = total_seconds // 86400
    hours = (total_seconds % 86400) // 3600
    minutes = (total_seconds % 3600) // 60
    
    if days > 0:
        return f"{days} day{'s' if days != 1 else ''}, {hours} hour{'s' if hours != 1 else ''}"
    elif hours > 0:
        return f"{hours} hour{'s' if hours != 1 else ''}, {minutes} minute{'s' if minutes != 1 else ''}"
    else:
        return f"{minutes} minute{'s' if minutes != 1 else ''}"

def get_schedule_recommendations() -> Dict[str, Any]:
    """
    Get schedule time recommendations for better engagement.
    
    Returns:
        Dict[str, Any]: Schedule recommendations
    """
    current_time = datetime.now()
    
    recommendations = {
        "today": {
            "9:00": "Best for morning audience (high engagement)",
            "14:00": "Good for afternoon reach (students/workers on breaks)",
            "19:00": "Prime evening time (peak viewing hours)",
            "21:00": "Night owl time (late-night viewers)"
        },
        "tomorrow": {
            "9:00": "Morning engagement (early risers)",
            "14:00": "Afternoon reach (lunch breaks)",
            "19:00": "Evening peak (family time)"
        },
        "weekend": {
            "10:00": "Weekend family time (relaxed viewing)",
            "14:00": "Weekend afternoon (casual viewers)",
            "18:00": "Weekend evening (entertainment time)"
        }
    }
    
    return recommendations 