from fastapi import APIRouter, Depends, HTTPException
from sqlmodel import Session
from uuid import UUID
from pydantic import BaseModel, Field, validator

from ..controllers.gemini_key_controller import (
    create_gemini_key,
    get_gemini_key,
    update_gemini_key,
    delete_gemini_key,
    get_gemini_key_status
)
from ..models.gemini_key_model import (
    GeminiKeyCreate,
    GeminiKeyUpdate,
    GeminiKeyResponse,
    GeminiKeyStatus
)
from ..utils.database_dependency import get_database_session
from ..controllers.user_controller import get_current_user
from ..models.user_model import UserSignUp

router = APIRouter(prefix="/gemini-keys", tags=["gemini-keys"])

class GeminiKeyCreateRequest(BaseModel):
    api_key: str = Field(..., min_length=10, max_length=1000)
    
    @validator('api_key')
    def validate_api_key(cls, v):
        if not v or not v.strip():
            raise ValueError("API key cannot be empty")
        if len(v.strip()) < 10:
            raise ValueError("API key must be at least 10 characters long")
        return v.strip()

class GeminiKeyUpdateRequest(BaseModel):
    api_key: str = Field(..., min_length=10, max_length=1000)
    is_active: bool = Field(default=True)
    
    @validator('api_key')
    def validate_api_key(cls, v):
        if not v or not v.strip():
            raise ValueError("API key cannot be empty")
        if len(v.strip()) < 10:
            raise ValueError("API key must be at least 10 characters long")
        return v.strip()

# Route 1: Create Gemini API key
@router.post("/", response_model=GeminiKeyResponse)
async def create_gemini_key_endpoint(
    request: GeminiKeyCreateRequest,
    current_user: UserSignUp = Depends(get_current_user),
    db: Session = Depends(get_database_session)
):
    """
    Create a new Gemini API key for the authenticated user
    """
    return create_gemini_key(
        user_id=current_user.id,
        api_key=request.api_key,
        db=db
    )

# Route 2: Get Gemini API key
@router.get("/", response_model=GeminiKeyResponse)
async def get_gemini_key_endpoint(
    current_user: UserSignUp = Depends(get_current_user),
    db: Session = Depends(get_database_session)
):
    """
    Get the Gemini API key for the authenticated user
    """
    return get_gemini_key(
        user_id=current_user.id,
        db=db
    )

# Route 3: Update Gemini API key
@router.put("/", response_model=GeminiKeyResponse)
async def update_gemini_key_endpoint(
    request: GeminiKeyUpdateRequest,
    current_user: UserSignUp = Depends(get_current_user),
    db: Session = Depends(get_database_session)
):
    """
    Update the Gemini API key for the authenticated user
    """
    return update_gemini_key(
        user_id=current_user.id,
        api_key=request.api_key,
        is_active=request.is_active,
        db=db
    )

# Route 4: Delete Gemini API key
@router.delete("/")
async def delete_gemini_key_endpoint(
    current_user: UserSignUp = Depends(get_current_user),
    db: Session = Depends(get_database_session)
):
    """
    Delete the Gemini API key for the authenticated user
    """
    return delete_gemini_key(
        user_id=current_user.id,
        db=db
    )

# Route 5: Get Gemini API key status
@router.get("/status", response_model=GeminiKeyStatus)
async def get_gemini_key_status_endpoint(
    current_user: UserSignUp = Depends(get_current_user),
    db: Session = Depends(get_database_session)
):
    """
    Get the status of Gemini API key for the authenticated user
    """
    return get_gemini_key_status(
        user_id=current_user.id,
        db=db
    ) 