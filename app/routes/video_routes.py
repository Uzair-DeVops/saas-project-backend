from fastapi import APIRouter, Depends, UploadFile, File, HTTPException, Form, BackgroundTasks
from sqlmodel import Session
from typing import List
from uuid import UUID
from ..controllers.video_controller import upload_video, get_user_videos, get_video_by_id, download_and_store_video, update_video
from ..models.video_model import VideoResponse, VideoUpdate
from ..utils.database_dependency import get_database_session
from ..controllers.user_controller import get_current_user
from ..models.user_model import UserSignUp

router = APIRouter(prefix="/videos", tags=["videos"])

@router.post("/upload", response_model=VideoResponse)
async def upload_video_endpoint(
    background_tasks: BackgroundTasks,
    file: UploadFile = File(...),
    current_user: UserSignUp = Depends(get_current_user),
    db: Session = Depends(get_database_session)
):
    """
    Upload a video file for the authenticated user
    """
    return await upload_video(file, current_user.id, db, background_tasks)

@router.post("/download", response_model=VideoResponse)
async def download_video_endpoint(
    background_tasks: BackgroundTasks,
    video_url: str = Form(...),
    current_user: UserSignUp = Depends(get_current_user),
    db: Session = Depends(get_database_session)
):
    """
    Download a video from URL and store for the authenticated user
    """
    return await download_and_store_video(video_url, current_user.id, db, background_tasks)

@router.get("/my-videos", response_model=List[VideoResponse])
async def get_my_videos(
    current_user: UserSignUp = Depends(get_current_user),
    db: Session = Depends(get_database_session)
):
    """
    Get all videos for the authenticated user
    """
    return get_user_videos(current_user.id, db)

@router.get("/{video_id}", response_model=VideoResponse)
async def get_my_video(
    video_id: UUID,
    current_user: UserSignUp = Depends(get_current_user),
    db: Session = Depends(get_database_session)
):
    """
    Get a specific video by ID for the authenticated user
    """
    return get_video_by_id(video_id, current_user.id, db)

@router.put("/{video_id}", response_model=VideoResponse)
async def update_my_video(
    video_id: UUID,
    video_update: VideoUpdate,
    current_user: UserSignUp = Depends(get_current_user),
    db: Session = Depends(get_database_session)
):
    """
    Update a specific video by ID for the authenticated user
    """
    return update_video(video_id, current_user.id, video_update, db)

@router.post("/{video_id}/cancel-cleanup")
async def cancel_video_cleanup(
    video_id: UUID,
    current_user: UserSignUp = Depends(get_current_user),
    db: Session = Depends(get_database_session)
):
    """
    Cancel scheduled cleanup for a video
    """
    from ..services.video_cleanup_service import video_cleanup_service
    
    # Verify video belongs to user
    video = get_video_by_id(video_id, current_user.id, db)
    if not video:
        raise HTTPException(status_code=404, detail="Video not found")
    
    # Cancel cleanup
    video_cleanup_service.cancel_cleanup(video_id)
    
    return {"message": f"Cleanup cancelled for video {video_id}"}

@router.get("/debug/active-cleanups")
async def get_active_cleanups(
    current_user: UserSignUp = Depends(get_current_user)
):
    """
    Get list of active cleanup tasks (for debugging)
    """
    from ..services.video_cleanup_service import video_cleanup_service
    
    active_cleanups = video_cleanup_service.get_active_cleanups()
    return {"active_cleanups": active_cleanups} 