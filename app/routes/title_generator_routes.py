from fastapi import APIRouter, Depends, HTTPException
from sqlmodel import Session
from uuid import UUID
from pydantic import BaseModel, Field, validator

from ..controllers.title_generator_controller import (
    generate_title_for_video,
    save_video_title,
    regenerate_video_title
)
from ..services.title_generator_service import TitleResponse
from ..utils.database_dependency import get_database_session
from ..controllers.user_controller import get_current_user
from ..models.user_model import UserSignUp
from ..utils.gemini_dependency import get_user_gemini_api_key
router = APIRouter(prefix="/title-generator", tags=["title-generator"])

class TitleSaveRequest(BaseModel):
    title: str = Field(..., min_length=3, max_length=200)
    
    @validator('title')
    def validate_title(cls, v):
        if not v or not v.strip():
            raise ValueError("Title cannot be empty")
        if len(v.strip()) < 3:
            raise ValueError("Title must be at least 3 characters long")
        # Check if it looks like a UUID (which would be wrong)
        if len(v.strip()) == 36 and v.strip().count('-') == 4:
            raise ValueError("Title appears to be a UUID - please provide the actual title text")
        return v.strip()

class RegenerateWithRequirementsRequest(BaseModel):
    user_requirements: str

# Route 1: Generate title from video ID
@router.post("/{video_id}/generate", response_model=TitleResponse)
async def generate_title_endpoint(
    video_id: UUID,
    current_user: UserSignUp = Depends(get_current_user),
    db: Session = Depends(get_database_session)
):
    """
    Generate a title for a video using its transcript
    User sends video ID → get transcript → generate title → return to user
    """
    api_key = get_user_gemini_api_key(current_user.id, db)
    return await generate_title_for_video(
        video_id=video_id,
        user_id=current_user.id,
        db=db,
        user_requirements=None,
        api_key=api_key
    )

# Route 2: Save title when user likes it
@router.post("/{video_id}/save")
async def save_title_endpoint(
    video_id: UUID,
    request: TitleSaveRequest,
    current_user: UserSignUp = Depends(get_current_user),
    db: Session = Depends(get_database_session)
):
    """
    Save the generated title to the video record
    User likes the title → send video ID + title → save to database
    """
    return await save_video_title(
        video_id=video_id,
        user_id=current_user.id,
        title=request.title,
        db=db
    )

# Route 3: Regenerate with user requirements
@router.post("/{video_id}/regenerate-with-requirements", response_model=TitleResponse)
async def regenerate_with_requirements_endpoint(
    video_id: UUID,
    request: RegenerateWithRequirementsRequest,
    current_user: UserSignUp = Depends(get_current_user),
    db: Session = Depends(get_database_session)
):
    """
    Regenerate title with user requirements
    User wants changes → send video ID + requirements → regenerate title
    """
    return await generate_title_for_video(
        video_id=video_id,
        user_id=current_user.id,
        db=db,
        user_requirements=request.user_requirements
    ) 