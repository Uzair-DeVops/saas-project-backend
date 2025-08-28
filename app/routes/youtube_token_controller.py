from fastapi import APIRouter, Depends, HTTPException, status
from sqlmodel import Session
from fastapi.responses import HTMLResponse
from typing import Optional
from uuid import UUID
import os
from fastapi.templating import Jinja2Templates

templates = Jinja2Templates(directory="app/views")

from ..models import GoogleToken, TokenStatus, CreateTokenResponse, RefreshTokenResponse
from ..controllers.youtube_token_controller import (
    create_token,
    handle_oauth_callback,
    refresh_token,
    get_token_status,
    get_google_token_by_user_id,
    get_google_token_after_inspect_and_refresh
)
from ..models.user_model import UserSignUp
from ..utils.auth_utils import get_current_user_from_token
from ..utils.database_dependency import get_database_session
from ..controllers.user_controller import get_current_user

router = APIRouter(prefix="/youtube", tags=["Youtube"])

@router.post("/create-token", response_model=CreateTokenResponse)
async def create_oauth_token(
    db: Session = Depends(get_database_session),
    current_user: UserSignUp = Depends(get_current_user)
):
    """
    Create OAuth token - opens browser for Google authentication.
    """
    try:
        result = create_token(current_user.id, db)
        return result
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to create OAuth token: {str(e)}")

@router.get("/oauth/callback", response_class=HTMLResponse)
async def oauth_callback(
    code: Optional[str] = None,
    state: Optional[str] = None,
    error: Optional[str] = None,
    error_description: Optional[str] = None,
    db: Session = Depends(get_database_session)
):
    """Route 2: OAuth callback - exchanges authorization code for tokens and stores them."""
    if error:
        return templates.TemplateResponse('error.html', {
            'request': {},
            'error': error, 
            'error_description': error_description or "Unknown error"
        })
    
    if not code:
        return templates.TemplateResponse('error.html', {
            'request': {},
            'error': "No authorization code received", 
            'error_description': "The OAuth process did not return an authorization code"
        })
    
    try:
        # Extract user_id from state parameter
        if state and state.startswith("user_"):
            try:
                user_id = UUID(state.split("_")[1])
            except ValueError:
                return templates.TemplateResponse('error.html', {
                    'request': {},
                    'error': "Invalid user ID format", 
                    'error_description': "The user ID in the state parameter is not a valid UUID"
                })
        else:
            return templates.TemplateResponse('error.html', {
                'request': {},
                'error': "Invalid state parameter", 
                'error_description': "The OAuth state parameter is missing or invalid"
            })
        
        # Handle OAuth callback and save tokens
        handle_oauth_callback(code, user_id, db, state)
        
        # Return success HTML page from template
        return templates.TemplateResponse('oauth_success.html', {
            'request': {},
            'service_name': 'Google Calendar',
            'service_logo': '/static/calendar-logo.png'
        })
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.post("/refresh-token", response_model=RefreshTokenResponse)
async def refresh_oauth_token(
    db: Session = Depends(get_database_session),
    current_user: UserSignUp = Depends(get_current_user)
):
    """
    Manually refresh OAuth token for the current user.
    """
    try:
        result = refresh_token(current_user.id, db)
        return result
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Token refresh failed: {str(e)}")

@router.get("/status", response_model=TokenStatus)
async def get_token_status_endpoint(
    db: Session = Depends(get_database_session),
    current_user: UserSignUp = Depends(get_current_user)
):
    """
    Get current token status for the authenticated user.
    """
    try:
        result = get_token_status(current_user.id, db)
        return result
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to get token status: {str(e)}")

@router.get("/{user_id}", response_model=Optional[GoogleToken])
def get_token(user_id: UUID, db: Session = Depends(get_database_session)):
    """
    Get Google token for a specific user ID.
    """
    token = get_google_token_by_user_id(db, user_id)
    if not token:
        raise HTTPException(status_code=404, detail="Token not found")
    return token

@router.get("/{user_id}/refreshed", response_model=Optional[GoogleToken])
def get_refreshed_token(user_id: UUID, db: Session = Depends(get_database_session)):
    """
    Get Google token with automatic refresh if expired.
    This endpoint is used by the standalone calendar server.
    """
    try:
        # This function handles refresh automatically
        refreshed_tokens = get_google_token_after_inspect_and_refresh(user_id, db)
        
        if not refreshed_tokens:
            raise HTTPException(status_code=404, detail="No tokens found for user")
        
        # Convert back to GoogleToken model
        token = get_google_token_by_user_id(db, user_id)
        if not token:
            raise HTTPException(status_code=404, detail="Token not found")
        
        return token
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Token refresh failed: {str(e)}") 