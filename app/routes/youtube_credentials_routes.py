from fastapi import APIRouter, Depends, HTTPException
from sqlmodel import Session
from uuid import UUID
from pydantic import BaseModel, Field, validator
from typing import Optional

from ..controllers.youtube_credentials_controller import (
    create_youtube_credentials,
    get_youtube_credentials,
    update_youtube_credentials,
    delete_youtube_credentials,
    get_youtube_credentials_status
)
from ..models.youtube_credentials_model import (
    YouTubeCredentialsCreate,
    YouTubeCredentialsUpdate,
    YouTubeCredentialsResponse,
    YouTubeCredentialsStatus
)
from ..utils.database_dependency import get_database_session
from ..controllers.user_controller import get_current_user
from ..models.user_model import UserSignUp

router = APIRouter(prefix="/youtube-credentials", tags=["youtube-credentials"])

class YouTubeCredentialsCreateRequest(BaseModel):
    client_id: str = Field(..., min_length=10, max_length=200)
    client_secret: str = Field(..., min_length=10, max_length=200)
    
    @validator('client_id')
    def validate_client_id(cls, v):
        if not v or not v.strip():
            raise ValueError("Client ID cannot be empty")
        if len(v.strip()) < 10:
            raise ValueError("Client ID must be at least 10 characters long")
        return v.strip()
    
    @validator('client_secret')
    def validate_client_secret(cls, v):
        if not v or not v.strip():
            raise ValueError("Client secret cannot be empty")
        if len(v.strip()) < 10:
            raise ValueError("Client secret must be at least 10 characters long")
        return v.strip()

class YouTubeCredentialsUpdateRequest(BaseModel):
    client_id: str = Field(..., min_length=10, max_length=200)
    client_secret: str = Field(..., min_length=10, max_length=200)
    is_active: bool = Field(default=True)
    
    @validator('client_id')
    def validate_client_id(cls, v):
        if not v or not v.strip():
            raise ValueError("Client ID cannot be empty")
        if len(v.strip()) < 10:
            raise ValueError("Client ID must be at least 10 characters long")
        return v.strip()
    
    @validator('client_secret')
    def validate_client_secret(cls, v):
        if not v or not v.strip():
            raise ValueError("Client secret cannot be empty")
        if len(v.strip()) < 10:
            raise ValueError("Client secret must be at least 10 characters long")
        return v.strip()

# Route 1: Create YouTube credentials
@router.post("/", response_model=YouTubeCredentialsResponse)
async def create_youtube_credentials_endpoint(
    request: YouTubeCredentialsCreateRequest,
    current_user: UserSignUp = Depends(get_current_user),
    db: Session = Depends(get_database_session)
):
    """
    Create YouTube credentials for the authenticated user
    """
    return create_youtube_credentials(
        user_id=current_user.id,
        client_id=request.client_id,
        client_secret=request.client_secret,
        db=db
    )

# Route 2: Get YouTube credentials
@router.get("/", response_model=Optional[YouTubeCredentialsResponse])
async def get_youtube_credentials_endpoint(
    current_user: UserSignUp = Depends(get_current_user),
    db: Session = Depends(get_database_session)
):
    """
    Get the YouTube credentials for the authenticated user
    Returns null if no credentials are found
    """
    return get_youtube_credentials(
        user_id=current_user.id,
        db=db
    )

# Route 3: Update YouTube credentials
@router.put("/", response_model=YouTubeCredentialsResponse)
async def update_youtube_credentials_endpoint(
    request: YouTubeCredentialsUpdateRequest,
    current_user: UserSignUp = Depends(get_current_user),
    db: Session = Depends(get_database_session)
):
    """
    Update the YouTube credentials for the authenticated user
    """
    return update_youtube_credentials(
        user_id=current_user.id,
        db=db,
        client_id=request.client_id,
        client_secret=request.client_secret,
        is_active=request.is_active
    )

# Route 4: Delete YouTube credentials
@router.delete("/")
async def delete_youtube_credentials_endpoint(
    current_user: UserSignUp = Depends(get_current_user),
    db: Session = Depends(get_database_session)
):
    """
    Delete the YouTube credentials for the authenticated user
    """
    return delete_youtube_credentials(
        user_id=current_user.id,
        db=db
    )

# Route 5: Get YouTube credentials status
@router.get("/status", response_model=YouTubeCredentialsStatus)
async def get_youtube_credentials_status_endpoint(
    current_user: UserSignUp = Depends(get_current_user),
    db: Session = Depends(get_database_session)
):
    """
    Get the status of YouTube credentials for the authenticated user
    """
    return get_youtube_credentials_status(
        user_id=current_user.id,
        db=db
    )
