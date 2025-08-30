"""
YouTube Cache Service - Implements smart caching strategies to reduce API calls
"""
from typing import Dict, Any, Optional, List
from datetime import datetime, timedelta
from sqlmodel import Session, select
from ..models.dashboard_overview_model import DashboardOverview
from ..models.dashboard_playlist_model import DashboardPlaylist
from ..models.dashboard_video_model import DashboardVideo
from ..models.dashboard_playlist_video_model import DashboardPlaylistVideo
from ..utils.my_logger import get_logger

logger = get_logger("YOUTUBE_CACHE_SERVICE")

class YouTubeCacheService:
    """Service for managing YouTube API data caching"""
    
    # Cache persists until user explicitly requests refresh
    # No automatic expiration - user controls when to get fresh data
    
    @staticmethod
    def is_cache_valid(cached_data: Any, cache_type: str) -> bool:
        """Check if cached data is still valid - cache persists until user refresh"""
        if not cached_data:
            return False
            
        # Cache is always valid if it exists - no automatic expiration
        # User must explicitly request refresh to get fresh data
        return True
    
    @staticmethod
    def get_overview_cache(user_id: str, db: Session) -> Optional[DashboardOverview]:
        """Get cached overview data"""
        try:
            # Convert string user_id to UUID
            from uuid import UUID
            user_uuid = UUID(user_id)
            
            statement = select(DashboardOverview).where(
                DashboardOverview.user_id == user_uuid
            ).order_by(DashboardOverview.data_updated_at.desc())
            
            cached_data = db.exec(statement).first()
            
            if cached_data and YouTubeCacheService.is_cache_valid(cached_data, 'overview'):
                logger.info(f"Using cached overview data for user {user_id}")
                return cached_data
            
            return None
            
        except Exception as e:
            logger.error(f"Error getting overview cache: {e}")
            return None
    
    @staticmethod
    def get_playlists_cache(user_id: str, db: Session) -> Optional[List[DashboardPlaylist]]:
        """Get cached playlists data"""
        try:
            # Convert string user_id to UUID
            from uuid import UUID
            user_uuid = UUID(user_id)
            
            statement = select(DashboardPlaylist).where(
                DashboardPlaylist.user_id == user_uuid
            ).order_by(DashboardPlaylist.data_updated_at.desc())
            
            cached_data = db.exec(statement).all()
            
            if cached_data:
                # Check if any playlist data is recent enough
                latest_update = max(
                    playlist.data_updated_at for playlist in cached_data
                )
                
                if YouTubeCacheService.is_cache_valid(
                    type('MockData', (), {'data_updated_at': latest_update})(), 'playlists'
                ):
                    logger.info(f"Using cached playlists data for user {user_id}")
                    return cached_data
            
            return None
            
        except Exception as e:
            logger.error(f"Error getting playlists cache: {e}")
            return None
    
    @staticmethod
    def get_videos_cache(user_id: str, db: Session) -> Optional[List[DashboardVideo]]:
        """Get cached videos data"""
        try:
            # Convert string user_id to UUID
            from uuid import UUID
            user_uuid = UUID(user_id)
            
            statement = select(DashboardVideo).where(
                DashboardVideo.user_id == user_uuid
            ).order_by(DashboardVideo.data_updated_at.desc())
            
            cached_data = db.exec(statement).all()
            
            if cached_data:
                # Check if any video data is recent enough
                latest_update = max(
                    video.data_updated_at for video in cached_data
                )
                
                if YouTubeCacheService.is_cache_valid(
                    type('MockData', (), {'data_updated_at': latest_update})(), 'videos'
                ):
                    logger.info(f"Using cached videos data for user {user_id}")
                    return cached_data
            
            return None
            
        except Exception as e:
            logger.error(f"Error getting videos cache: {e}")
            return None
    
    @staticmethod
    def get_playlist_videos_cache(
        user_id: str, 
        playlist_id: str, 
        db: Session
    ) -> Optional[List[DashboardVideo]]:
        """Get cached playlist videos data"""
        try:
            # Convert string user_id to UUID
            from uuid import UUID
            user_uuid = UUID(user_id)
            
            # Get playlist-video relationships
            statement = select(DashboardPlaylistVideo).where(
                DashboardPlaylistVideo.user_id == user_uuid,
                DashboardPlaylistVideo.playlist_id == playlist_id
            ).order_by(DashboardPlaylistVideo.position)
            
            playlist_videos = db.exec(statement).all()
            
            if not playlist_videos:
                return None
            
            # Get video IDs from relationships
            video_ids = [pv.video_id for pv in playlist_videos]
            
            # Get actual video data
            video_statement = select(DashboardVideo).where(
                DashboardVideo.user_id == user_uuid,
                DashboardVideo.video_id.in_(video_ids)
            ).order_by(DashboardVideo.data_updated_at.desc())
            
            cached_videos = db.exec(video_statement).all()
            
            if cached_videos:
                # Check if any video data is recent enough
                latest_update = max(
                    video.data_updated_at for video in cached_videos
                )
                
                if YouTubeCacheService.is_cache_valid(
                    type('MockData', (), {'data_updated_at': latest_update})(), 'playlist_videos'
                ):
                    logger.info(f"Using cached playlist videos data for user {user_id}, playlist {playlist_id}")
                    return cached_videos
            
            return None
            
        except Exception as e:
            logger.error(f"Error getting playlist videos cache: {e}")
            return None
    
    @staticmethod
    def clear_overview_cache(user_id: str, db: Session) -> bool:
        """Clear overview cache for user"""
        try:
            # Convert string user_id to UUID
            from uuid import UUID
            user_uuid = UUID(user_id)
            
            db.query(DashboardOverview).filter(
                DashboardOverview.user_id == user_uuid
            ).delete()
            db.commit()
            logger.info(f"Cleared overview cache for user {user_id}")
            return True
        except Exception as e:
            logger.error(f"Error clearing overview cache: {e}")
            db.rollback()
            return False
    
    @staticmethod
    def clear_playlists_cache(user_id: str, db: Session) -> bool:
        """Clear playlists cache for user"""
        try:
            # Convert string user_id to UUID
            from uuid import UUID
            user_uuid = UUID(user_id)
            
            db.query(DashboardPlaylist).filter(
                DashboardPlaylist.user_id == user_uuid
            ).delete()
            db.commit()
            logger.info(f"Cleared playlists cache for user {user_id}")
            return True
        except Exception as e:
            logger.error(f"Error clearing playlists cache: {e}")
            db.rollback()
            return False
    
    @staticmethod
    def clear_videos_cache(user_id: str, db: Session) -> bool:
        """Clear videos cache for user"""
        try:
            # Convert string user_id to UUID
            from uuid import UUID
            user_uuid = UUID(user_id)
            
            db.query(DashboardVideo).filter(
                DashboardVideo.user_id == user_uuid
            ).delete()
            db.commit()
            logger.info(f"Cleared videos cache for user {user_id}")
            return True
        except Exception as e:
            logger.error(f"Error clearing videos cache: {e}")
            db.rollback()
            return False
    
    @staticmethod
    def clear_playlist_videos_cache(user_id: str, playlist_id: str, db: Session) -> bool:
        """Clear playlist videos cache for user and playlist"""
        try:
            # Convert string user_id to UUID
            from uuid import UUID
            user_uuid = UUID(user_id)
            
            db.query(DashboardPlaylistVideo).filter(
                DashboardPlaylistVideo.user_id == user_uuid,
                DashboardPlaylistVideo.playlist_id == playlist_id
            ).delete()
            db.commit()
            logger.info(f"Cleared playlist videos cache for user {user_id}, playlist {playlist_id}")
            return True
        except Exception as e:
            logger.error(f"Error clearing playlist videos cache: {e}")
            db.rollback()
            return False
    
    @staticmethod
    def should_use_cache(cache_type: str) -> bool:
        """Determine if cache should be used based on type"""
        # Always use cache for normal operations, force refresh only when explicitly requested
        return True
    
    @staticmethod
    def get_cache_age_minutes(cached_data: Any) -> int:
        """Get cache age in minutes"""
        try:
            if not cached_data:
                return 999999  # Very old
            
            # Check for different possible field names
            updated_at = None
            if hasattr(cached_data, 'data_updated_at'):
                updated_at = cached_data.data_updated_at
            elif hasattr(cached_data, 'updated_at'):
                updated_at = cached_data.updated_at
            else:
                return 999999  # Very old
            
            if isinstance(updated_at, str):
                updated_at = datetime.fromisoformat(updated_at.replace('Z', '+00:00'))
            
            age_seconds = (datetime.now() - updated_at).total_seconds()
            return int(age_seconds / 60)
            
        except Exception as e:
            logger.error(f"Error calculating cache age: {e}")
            return 999999 