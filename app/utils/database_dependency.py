"""
Database dependency for FastAPI
"""
from typing import Generator
from sqlmodel import Session
from .my_logger import get_logger

logger = get_logger("DATABASE")

def get_database_session() -> Generator[Session, None, None]:
    from ..config.database import initialize_database_engine

    """Database session dependency"""
    try:
        engine = initialize_database_engine()
        if not engine:
            logger.error("Database engine not available")
            raise Exception("Database connection failed")
        
        with Session(engine) as session:
            yield session
    except Exception as e:
        logger.error(f"Database session error: {e}")
        raise
