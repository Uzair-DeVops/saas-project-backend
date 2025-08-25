
import shutil
from pathlib import Path
from typing import List
from uuid import UUID
from fastapi import UploadFile, HTTPException, Depends, BackgroundTasks
from sqlmodel import Session, select
from ..models.video_model import Video, VideoResponse, VideoUpdate
from ..utils.my_logger import get_logger
from ..services.video_cleanup_service import video_cleanup_service
from ..services.dowload_video_service import download_youtube_video
from ..services.video_transcript_generator_service import generate_transcript_background
logger = get_logger("VIDEO_CONTROLLER")

# Create videos directory if it doesn't exist
VIDEOS_DIR = Path("videos")
VIDEOS_DIR.mkdir(exist_ok=True)



async def upload_video(
    file: UploadFile,
    user_id: UUID,
    db: Session,
    background_tasks: BackgroundTasks
) -> VideoResponse:
    """
    Upload video file and store path in database
    """
    try:
        # Validate file type
        if not file.content_type or not file.content_type.startswith('video/'):
            raise HTTPException(status_code=400, detail="File must be a video")
        
        # Generate unique filename
        file_extension = Path(file.filename).suffix if file.filename else '.mp4'
        unique_filename = f"{user_id}_{file.filename or 'video'}{file_extension}"
        file_path = VIDEOS_DIR / unique_filename
        
        # Save file to videos directory
        with open(file_path, "wb") as buffer:
            shutil.copyfileobj(file.file, buffer)
        
        # Store video path in databa
        video = Video(
            user_id=user_id,
            video_path=str(file_path)
        )
        
        db.add(video)
        db.commit()
        db.refresh(video)
        
        # Schedule cleanup after 30 minutes
        await video_cleanup_service.schedule_video_cleanup(video.id, str(file_path), db)
        
        # Add transcript generation to background tasks
        background_tasks.add_task(generate_transcript_background, video.id, str(file_path), db)
        
        logger.info(f"Video uploaded successfully for user {user_id}: {file_path}")
        logger.info(f"Cleanup scheduled for video {video.id} in 30 minutes")
        logger.info(f"Transcript generation scheduled in background for video {video.id}")
        
        return VideoResponse(
            id=video.id,
            user_id=video.user_id,
            video_path=video.video_path,
            youtube_video_id=video.youtube_video_id,
            transcript=video.transcript,
            title=video.title,
            timestamps=video.timestamps,
            description=video.description,
            thumbnail_path=video.thumbnail_path,
            thumbnail_url=video.thumbnail_url,
            privacy_status=video.privacy_status,
            schedule_datetime=video.schedule_datetime,
            video_status=video.video_status,
            playlist_name=video.playlist_name,
            created_at=video.created_at
        )
        
    except Exception as e:
        logger.error(f"Error uploading video: {e}")
        raise HTTPException(status_code=500, detail="Failed to upload video")

def get_user_videos(
    user_id: UUID,
    db: Session
) -> List[VideoResponse]:
    """
    Get all videos for a specific user
    """
    try:
        statement = select(Video).where(Video.user_id == user_id)
        videos = db.exec(statement).all()
        
        return [
            VideoResponse(
                id=video.id,
                user_id=video.user_id,
                video_path=video.video_path,
                youtube_video_id=video.youtube_video_id,
                transcript=video.transcript,
                title=video.title,
                timestamps=video.timestamps,
                description=video.description,
                thumbnail_path=video.thumbnail_path,
                thumbnail_url=video.thumbnail_url,
                privacy_status=video.privacy_status,
                schedule_datetime=video.schedule_datetime,
                video_status=video.video_status,
                playlist_name=video.playlist_name,
                created_at=video.created_at
            )
            for video in videos
        ]
        
    except Exception as e:
        logger.error(f"Error fetching videos for user {user_id}: {e}")
        raise HTTPException(status_code=500, detail="Failed to fetch videos")

def get_video_by_id(
    video_id: UUID,
    user_id: UUID,
    db: Session
) -> VideoResponse:
    """
    Get a specific video by ID for a user
    """
    try:
        statement = select(Video).where(
            Video.id == video_id,
            Video.user_id == user_id
        )
        video = db.exec(statement).first()
        
        if not video:
            raise HTTPException(status_code=404, detail="Video not found")
        
        return VideoResponse(
            id=video.id,
            user_id=video.user_id,
            video_path=video.video_path,
            youtube_video_id=video.youtube_video_id,
            transcript=video.transcript,
            title=video.title,
            timestamps=video.timestamps,
            description=video.description,
            thumbnail_path=video.thumbnail_path,
            thumbnail_url=video.thumbnail_url,
            privacy_status=video.privacy_status,
            schedule_datetime=video.schedule_datetime,
            video_status=video.video_status,
            playlist_name=video.playlist_name,
            created_at=video.created_at
        )
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error fetching video {video_id}: {e}")
        raise HTTPException(status_code=500, detail="Failed to fetch video")

async def download_and_store_video(
    video_url: str,
    user_id: UUID,
    db: Session,
    background_tasks: BackgroundTasks
) -> VideoResponse:
    """
    Download video from URL and store path in database
    """
    try:
        # Download video using yt-dlp
        video_id, filepath = download_youtube_video(video_url, str(VIDEOS_DIR))
        
        if not filepath:
            raise HTTPException(status_code=400, detail="Failed to download video from URL")
        
        # Store video path in database
        video = Video(
            user_id=user_id,
            video_path=filepath,
            youtube_video_id=video_id
        )
        
        db.add(video)
        db.commit()
        db.refresh(video)
        
        # Schedule cleanup after 30 minutes
        await video_cleanup_service.schedule_video_cleanup(video.id, filepath, db)
        
        # Add transcript generation to background tasks
        background_tasks.add_task(generate_transcript_background, video.id, filepath, db)
        
        logger.info(f"Video downloaded and stored successfully for user {user_id}: {filepath}")
        logger.info(f"Cleanup scheduled for video {video.id} in 30 minutes")
        logger.info(f"Transcript generation scheduled in background for video {video.id}")
        
        return VideoResponse(
            id=video.id,
            user_id=video.user_id,
            video_path=video.video_path,
            youtube_video_id=video.youtube_video_id,
            transcript=video.transcript,
            title=video.title,
            timestamps=video.timestamps,
            description=video.description,
            thumbnail_path=video.thumbnail_path,
            thumbnail_url=video.thumbnail_url,
            privacy_status=video.privacy_status,
            schedule_datetime=video.schedule_datetime,
            video_status=video.video_status,
            playlist_name=video.playlist_name,
            created_at=video.created_at
        )
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error downloading video: {e}")
        raise HTTPException(status_code=500, detail="Failed to download video") 

def update_video(
    video_id: UUID,
    user_id: UUID,
    video_update: VideoUpdate,
    db: Session
) -> VideoResponse:
    """
    Update a specific video by ID for a user
    """
    try:
        # First, get the video and verify it belongs to the user
        statement = select(Video).where(
            Video.id == video_id,
            Video.user_id == user_id
        )
        video = db.exec(statement).first()
        
        if not video:
            raise HTTPException(status_code=404, detail="Video not found")
        
        # Update only the fields that are provided in the update request
        update_data = video_update.dict(exclude_unset=True)
        
        for field, value in update_data.items():
            if hasattr(video, field):
                setattr(video, field, value)
        
        db.add(video)
        db.commit()
        db.refresh(video)
        
        logger.info(f"Video {video_id} updated successfully for user {user_id}")
        
        return VideoResponse(
            id=video.id,
            user_id=video.user_id,
            video_path=video.video_path,
            youtube_video_id=video.youtube_video_id,
            transcript=video.transcript,
            title=video.title,
            timestamps=video.timestamps,
            description=video.description,
            thumbnail_path=video.thumbnail_path,
            thumbnail_url=video.thumbnail_url,
            privacy_status=video.privacy_status,
            schedule_datetime=video.schedule_datetime,
            video_status=video.video_status,
            playlist_name=video.playlist_name,
            created_at=video.created_at
        )
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error updating video {video_id}: {e}")
        raise HTTPException(status_code=500, detail="Failed to update video") 