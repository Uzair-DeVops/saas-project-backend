import requests
import webbrowser
import json
import os
from datetime import datetime, timedelta
from typing import Optional, Dict, Any
from uuid import UUID
from sqlmodel import Session, select
from ..models import GoogleToken, TokenResponse, TokenStatus, OAuthCallbackResponse, CreateTokenResponse, RefreshTokenResponse, StoredTokens
from ..utils.database_dependency import get_database_session
from ..utils.my_logger import get_logger
from ..controllers.youtube_credentials_controller import get_user_youtube_credentials

logger = get_logger("YOUTUBE_TOKEN_SERVICE")

import secrets
from urllib.parse import urlencode

# Configuration
REDIRECT_URI = "https://saas-backend.duckdns.org/youtube/oauth/callback"

# Google API endpoints
GOOGLE_AUTH_URL = "https://accounts.google.com/o/oauth2/auth"
GOOGLE_TOKEN_URL = "https://oauth2.googleapis.com/token"

def get_google_auth_url(user_id: UUID, db: Session, redirect_uri: str = None, state: str = "user_1") -> str:
    """Generate the Google OAuth2 authorization URL."""
    # Get user's YouTube credentials
    credentials = get_user_youtube_credentials(user_id, db)
    if not credentials:
        raise ValueError(f"No YouTube credentials found for user_id: {user_id}")
    
    if redirect_uri is None:
        redirect_uri = REDIRECT_URI
    
    scopes = [
        "https://www.googleapis.com/auth/youtube",
        "https://www.googleapis.com/auth/youtube.readonly",
        "https://www.googleapis.com/auth/youtube.upload",
        "https://www.googleapis.com/auth/youtube.force-ssl",
        "https://www.googleapis.com/auth/userinfo.email",
        "https://www.googleapis.com/auth/userinfo.profile",
        "openid",
        "https://www.googleapis.com/auth/bigquery",
        "https://www.googleapis.com/auth/cloud-platform",
        "https://www.googleapis.com/auth/bigquery.readonly",
        "https://www.googleapis.com/auth/cloud-platform.read-only",
        "https://www.googleapis.com/auth/devstorage.full_control",
        "https://www.googleapis.com/auth/devstorage.read_only",
        "https://www.googleapis.com/auth/devstorage.read_write"
    ]
    
    params = {
        "response_type": "code",
        "client_id": credentials.client_id,
        "redirect_uri": redirect_uri,
        "scope": " ".join(scopes),
        "state": state,
        "access_type": "offline",
        "prompt": "consent"  # keep refresh-token behavior
    }
    
    # Use urlencode to properly encode the parameters
    query_string = urlencode(params)
    return f"{GOOGLE_AUTH_URL}?{query_string}"

def exchange_code_for_tokens(authorization_code: str, user_id: UUID, db: Session) -> Optional[Dict[str, Any]]:
    """Exchange authorization code for access tokens."""
    # Get user's YouTube credentials
    credentials = get_user_youtube_credentials(user_id, db)
    if not credentials:
        logger.error(f"No YouTube credentials found for user_id: {user_id}")
        return None
    
    data = {
        "grant_type": "authorization_code",
        "code": authorization_code,
        "client_id": credentials.client_id,
        "client_secret": credentials.client_secret,
        "redirect_uri": REDIRECT_URI
    }
    
    headers = {"Content-Type": "application/x-www-form-urlencoded"}
    
    try:
        response = requests.post(GOOGLE_TOKEN_URL, data=data, headers=headers)
        logger.info(f"DEBUG: Google token exchange response status: {response.status_code}")
        logger.info(f"DEBUG: Google token exchange response: {response.text}")
        response.raise_for_status()
        return response.json()
    except requests.exceptions.RequestException as e:
        logger.error(f"Error exchanging code for tokens: {e}")
        if hasattr(e, 'response') and e.response is not None:
            logger.error(f"DEBUG: Error response: {e.response.text}")
        return None

def refresh_access_token(refresh_token: str, user_id: UUID, db: Session) -> Optional[Dict[str, Any]]:
    """Refresh access token using refresh token."""
    # Get user's YouTube credentials
    credentials = get_user_youtube_credentials(user_id, db)
    if not credentials:
        logger.error(f"No YouTube credentials found for user_id: {user_id}")
        return None
    
    data = {
        "grant_type": "refresh_token",
        "refresh_token": refresh_token,
        "client_id": credentials.client_id,
        "client_secret": credentials.client_secret
    }
    
    headers = {"Content-Type": "application/x-www-form-urlencoded"}
    
    try:
        response = requests.post(GOOGLE_TOKEN_URL, data=data, headers=headers)
        response.raise_for_status()
        return response.json()
    except requests.exceptions.RequestException as e:
        logger.error(f"Error refreshing token: {e}")
        return None

def save_tokens_to_db(tokens: Dict[str, Any], user_id: UUID, db: Session) -> bool:
    """Save tokens to database with expiration timestamp."""
    try:
        logger.info(f"DEBUG: Google API response tokens keys: {list(tokens.keys())}")
        # Add expiration timestamp
        if 'expires_in' in tokens:
            expires_at = datetime.now() + timedelta(seconds=tokens['expires_in'])
            tokens['expires_at'] = expires_at.isoformat()
        else:
            tokens['expires_at'] = datetime.now().isoformat()
        
        # Check if token already exists for this user
        existing_token = get_google_token_by_user_id(db, user_id)
        
        if existing_token:
            # Update existing token
            for key, value in tokens.items():
                if hasattr(existing_token, key):
                    setattr(existing_token, key, value)
            db.add(existing_token)
        else:
            # Create new token
            from ..models import GoogleToken
            new_token = GoogleToken(
                user_id=user_id,
                access_token=tokens['access_token'],
                refresh_token=tokens['refresh_token'],
                token_type=tokens['token_type'],
                expires_in=tokens['expires_in'],
                scope=tokens['scope'],
                expires_at=tokens['expires_at']
            )
            db.add(new_token)
        
        db.commit()
        return True
    except Exception as e:
        logger.error(f"Error saving tokens to database: {e}")
        db.rollback()
        return False

def load_tokens_from_db(user_id: UUID, db: Session) -> Optional[Dict[str, Any]]:
    """Load tokens from database."""
    try:
        token = get_google_token_by_user_id(db, user_id)
        if not token:
            return None
        
        return {
            'access_token': token.access_token,
            'refresh_token': token.refresh_token,
            'token_type': token.token_type,
            'expires_in': token.expires_in,
            'scope': token.scope,
            'expires_at': token.expires_at,
            'refresh_token_expires_in': token.refresh_token_expires_in
        }
    except Exception as e:
        logger.error(f"Error loading tokens from database: {e}")
        return None

def get_google_token_by_user_id(db: Session, user_id: UUID):
    """Get Google token by user ID."""
    from ..models import GoogleToken
    statement = select(GoogleToken).where(GoogleToken.user_id == user_id)
    return db.exec(statement).first()

def is_token_expired(tokens: Dict[str, Any]) -> bool:
    """Check if access token is expired."""
    if 'expires_at' not in tokens:
        return True
    
    try:
        expires_at = datetime.fromisoformat(tokens['expires_at'])
        return datetime.now() >= expires_at
    except:
        return True

def create_token(user_id: UUID, db: Session) -> CreateTokenResponse:
    """Create token - opens browser for OAuth authentication."""
    # Generate a stronger state parameter
    state = f"user_{str(user_id)}"
    auth_url = get_google_auth_url(user_id, db, REDIRECT_URI, state)
    
    # Open browser
    webbrowser.open(auth_url)
    
    return CreateTokenResponse(
        message="Browser opened for OAuth authentication",
        auth_url=auth_url,
        instructions="Complete authentication in browser, then check /oauth/callback for the authorization code"
    )

def handle_oauth_callback(code: str, user_id: UUID, db: Session, state: Optional[str] = None) -> OAuthCallbackResponse:
    """Handle OAuth callback - exchanges authorization code for tokens and stores them."""
    # Exchange code for tokens
    tokens = exchange_code_for_tokens(code, user_id, db)
    
    if not tokens:
        raise Exception("Failed to exchange code for tokens")
    
    # Save tokens to database
    if save_tokens_to_db(tokens, user_id, db):
        return OAuthCallbackResponse(
            success=True,
            message="OAuth successful! Tokens saved to database.",
            authorization_code=code,
            state=state,
            tokens_saved=True,
            access_token_preview=tokens.get('access_token', '')[:20] + "..." if tokens.get('access_token') else None
        )
    else:
        raise Exception("Failed to save tokens to database")

def refresh_token(user_id: UUID, db: Session) -> RefreshTokenResponse:
    """Refresh token - checks if token is expired and refreshes if needed."""
    # Load current tokens
    tokens = load_tokens_from_db(user_id, db)
    
    if not tokens:
        raise Exception("No tokens found. Please create tokens first using /create-token")
    
    # Check if token is expired
    if not is_token_expired(tokens):
        return RefreshTokenResponse(
            message="Token is still valid",
            expires_at=tokens.get('expires_at'),
            token_preview=tokens.get('access_token', '')[:20] + "..." if tokens.get('access_token') else None
        )
    
    # Token is expired, refresh it
    refresh_token_value = tokens.get('refresh_token')
    if not refresh_token_value:
        raise Exception("No refresh token found")
    
    new_tokens = refresh_access_token(refresh_token_value, user_id, db)
    if not new_tokens:
        raise Exception("Failed to refresh token")
    
    # Save new tokens to database
    if save_tokens_to_db(new_tokens, user_id, db):
        return RefreshTokenResponse(
            message="Token refreshed successfully",
            expires_at=new_tokens.get('expires_at'),
            token_preview=new_tokens.get('access_token', '')[:20] + "..." if new_tokens.get('access_token') else None
        )
    else:
        raise Exception("Failed to save refreshed tokens")

def get_token_status(user_id: UUID, db: Session) -> TokenStatus:
    """Get current token status."""
    tokens = load_tokens_from_db(user_id, db)
    
    if not tokens:
        return TokenStatus(
            status="no_tokens",
            message="No tokens found. Use /create-token to authenticate.",
            has_access_token=False,
            has_refresh_token=False,
            expires_at=None,
            token_type=None,
            scope=None,
            access_token_preview=None
        )
    
    is_expired = is_token_expired(tokens)
    
    return TokenStatus(
        status="expired" if is_expired else "valid",
        message="Token is expired" if is_expired else "Token is valid",
        has_access_token="access_token" in tokens,
        has_refresh_token="refresh_token" in tokens,
        expires_at=tokens.get('expires_at'),
        token_type=tokens.get('token_type'),
        scope=tokens.get('scope'),
        access_token_preview=tokens.get('access_token', '')[:20] + "..." if tokens.get('access_token') else None
    )

def get_google_token_after_inspect_and_refresh(user_id: UUID, db: Session) -> Optional[Dict[str, Any]]:
    """
    Automatic token refresh function similar to calendar implementation.
    
    1. Loads tokens for user_id
    2. Checks if token is expired
    3. Automatically refreshes if expired and saves to database
    4. Returns ready-to-use tokens with user_id or None if no tokens exist
    """
    try:
        # Load current tokens from database
        tokens = load_tokens_from_db(user_id, db)
        
        if not tokens:
            logger.error(f"No Google tokens found for user_id: {user_id}")
            return None
        
        # Check if token is expired
        if is_token_expired(tokens):
            logger.error(f"Google token expired for user_id: {user_id} - refreshing automatically...")
            
            # Get refresh token
            refresh_token_value = tokens.get('refresh_token')
            if not refresh_token_value:
                logger.error(f"No refresh token found for user_id: {user_id}")
                return None
            
            # Refresh the token
            new_tokens = refresh_access_token(refresh_token_value, user_id, db)
            
            if not new_tokens:
                logger.error(f"Failed to refresh Google token for user_id: {user_id}")
                return None
            
            # Save new tokens to database
            if save_tokens_to_db(new_tokens, user_id, db):
                logger.info(f"Successfully refreshed and saved Google tokens for user_id: {user_id}")
                # Add user_id to the returned tokens
                new_tokens['user_id'] = str(user_id)
                return new_tokens
            else:
                logger.error(f"Failed to save refreshed Google tokens for user_id: {user_id}")
                return None
        else:
            logger.info(f"Google token is still valid for user_id: {user_id}")
            # Add user_id to the returned tokens
            tokens['user_id'] = str(user_id)
            return tokens
            
    except Exception as e:
        logger.error(f"Error in get_google_token_after_inspect_and_refresh for user_id {user_id}: {e}")
        return None

def get_access_token(user_id: UUID, db: Session) -> Optional[str]:
    """Get access token for a specific user ID."""
    try:
        # First try to get fresh tokens (with auto-refresh if needed)
        tokens = get_google_token_after_inspect_and_refresh(user_id, db)
        
        if tokens and 'access_token' in tokens:
            return tokens['access_token']
        
        return None
    except Exception as e:
        logger.error(f"Error getting access token for user_id {user_id}: {e}")
        return None 