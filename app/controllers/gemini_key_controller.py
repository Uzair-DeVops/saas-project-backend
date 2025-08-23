from typing import Optional
from uuid import UUID
from sqlmodel import Session, select
from fastapi import HTTPException
from ..models.gemini_key_model import (
    GeminiKey, 
    GeminiKeyCreate, 
    GeminiKeyUpdate, 
    GeminiKeyResponse, 
    GeminiKeyStatus
)
from ..utils.my_logger import get_logger

logger = get_logger("GEMINI_KEY_CONTROLLER")

def create_gemini_key(
    user_id: UUID,
    api_key: str,
    db: Session
) -> GeminiKeyResponse:
    """
    Create a new Gemini API key for a user
    """
    try:
        logger.info(f"Creating Gemini API key for user {user_id}")
        
        # Check if user already has a key
        existing_key = db.exec(
            select(GeminiKey).where(GeminiKey.user_id == user_id)
        ).first()
        
        if existing_key:
            logger.warning(f"User {user_id} already has a Gemini API key")
            raise HTTPException(
                status_code=400, 
                detail="User already has a Gemini API key. Use update instead."
            )
        
        # Create new key
        gemini_key = GeminiKey(
            user_id=user_id,
            api_key=api_key
        )
        
        db.add(gemini_key)
        db.commit()
        db.refresh(gemini_key)
        
        logger.info(f"Gemini API key created successfully for user {user_id}")
        
        return GeminiKeyResponse(
            id=gemini_key.id,
            user_id=gemini_key.user_id,
            api_key_preview=_get_key_preview(gemini_key.api_key),
            is_active=gemini_key.is_active,
            created_at=gemini_key.created_at,
            updated_at=gemini_key.updated_at
        )
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error creating Gemini API key for user {user_id}: {e}")
        db.rollback()
        raise HTTPException(status_code=500, detail="Failed to create Gemini API key")

def get_gemini_key(
    user_id: UUID,
    db: Session
) -> GeminiKeyResponse:
    """
    Get Gemini API key for a user
    """
    try:
        logger.info(f"Fetching Gemini API key for user {user_id}")
        
        gemini_key = db.exec(
            select(GeminiKey).where(GeminiKey.user_id == user_id)
        ).first()
        
        if not gemini_key:
            logger.warning(f"No Gemini API key found for user {user_id}")
            raise HTTPException(
                status_code=404, 
                detail="Gemini API key not found"
            )
        
        return GeminiKeyResponse(
            id=gemini_key.id,
            user_id=gemini_key.user_id,
            api_key_preview=_get_key_preview(gemini_key.api_key),
            is_active=gemini_key.is_active,
            created_at=gemini_key.created_at,
            updated_at=gemini_key.updated_at
        )
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error fetching Gemini API key for user {user_id}: {e}")
        raise HTTPException(status_code=500, detail="Failed to fetch Gemini API key")

def update_gemini_key(
    user_id: UUID,
    api_key: Optional[str] = None,
    is_active: Optional[bool] = None,
    db: Session = None
) -> GeminiKeyResponse:
    """
    Update Gemini API key for a user
    """
    try:
        logger.info(f"Updating Gemini API key for user {user_id}")
        
        gemini_key = db.exec(
            select(GeminiKey).where(GeminiKey.user_id == user_id)
        ).first()
        
        if not gemini_key:
            logger.warning(f"No Gemini API key found for user {user_id}")
            raise HTTPException(
                status_code=404, 
                detail="Gemini API key not found"
            )
        
        # Update fields if provided
        if api_key is not None:
            gemini_key.api_key = api_key
        if is_active is not None:
            gemini_key.is_active = is_active
        
        db.add(gemini_key)
        db.commit()
        db.refresh(gemini_key)
        
        logger.info(f"Gemini API key updated successfully for user {user_id}")
        
        return GeminiKeyResponse(
            id=gemini_key.id,
            user_id=gemini_key.user_id,
            api_key_preview=_get_key_preview(gemini_key.api_key),
            is_active=gemini_key.is_active,
            created_at=gemini_key.created_at,
            updated_at=gemini_key.updated_at
        )
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error updating Gemini API key for user {user_id}: {e}")
        db.rollback()
        raise HTTPException(status_code=500, detail="Failed to update Gemini API key")

def delete_gemini_key(
    user_id: UUID,
    db: Session
) -> dict:
    """
    Delete Gemini API key for a user
    """
    try:
        logger.info(f"Deleting Gemini API key for user {user_id}")
        
        gemini_key = db.exec(
            select(GeminiKey).where(GeminiKey.user_id == user_id)
        ).first()
        
        if not gemini_key:
            logger.warning(f"No Gemini API key found for user {user_id}")
            raise HTTPException(
                status_code=404, 
                detail="Gemini API key not found"
            )
        
        db.delete(gemini_key)
        db.commit()
        
        logger.info(f"Gemini API key deleted successfully for user {user_id}")
        
        return {
            "success": True,
            "message": "Gemini API key deleted successfully"
        }
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error deleting Gemini API key for user {user_id}: {e}")
        db.rollback()
        raise HTTPException(status_code=500, detail="Failed to delete Gemini API key")

def get_gemini_key_status(
    user_id: UUID,
    db: Session
) -> GeminiKeyStatus:
    """
    Get Gemini API key status for a user
    """
    try:
        logger.info(f"Checking Gemini API key status for user {user_id}")
        
        gemini_key = db.exec(
            select(GeminiKey).where(GeminiKey.user_id == user_id)
        ).first()
        
        if not gemini_key:
            return GeminiKeyStatus(
                has_key=False,
                is_active=False,
                key_preview=None
            )
        
        return GeminiKeyStatus(
            has_key=True,
            is_active=gemini_key.is_active,
            key_preview=_get_key_preview(gemini_key.api_key)
        )
        
    except Exception as e:
        logger.error(f"Error checking Gemini API key status for user {user_id}: {e}")
        raise HTTPException(status_code=500, detail="Failed to check Gemini API key status")

def get_gemini_api_key_for_user(
    user_id: UUID,
    db: Session
) -> Optional[str]:
    """
    Get the actual Gemini API key for a user (for internal use in services)
    """
    try:
        gemini_key = db.exec(
            select(GeminiKey).where(
                GeminiKey.user_id == user_id,
                GeminiKey.is_active == True
            )
        ).first()
        
        return gemini_key.api_key if gemini_key else None
        
    except Exception as e:
        logger.error(f"Error getting Gemini API key for user {user_id}: {e}")
        return None

def _get_key_preview(api_key: str) -> str:
    """
    Create a preview of the API key showing first 10 and last 4 characters
    """
    if len(api_key) <= 14:
        return "*" * len(api_key)
    
    return f"{api_key[:10]}...{api_key[-4:]}" 