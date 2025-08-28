from sqlmodel import Session, select
from uuid import UUID
from typing import Optional
from fastapi import HTTPException

from ..models.youtube_credentials_model import (
    YouTubeCredentials,
    YouTubeCredentialsCreate,
    YouTubeCredentialsUpdate,
    YouTubeCredentialsResponse,
    YouTubeCredentialsStatus
)
from ..utils.my_logger import get_logger

logger = get_logger("YOUTUBE_CREDENTIALS_CONTROLLER")

def create_youtube_credentials(
    user_id: UUID,
    client_id: str,
    client_secret: str,
    db: Session
) -> YouTubeCredentialsResponse:
    """Create YouTube credentials for a user"""
    try:
        # Check if user already has credentials
        existing_credentials = db.exec(
            select(YouTubeCredentials).where(YouTubeCredentials.user_id == user_id)
        ).first()
        
        if existing_credentials:
            raise HTTPException(
                status_code=400,
                detail="YouTube credentials already exist for this user. Use update instead."
            )
        
        # Create new credentials
        credentials = YouTubeCredentials(
            user_id=user_id,
            client_id=client_id,
            client_secret=client_secret,
            is_active=True
        )
        
        db.add(credentials)
        db.commit()
        db.refresh(credentials)
        
        logger.info(f"Successfully created YouTube credentials for user_id: {user_id}")
        
        return YouTubeCredentialsResponse(
            id=credentials.id,
            user_id=credentials.user_id,
            client_id_preview=f"{credentials.client_id[:10]}...{credentials.client_id[-4:]}",
            client_secret_preview=f"{credentials.client_secret[:10]}...{credentials.client_secret[-4:]}",
            is_active=credentials.is_active,
            created_at=credentials.created_at,
            updated_at=credentials.updated_at
        )
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error creating YouTube credentials for user_id {user_id}: {e}")
        db.rollback()
        raise HTTPException(
            status_code=500,
            detail="Internal server error while creating YouTube credentials"
        )

def get_youtube_credentials(
    user_id: UUID,
    db: Session
) -> YouTubeCredentialsResponse:
    """Get YouTube credentials for a user"""
    try:
        credentials = db.exec(
            select(YouTubeCredentials).where(YouTubeCredentials.user_id == user_id)
        ).first()
        
        if not credentials:
            raise HTTPException(
                status_code=404,
                detail="YouTube credentials not found for this user"
            )
        
        return YouTubeCredentialsResponse(
            id=credentials.id,
            user_id=credentials.user_id,
            client_id_preview=f"{credentials.client_id[:10]}...{credentials.client_id[-4:]}",
            client_secret_preview=f"{credentials.client_secret[:10]}...{credentials.client_secret[-4:]}",
            is_active=credentials.is_active,
            created_at=credentials.created_at,
            updated_at=credentials.updated_at
        )
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error getting YouTube credentials for user_id {user_id}: {e}")
        raise HTTPException(
            status_code=500,
            detail="Internal server error while getting YouTube credentials"
        )

def update_youtube_credentials(
    user_id: UUID,
    db: Session,
    client_id: Optional[str] = None,
    client_secret: Optional[str] = None,
    is_active: Optional[bool] = None
) -> YouTubeCredentialsResponse:
    """Update YouTube credentials for a user"""
    try:
        credentials = db.exec(
            select(YouTubeCredentials).where(YouTubeCredentials.user_id == user_id)
        ).first()
        
        if not credentials:
            raise HTTPException(
                status_code=404,
                detail="YouTube credentials not found for this user"
            )
        
        # Update fields if provided
        if client_id is not None:
            credentials.client_id = client_id
        if client_secret is not None:
            credentials.client_secret = client_secret
        if is_active is not None:
            credentials.is_active = is_active
        
        db.add(credentials)
        db.commit()
        db.refresh(credentials)
        
        logger.info(f"Successfully updated YouTube credentials for user_id: {user_id}")
        
        return YouTubeCredentialsResponse(
            id=credentials.id,
            user_id=credentials.user_id,
            client_id_preview=f"{credentials.client_id[:10]}...{credentials.client_id[-4:]}",
            client_secret_preview=f"{credentials.client_secret[:10]}...{credentials.client_secret[-4:]}",
            is_active=credentials.is_active,
            created_at=credentials.created_at,
            updated_at=credentials.updated_at
        )
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error updating YouTube credentials for user_id {user_id}: {e}")
        db.rollback()
        raise HTTPException(
            status_code=500,
            detail="Internal server error while updating YouTube credentials"
        )

def delete_youtube_credentials(
    user_id: UUID,
    db: Session
) -> dict:
    """Delete YouTube credentials for a user"""
    try:
        credentials = db.exec(
            select(YouTubeCredentials).where(YouTubeCredentials.user_id == user_id)
        ).first()
        
        if not credentials:
            raise HTTPException(
                status_code=404,
                detail="YouTube credentials not found for this user"
            )
        
        db.delete(credentials)
        db.commit()
        
        logger.info(f"Successfully deleted YouTube credentials for user_id: {user_id}")
        
        return {
            "success": True,
            "message": "YouTube credentials deleted successfully"
        }
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error deleting YouTube credentials for user_id {user_id}: {e}")
        db.rollback()
        raise HTTPException(
            status_code=500,
            detail="Internal server error while deleting YouTube credentials"
        )

def get_youtube_credentials_status(
    user_id: UUID,
    db: Session
) -> YouTubeCredentialsStatus:
    """Get YouTube credentials status for a user"""
    try:
        credentials = db.exec(
            select(YouTubeCredentials).where(YouTubeCredentials.user_id == user_id)
        ).first()
        
        if not credentials:
            return YouTubeCredentialsStatus(
                has_credentials=False,
                is_active=False,
                client_id_preview=None,
                client_secret_preview=None
            )
        
        return YouTubeCredentialsStatus(
            has_credentials=True,
            is_active=credentials.is_active,
            client_id_preview=f"{credentials.client_id[:10]}...{credentials.client_id[-4:]}",
            client_secret_preview=f"{credentials.client_secret[:10]}...{credentials.client_secret[-4:]}"
        )
        
    except Exception as e:
        logger.error(f"Error getting YouTube credentials status for user_id {user_id}: {e}")
        raise HTTPException(
            status_code=500,
            detail="Internal server error while getting YouTube credentials status"
        )

def get_user_youtube_credentials(
    user_id: UUID,
    db: Session
) -> Optional[YouTubeCredentials]:
    """Get raw YouTube credentials for internal use (returns full credentials)"""
    try:
        credentials = db.exec(
            select(YouTubeCredentials).where(
                YouTubeCredentials.user_id == user_id,
                YouTubeCredentials.is_active == True
            )
        ).first()
        
        return credentials
        
    except Exception as e:
        logger.error(f"Error getting raw YouTube credentials for user_id {user_id}: {e}")
        return None
