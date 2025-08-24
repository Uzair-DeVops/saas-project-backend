from typing import Optional
from uuid import UUID
from sqlmodel import Session
from ..controllers.gemini_key_controller import get_gemini_api_key_for_user
from ..utils.database_dependency import get_database_session
from ..utils.my_logger import get_logger

logger = get_logger("GEMINI_DEPENDENCY")

def get_user_gemini_api_key(user_id: UUID, db: Session) -> Optional[str]:
    """
    Get the Gemini API key for a specific user.
    Returns None if no key is found or if the key is inactive.
    
    Args:
        user_id: The user's UUID
        db: Database session
        
    Returns:
        The user's Gemini API key or None if not found/inactive
    """
    try:
        api_key = get_gemini_api_key_for_user(user_id, db)
        
        if not api_key:
            logger.warning(f"No active Gemini API key found for user {user_id}")
            return None
            
        logger.info(f"Retrieved Gemini API key for user {user_id}")
        return api_key
        
    except Exception as e:
        logger.error(f"Error retrieving Gemini API key for user {user_id}: {e}")
        return None

def get_gemini_api_key_with_fallback(user_id: UUID, db: Session, fallback_key: str = None) -> str:
    """
    Get the user's Gemini API key with a fallback to a default key.
    
    Args:
        user_id: The user's UUID
        db: Database session
        fallback_key: Fallback API key if user doesn't have one
        
    Returns:
        The user's Gemini API key or the fallback key
    """
    user_key = get_user_gemini_api_key(user_id, db)
    
    if user_key:
        return user_key
    
    if fallback_key:
        logger.info(f"Using fallback Gemini API key for user {user_id}")
        return fallback_key
    
    # Try to get from environment as last resort
    import os
    env_key = os.getenv("GEMINI_API_KEY")
    
    if env_key:
        logger.info(f"Using environment Gemini API key for user {user_id}")
        return env_key
    
    raise ValueError("No Gemini API key available") 