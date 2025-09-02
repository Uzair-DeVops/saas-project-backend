from typing import Optional
from uuid import UUID
from sqlmodel import Session
from fastapi import HTTPException, UploadFile
import shutil
from ..services.thumbnail_generator_service import agent_runner
from ..utils.my_logger import get_logger
from ..utils.gemini_dependency import get_user_gemini_api_key
logger = get_logger("THUMBNAIL_GENERATOR_CONTROLLER")

async def generate_thumbnail_for_video(
    video_id: UUID,
    user_id: UUID,
    db: Session
) -> dict:
    """
    Generate thumbnail image URL for a video using its transcript
    """
    try:
        logger.info(f"Generating thumbnail for video {video_id} by user {user_id}")
        
        # Get video transcript using utility
        from ..utils.transcript_dependency import get_video_transcript
        
        transcript = get_video_transcript(video_id, user_id, db)
        
        if not transcript:
            logger.error(f"No transcript available for video {video_id}")
            raise HTTPException(status_code=400, detail="No transcript available for this video")
        
        # Check if user has Gemini API key
        api_key = get_user_gemini_api_key(user_id, db)
        if not api_key:
            logger.warning(f"No Gemini API key found for user {user_id}")
            return {
                "success": False,
                "message": "No Gemini API key found. Please add your Gemini API key in settings to generate thumbnails.",
                "video_id": str(video_id),
                "image_url": None,
                "width": None,
                "height": None,
            }
        
        # Generate thumbnail using the service
        result = await agent_runner(transcript, api_key)
        
        if not result:
            logger.error(f"Failed to generate thumbnail for video {video_id}")
            raise HTTPException(status_code=500, detail="Failed to generate thumbnail")
        
        logger.info(f"Thumbnail generated successfully for video {video_id}")
        return {
            "success": True,
            "message": "Thumbnail generated successfully",
            "video_id": str(video_id),
            "image_url": result.get("imageUrl"),
            "width": result.get("width"),
            "height": result.get("height"),
        }
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error generating thumbnail for video {video_id}: {e}")
        raise HTTPException(status_code=500, detail="Failed to generate thumbnail")

async def save_video_thumbnail(
    video_id: UUID,
    user_id: UUID,
    thumbnail_url: str,
    db: Session
) -> dict:
    """
    Download thumbnail from URL and save to local directory, then store path in database
    """
    try:
        logger.info(f"Saving thumbnail for video {video_id} by user {user_id}")
        
        # Get video from database
        from ..models.video_model import Video
        from sqlmodel import select
        
        video = db.exec(select(Video).where(
            Video.id == video_id,
            Video.user_id == user_id
        )).first()
        
        if not video:
            logger.error(f"Video {video_id} not found for user {user_id}")
            raise HTTPException(status_code=404, detail="Video not found")
        
        # Validate thumbnail URL
        if not thumbnail_url or not thumbnail_url.strip():
            logger.error(f"Invalid thumbnail URL provided: '{thumbnail_url}'")
            raise HTTPException(status_code=400, detail="Thumbnail URL cannot be empty")
        
        # Download and save thumbnail
        thumbnail_path = await download_and_save_thumbnail(thumbnail_url, video_id, user_id)
        
        if not thumbnail_path:
            logger.error(f"Failed to download thumbnail from URL: {thumbnail_url}")
            raise HTTPException(status_code=500, detail="Failed to download thumbnail")
        
        # Update video thumbnail path and URL
        video.thumbnail_path = thumbnail_path
        video.thumbnail_url = thumbnail_url.strip()
        db.add(video)
        db.commit()
        
        logger.info(f"Thumbnail saved successfully for video {video_id}: {thumbnail_path}")
        return {
            "success": True,
            "message": "Thumbnail downloaded and saved successfully",
            "video_id": str(video_id),
            "thumbnail_path": thumbnail_path,
            "thumbnail_url": thumbnail_url,
            "saved_at": video.created_at
        }
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error saving thumbnail for video {video_id}: {e}")
        db.rollback()
        raise HTTPException(status_code=500, detail="Failed to save thumbnail")

async def download_and_save_thumbnail(thumbnail_url: str, video_id: UUID, user_id: UUID) -> Optional[str]:
    """
    Download thumbnail from URL and save to thumbnails directory
    """
    try:
        import aiohttp
        import os
        from pathlib import Path
        from urllib.parse import urlparse
        
        # Create thumbnails directory if it doesn't exist
        thumbnails_dir = Path("thumbnails")
        thumbnails_dir.mkdir(exist_ok=True)
        
        # Generate unique filename
        parsed_url = urlparse(thumbnail_url)
        file_extension = Path(parsed_url.path).suffix
        if not file_extension or file_extension.lower() not in ['.jpg', '.jpeg', '.png', '.gif', '.webp']:
            file_extension = '.jpg'  # Default to jpg if no valid extension
        
        filename = f"{user_id}_{video_id}{file_extension}"
        file_path = thumbnails_dir / filename
        
        # Download the image
        async with aiohttp.ClientSession() as session:
            async with session.get(thumbnail_url) as response:
                if response.status == 200:
                    # Save the image
                    with open(file_path, 'wb') as f:
                        f.write(await response.read())
                    
                    logger.info(f"Thumbnail downloaded and saved: {file_path}")
                    return str(file_path)
                else:
                    logger.error(f"Failed to download thumbnail. Status: {response.status}")
                    return None
                    
    except Exception as e:
        logger.error(f"Error downloading thumbnail: {e}")
        return None

async def upload_custom_thumbnail(
    video_id: UUID,
    user_id: UUID,
    file: UploadFile,
    db: Session
) -> dict:
    """
    Upload and save a custom thumbnail image from user's computer
    """
    try:
        logger.info(f"Uploading custom thumbnail for video {video_id} by user {user_id}")
        
        # Get video from database
        from ..models.video_model import Video
        from sqlmodel import select
        
        video = db.exec(select(Video).where(
            Video.id == video_id,
            Video.user_id == user_id
        )).first()
        
        if not video:
            logger.error(f"Video {video_id} not found for user {user_id}")
            raise HTTPException(status_code=404, detail="Video not found")
        
        # Validate file type
        if not file.content_type or not file.content_type.startswith('image/'):
            logger.error(f"Invalid file type: {file.content_type}")
            raise HTTPException(status_code=400, detail="File must be an image (jpg, png, gif, webp)")
        
        # Validate file size (max 10MB)
        if file.size and file.size > 10 * 1024 * 1024:  # 10MB
            logger.error(f"File too large: {file.size} bytes")
            raise HTTPException(status_code=400, detail="File size must be less than 10MB")
        
        # Save uploaded thumbnail
        thumbnail_path = await save_uploaded_thumbnail(file, video_id, user_id)
        
        if not thumbnail_path:
            logger.error(f"Failed to save uploaded thumbnail")
            raise HTTPException(status_code=500, detail="Failed to save uploaded thumbnail")
        
        # Update video thumbnail
        video.thumbnail_path = thumbnail_path
        video.thumbnail_url = None  # No original URL for uploaded files
        db.add(video)
        db.commit()
        
        logger.info(f"Custom thumbnail uploaded successfully for video {video_id}: {thumbnail_path}")
        return {
            "success": True,
            "message": "Custom thumbnail uploaded successfully",
            "video_id": str(video_id),
            "thumbnail_path": thumbnail_path,
            "original_filename": file.filename,
            "file_size": file.size,
            "content_type": file.content_type,
            "saved_at": video.created_at
        }
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error uploading custom thumbnail for video {video_id}: {e}")
        db.rollback()
        raise HTTPException(status_code=500, detail="Failed to upload custom thumbnail")

async def save_uploaded_thumbnail(file: UploadFile, video_id: UUID, user_id: UUID) -> Optional[str]:
    """
    Save uploaded thumbnail file to thumbnails directory
    """
    try:
        import os
        from pathlib import Path
        
        # Create thumbnails directory if it doesn't exist
        thumbnails_dir = Path("thumbnails")
        thumbnails_dir.mkdir(exist_ok=True)
        
        # Generate unique filename
        file_extension = Path(file.filename).suffix if file.filename else '.jpg'
        if file_extension.lower() not in ['.jpg', '.jpeg', '.png', '.gif', '.webp']:
            file_extension = '.jpg'  # Default to jpg if invalid extension
        
        filename = f"{user_id}_{video_id}_custom{file_extension}"
        file_path = thumbnails_dir / filename
        
        # Save the uploaded file
        with open(file_path, "wb") as buffer:
            shutil.copyfileobj(file.file, buffer)
        
        logger.info(f"Custom thumbnail saved: {file_path}")
        return str(file_path)
        
    except Exception as e:
        logger.error(f"Error saving uploaded thumbnail: {e}")
        return None
