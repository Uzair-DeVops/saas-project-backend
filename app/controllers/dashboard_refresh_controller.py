"""
Dashboard Refresh Controller - Handles forced refresh operations with cache clearing
"""
from typing import Dict, Any, List, Optional
from uuid import UUID
from sqlmodel import Session
from fastapi import HTTPException
from datetime import datetime

from ..services.dashboard_data_service import DashboardDataService
from ..services.dashboard_service import get_channel_info, get_all_playlists_comprehensive, get_all_user_videos_dashboard
from ..services.youtube_auth_service import get_youtube_client
from ..services.youtube_cache_service import YouTubeCacheService
from ..utils.my_logger import get_logger

logger = get_logger("DASHBOARD_REFRESH_CONTROLLER")

def force_refresh_overview_data(user_id: UUID, db: Session) -> Dict[str, Any]:
    """Force refresh overview data by clearing cache and fetching fresh data"""
    try:
        logger.info(f"Force refreshing overview data for user_id: {user_id}")
        
        # Clear overview cache
        cache_cleared = YouTubeCacheService.clear_overview_cache(str(user_id), db)
        if not cache_cleared:
            logger.warning(f"Failed to clear overview cache for user {user_id}")
        
        # Get YouTube client
        youtube = get_youtube_client(user_id, db)
        if not youtube:
            raise HTTPException(
                status_code=500,
                detail="Failed to get YouTube client. Please check your YouTube API credentials."
            )
        
        # Import the dashboard overview service
        from ..services.dashboard_overview_service import generate_dashboard_overview_data
        
        # Get fresh overview data
        overview_data = generate_dashboard_overview_data(youtube, user_id, db)
        
        if not overview_data:
            raise HTTPException(
                status_code=500,
                detail="Failed to fetch overview data from YouTube API."
            )
        
        # Store fresh data in database
        success = DashboardDataService.store_overview_data(user_id, overview_data, db)
        
        if not success:
            raise HTTPException(
                status_code=500,
                detail="Failed to store overview data in database."
            )
        
        logger.info(f"Successfully force refreshed overview data for user_id: {user_id}")
        
        return {
            "success": True,
            "message": "Overview data force refreshed successfully",
            "data": overview_data,
            "cache_info": {
                "is_cached": False,
                "age_minutes": 0,
                "last_updated": datetime.now().isoformat()
            }
        }
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error force refreshing overview data for user_id {user_id}: {e}")
        raise HTTPException(
            status_code=500,
            detail="Internal server error while force refreshing overview data"
        )

def force_refresh_playlists_data(user_id: UUID, db: Session) -> Dict[str, Any]:
    """Force refresh playlists data by clearing cache and fetching fresh data"""
    try:
        logger.info(f"Force refreshing playlists data for user_id: {user_id}")
        
        # Clear playlists cache
        cache_cleared = YouTubeCacheService.clear_playlists_cache(str(user_id), db)
        if not cache_cleared:
            logger.warning(f"Failed to clear playlists cache for user {user_id}")
        
        # Get YouTube client
        youtube = get_youtube_client(user_id, db)
        if not youtube:
            raise HTTPException(
                status_code=500,
                detail="Failed to get YouTube client. Please check your YouTube API credentials."
            )
        
        # Get fresh playlists data
        raw_playlists_data = get_all_playlists_comprehensive(youtube)
        
        if not raw_playlists_data:
            raise HTTPException(
                status_code=500,
                detail="Failed to fetch playlists data from YouTube API."
            )
        
        # Transform data to match expected database format
        playlists_data = []
        for playlist in raw_playlists_data:
            playlist_data = {
                'playlist_info': {
                    'playlist_id': playlist.get('playlist_id', ''),
                    'title': playlist.get('title', ''),
                    'description': playlist.get('description', ''),
                    'playlist_url': playlist.get('playlist_url', ''),
                    'embed_html': playlist.get('embed_html', ''),
                    'embed_url': playlist.get('embed_url', ''),
                    'playlist_type': playlist.get('playlist_type', ''),
                    'is_editable': playlist.get('is_editable', True),
                    'is_public': playlist.get('is_public', True),
                    'is_unlisted': playlist.get('is_unlisted', False),
                    'is_private': playlist.get('is_private', False),
                    'published_at': playlist.get('published_at', ''),
                    'channel_title': playlist.get('channel_title', ''),
                    'channel_id': playlist.get('channel_id', ''),
                    'privacy_status': playlist.get('privacy_status', 'private'),
                    'video_count': playlist.get('video_count', 0),
                    'tags': playlist.get('tags', []),
                    'default_language': playlist.get('default_language', ''),
                    'localized': playlist.get('localized', {}),
                    'thumbnails': playlist.get('thumbnails', {})
                },
                'analytics': playlist.get('analytics', {})
            }
            playlists_data.append(playlist_data)
        
        # Store fresh data in database
        success = DashboardDataService.store_playlists_data(user_id, playlists_data, db)
        
        if not success:
            raise HTTPException(
                status_code=500,
                detail="Failed to store playlists data in database."
            )
        
        logger.info(f"Successfully force refreshed {len(playlists_data)} playlists for user_id: {user_id}")
        
        return {
            "success": True,
            "message": f"Playlists data force refreshed successfully ({len(playlists_data)} playlists)",
            "data": playlists_data,
            "count": len(playlists_data),
            "cache_info": {
                "is_cached": False,
                "age_minutes": 0,
                "last_updated": datetime.now().isoformat()
            }
        }
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error force refreshing playlists data for user_id {user_id}: {e}")
        raise HTTPException(
            status_code=500,
            detail="Internal server error while force refreshing playlists data"
        )

def force_refresh_videos_data(user_id: UUID, db: Session) -> Dict[str, Any]:
    """Force refresh videos data by clearing cache and fetching fresh data"""
    try:
        logger.info(f"Force refreshing videos data for user_id: {user_id}")
        
        # Clear videos cache
        cache_cleared = YouTubeCacheService.clear_videos_cache(str(user_id), db)
        if not cache_cleared:
            logger.warning(f"Failed to clear videos cache for user {user_id}")
        
        # Get YouTube client
        youtube = get_youtube_client(user_id, db)
        if not youtube:
            raise HTTPException(
                status_code=500,
                detail="Failed to get YouTube client. Please check your YouTube API credentials."
            )
        
        # Get fresh videos data
        videos_data = get_all_user_videos_dashboard(user_id, db)
        
        if not videos_data:
            raise HTTPException(
                status_code=500,
                detail="Failed to fetch videos data from YouTube API."
            )
        
        # Store fresh data in database
        success = DashboardDataService.store_videos_data(user_id, videos_data, db)
        
        if not success:
            raise HTTPException(
                status_code=500,
                detail="Failed to store videos data in database."
            )
        
        logger.info(f"Successfully force refreshed {len(videos_data)} videos for user_id: {user_id}")
        
        return {
            "success": True,
            "message": f"Videos data force refreshed successfully ({len(videos_data)} videos)",
            "data": videos_data,
            "count": len(videos_data),
            "cache_info": {
                "is_cached": False,
                "age_minutes": 0,
                "last_updated": datetime.now().isoformat()
            }
        }
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error force refreshing videos data for user_id {user_id}: {e}")
        raise HTTPException(
            status_code=500,
            detail="Internal server error while force refreshing videos data"
        )

def force_refresh_single_playlist_data(user_id: UUID, playlist_id: str, db: Session) -> Dict[str, Any]:
    """Force refresh single playlist data by clearing cache and fetching fresh data"""
    try:
        logger.info(f"Force refreshing playlist data for playlist_id: {playlist_id}, user_id: {user_id}")
        
        # Clear playlist videos cache
        cache_cleared = YouTubeCacheService.clear_playlist_videos_cache(str(user_id), playlist_id, db)
        if not cache_cleared:
            logger.warning(f"Failed to clear playlist videos cache for user {user_id}, playlist {playlist_id}")
        
        # Get YouTube client
        youtube = get_youtube_client(user_id, db)
        if not youtube:
            raise HTTPException(
                status_code=500,
                detail="Failed to get YouTube client. Please check your YouTube API credentials."
            )
        
        # Import the existing comprehensive playlist logic
        from ..controllers.dashboard_controller import get_comprehensive_playlist_controller
        
        # Get fresh playlist data
        playlist_data = get_comprehensive_playlist_controller(user_id, playlist_id, db)
        
        if not playlist_data:
            raise HTTPException(
                status_code=404,
                detail="Playlist not found or you don't have permission to access it"
            )
        
        # Store fresh data in database
        playlists_data = [playlist_data]
        success = DashboardDataService.store_playlists_data(user_id, playlists_data, db)
        
        if not success:
            raise HTTPException(
                status_code=500,
                detail="Failed to store playlist data in database."
            )
        
        logger.info(f"Successfully force refreshed playlist data for playlist_id: {playlist_id}")
        
        return {
            "success": True,
            "message": "Playlist data force refreshed successfully",
            "data": playlist_data,
            "cache_info": {
                "is_cached": False,
                "age_minutes": 0,
                "last_updated": datetime.now().isoformat()
            }
        }
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error force refreshing playlist data for playlist_id {playlist_id}, user_id {user_id}: {e}")
        raise HTTPException(
            status_code=500,
            detail="Internal server error while force refreshing playlist data"
        )

def force_refresh_playlist_videos_data(user_id: UUID, playlist_id: str, db: Session) -> Dict[str, Any]:
    """Force refresh playlist videos data by clearing cache and fetching fresh data"""
    try:
        logger.info(f"Force refreshing playlist videos data for playlist_id: {playlist_id}, user_id: {user_id}")
        
        # Clear playlist videos cache
        cache_cleared = YouTubeCacheService.clear_playlist_videos_cache(str(user_id), playlist_id, db)
        if not cache_cleared:
            logger.warning(f"Failed to clear playlist videos cache for user {user_id}, playlist {playlist_id}")
        
        # Get YouTube client
        youtube = get_youtube_client(user_id, db)
        if not youtube:
            raise HTTPException(
                status_code=500,
                detail="Failed to get YouTube client. Please check your YouTube API credentials."
            )
        
        # Import the existing playlist videos logic
        from ..services.playlist_service import get_playlist_videos_by_id
        
        # Get fresh playlist videos data
        videos_data = get_playlist_videos_by_id(youtube, playlist_id)
        
        if not videos_data:
            raise HTTPException(
                status_code=404,
                detail="No videos found in playlist or you don't have permission to access it"
            )
        
        # Store fresh data in database
        success = DashboardDataService.store_playlist_videos_data(user_id, playlist_id, videos_data, db)
        
        if not success:
            raise HTTPException(
                status_code=500,
                detail="Failed to store playlist videos data in database."
            )
        
        logger.info(f"Successfully force refreshed {len(videos_data)} playlist videos for playlist_id: {playlist_id}")
        
        return {
            "success": True,
            "message": f"Playlist videos data force refreshed successfully ({len(videos_data)} videos)",
            "data": videos_data,
            "count": len(videos_data),
            "cache_info": {
                "is_cached": False,
                "age_minutes": 0,
                "last_updated": datetime.now().isoformat()
            }
        }
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error force refreshing playlist videos data for playlist_id {playlist_id}, user_id {user_id}: {e}")
        raise HTTPException(
            status_code=500,
            detail="Internal server error while force refreshing playlist videos data"
        )

def force_refresh_single_playlist_video_data(user_id: UUID, playlist_id: str, video_id: str, db: Session) -> Dict[str, Any]:
    """Force refresh single playlist video data by clearing cache and fetching fresh data"""
    try:
        logger.info(f"Force refreshing playlist video data for playlist_id: {playlist_id}, video_id: {video_id}, user_id: {user_id}")
        
        # Get YouTube client
        youtube = get_youtube_client(user_id, db)
        if not youtube:
            raise HTTPException(
                status_code=500,
                detail="Failed to get YouTube client. Please check your YouTube API credentials."
            )
        
        # Import the existing video details logic
        from ..controllers.dashboard_controller import get_video_details_controller
        
        # Get fresh video data
        video_data = get_video_details_controller(user_id, video_id, db)
        
        if not video_data:
            raise HTTPException(
                status_code=404,
                detail="Video not found or you don't have permission to access it"
            )
        
        # Store fresh data in database (convert to list format for consistency)
        videos_data = [video_data]
        success = DashboardDataService.store_videos_data(user_id, videos_data, db)
        
        if not success:
            raise HTTPException(
                status_code=500,
                detail="Failed to store video data in database."
            )
        
        logger.info(f"Successfully force refreshed playlist video data for playlist_id: {playlist_id}, video_id: {video_id}")
        
        return {
            "success": True,
            "message": "Playlist video data force refreshed successfully",
            "data": video_data,
            "cache_info": {
                "is_cached": False,
                "age_minutes": 0,
                "last_updated": datetime.now().isoformat()
            }
        }
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error force refreshing playlist video data for playlist_id {playlist_id}, video_id {video_id}, user_id {user_id}: {e}")
        raise HTTPException(
            status_code=500,
            detail="Internal server error while force refreshing playlist video data"
        )

def force_refresh_single_video_data(user_id: UUID, video_id: str, db: Session) -> Dict[str, Any]:
    """Force refresh single video data by clearing cache and fetching fresh data"""
    try:
        logger.info(f"Force refreshing video data for video_id: {video_id}, user_id: {user_id}")
        
        # Get YouTube client
        youtube = get_youtube_client(user_id, db)
        if not youtube:
            raise HTTPException(
                status_code=500,
                detail="Failed to get YouTube client. Please check your YouTube API credentials."
            )
        
        # Import the existing video details logic
        from ..controllers.dashboard_controller import get_video_details_controller
        
        # Get fresh video data
        video_data = get_video_details_controller(user_id, video_id, db)
        
        if not video_data:
            raise HTTPException(
                status_code=404,
                detail="Video not found or you don't have permission to access it"
            )
        
        # Store fresh data in database (convert to list format for consistency)
        videos_data = [video_data]
        success = DashboardDataService.store_videos_data(user_id, videos_data, db)
        
        if not success:
            raise HTTPException(
                status_code=500,
                detail="Failed to store video data in database."
            )
        
        logger.info(f"Successfully force refreshed video data for video_id: {video_id}")
        
        return {
            "success": True,
            "message": "Video data force refreshed successfully",
            "data": video_data,
            "cache_info": {
                "is_cached": False,
                "age_minutes": 0,
                "last_updated": datetime.now().isoformat()
            }
        }
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error force refreshing video data for video_id {video_id}, user_id {user_id}: {e}")
        raise HTTPException(
            status_code=500,
            detail="Internal server error while force refreshing video data"
        )
