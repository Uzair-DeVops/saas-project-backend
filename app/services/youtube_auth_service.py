import os
import pickle
from typing import Optional, Dict, Any
from uuid import UUID
from google_auth_oauthlib.flow import InstalledAppFlow
from google.auth.transport.requests import Request
from googleapiclient.discovery import build
from google.oauth2.credentials import Credentials
from sqlmodel import Session

from ..controllers.youtube_token_controller import get_google_token_after_inspect_and_refresh
from ..controllers.youtube_credentials_controller import get_user_youtube_credentials
from ..utils.my_logger import get_logger

logger = get_logger("YOUTUBE_AUTH_SERVICE")

# YouTube API scopes - using the same scopes as your existing service
SCOPES = [
    'https://www.googleapis.com/auth/youtube',
    'https://www.googleapis.com/auth/youtube.readonly',
    'https://www.googleapis.com/auth/youtube.upload',
    'https://www.googleapis.com/auth/youtube.force-ssl',
    'https://www.googleapis.com/auth/userinfo.email',
    'https://www.googleapis.com/auth/userinfo.profile',
    'openid',
    'https://www.googleapis.com/auth/bigquery',
    'https://www.googleapis.com/auth/cloud-platform',
    'https://www.googleapis.com/auth/bigquery.readonly',
    'https://www.googleapis.com/auth/cloud-platform.read-only',
    'https://www.googleapis.com/auth/devstorage.full_control',
    'https://www.googleapis.com/auth/devstorage.read_only',
    'https://www.googleapis.com/auth/devstorage.read_write'
]

def get_youtube_client(user_id: UUID, db: Session) -> Optional[Any]:
    """
    Get authenticated YouTube API client for a specific user.
    
    Args:
        user_id: UUID of the user
        db: Database session
    
    Returns:
        googleapiclient.discovery.Resource: Authenticated YouTube API client or None if authentication fails
    """
    try:
        # Get fresh tokens (with auto-refresh if needed)
        tokens = get_google_token_after_inspect_and_refresh(user_id, db)
        
        if not tokens:
            logger.error(f"No valid tokens found for user_id: {user_id}")
            return None
        
        # Get user's YouTube credentials
        user_credentials = get_user_youtube_credentials(user_id, db)
        if not user_credentials:
            logger.error(f"No YouTube credentials found for user_id: {user_id}")
            return None
        
        # Create credentials from tokens
        creds = Credentials(
            token=tokens.get('access_token'),
            refresh_token=tokens.get('refresh_token'),
            token_uri="https://oauth2.googleapis.com/token",
            client_id=user_credentials.client_id,
            client_secret=user_credentials.client_secret,
            scopes=SCOPES
        )
        
        # Build and return YouTube API client
        youtube_service = build('youtube', 'v3', credentials=creds)
        logger.info(f"Successfully created YouTube client for user_id: {user_id}")
        
        return youtube_service
        
    except Exception as e:
        logger.error(f"Error creating YouTube client for user_id {user_id}: {e}")
        return None 