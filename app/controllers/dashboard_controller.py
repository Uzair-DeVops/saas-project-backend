from typing import List, Dict, Any
from uuid import UUID
from fastapi import HTTPException
from sqlmodel import Session

from ..services.dashboard_service import (
    get_user_playlists_dashboard,
    get_playlist_videos_dashboard,
    get_all_user_videos_dashboard,
    get_video_details_dashboard
)
from ..utils.my_logger import get_logger

logger = get_logger("DASHBOARD_CONTROLLER")

def get_all_playlists_comprehensive_controller(user_id: UUID, db: Session) -> List[Dict[str, Any]]:
    """
    Get all playlists with comprehensive analytics for dashboard.
    
    Args:
        user_id: UUID of the user
        db: Database session
    
    Returns:
        List[Dict[str, Any]]: List of playlists with comprehensive analytics
    """
    try:
        from ..services.youtube_auth_service import get_youtube_client
        from ..services.dashboard_service import get_all_playlists_comprehensive
        
        youtube = get_youtube_client(user_id, db)
        if not youtube:
            logger.error(f"Failed to get YouTube client for user {user_id}")
            return []
        
        playlists = get_all_playlists_comprehensive(youtube)
        logger.info(f"Successfully retrieved {len(playlists)} playlists for user {user_id}")
        return playlists
        
    except Exception as e:
        logger.error(f"Error in get_all_playlists_comprehensive_controller: {e}")
        return []

def get_comprehensive_playlist_controller(user_id: UUID, playlist_id: str, db: Session) -> Dict[str, Any]:
    """
    Get comprehensive analytics for a specific playlist.
    
    Args:
        user_id: UUID of the user
        playlist_id: YouTube playlist ID
        db: Database session
    
    Returns:
        Dict[str, Any]: Comprehensive playlist analytics with full playlist metadata
    """
    try:
        from ..services.youtube_auth_service import get_youtube_client
        from ..services.dashboard_service import get_comprehensive_playlist_analytics
        
        youtube = get_youtube_client(user_id, db)
        if not youtube:
            logger.error(f"Failed to get YouTube client for user {user_id}")
            return {}
        
        # Get playlist metadata first
        playlist_request = youtube.playlists().list(
            part='snippet,contentDetails,status',
            id=playlist_id
        )
        playlist_response = playlist_request.execute()
        
        if not playlist_response['items']:
            logger.error(f"Playlist not found: {playlist_id}")
            return {}
        
        playlist_info = playlist_response['items'][0]
        snippet = playlist_info['snippet']
        content_details = playlist_info['contentDetails']
        status = playlist_info['status']
        
        # Get comprehensive analytics
        analytics_data = get_comprehensive_playlist_analytics(youtube, playlist_id)
        
        # Combine playlist metadata with analytics to match the structure of get_all_playlists_comprehensive
        comprehensive_playlist_data = {
            'playlist_info': {
                'playlist_id': playlist_id,
                'title': snippet.get('title', ''),
                'description': snippet.get('description', ''),
                'published_at': snippet.get('publishedAt', ''),
                'thumbnail_url': snippet.get('thumbnails', {}).get('medium', {}).get('url', ''),
                'channel_title': snippet.get('channelTitle', ''),
                'channel_id': snippet.get('channelId', ''),
                'privacy_status': status.get('privacyStatus', 'private'),
                'video_count': content_details.get('itemCount', 0),
                'tags': snippet.get('tags', []),
                'default_language': snippet.get('defaultLanguage', ''),
                'localized': snippet.get('localized', {})
            },
            'analytics': analytics_data
        }
        
        logger.info(f"Successfully retrieved comprehensive data for playlist {playlist_id}")
        return comprehensive_playlist_data
        
    except Exception as e:
        logger.error(f"Error in get_comprehensive_playlist_controller: {e}")
        return {}

def get_playlists_controller(user_id: UUID, db: Session) -> List[Dict[str, Any]]:
    """
    Controller function to get all playlists for dashboard.
    
    Args:
        user_id: UUID of the user
        db: Database session
    
    Returns:
        List[Dict[str, Any]]: List of playlists with metadata
    
    Raises:
        HTTPException: If error occurs
    """
    try:
        logger.info(f"Getting playlists for dashboard, user_id: {user_id}")
        
        playlists = get_user_playlists_dashboard(user_id, db)
        
        if playlists is None:
            logger.error(f"Failed to get playlists for user_id: {user_id}")
            raise HTTPException(
                status_code=500,
                detail="Failed to retrieve playlists. Please check your YouTube API credentials."
            )
        
        logger.info(f"Successfully retrieved {len(playlists)} playlists for user_id: {user_id}")
        return playlists
        
    except HTTPException:
        # Re-raise HTTP exceptions as they are already properly formatted
        raise
    except Exception as e:
        logger.error(f"Error in get_playlists_controller for user_id {user_id}: {e}")
        raise HTTPException(
            status_code=500,
            detail=f"Failed to get playlists: {str(e)}"
        )

def get_all_user_videos_controller(user_id: UUID, db: Session) -> List[Dict[str, Any]]:
    """
    Controller function to get all user videos for dashboard.
    
    Args:
        user_id: UUID of the user
        db: Database session
    
    Returns:
        List[Dict[str, Any]]: List of all videos with detailed information
    
    Raises:
        HTTPException: If error occurs
    """
    try:
        logger.info(f"Getting all user videos for dashboard, user_id: {user_id}")
        
        videos = get_all_user_videos_dashboard(user_id, db)
        
        if videos is None:
            logger.error(f"Failed to get user videos for user_id: {user_id}")
            raise HTTPException(
                status_code=500,
                detail="Failed to retrieve user videos. Please check your YouTube API credentials."
            )
        
        logger.info(f"Successfully retrieved {len(videos)} videos for user_id: {user_id}")
        return videos
        
    except HTTPException:
        # Re-raise HTTP exceptions as they are already properly formatted
        raise
    except Exception as e:
        logger.error(f"Error in get_all_user_videos_controller for user_id {user_id}: {e}")
        raise HTTPException(
            status_code=500,
            detail=f"Failed to get user videos: {str(e)}"
        )

def get_video_details_controller(user_id: UUID, video_id: str, db: Session) -> Dict[str, Any]:
    """
    Controller function to get detailed analytics for a specific video.
    
    Args:
        user_id: UUID of the user
        video_id: YouTube video ID
        db: Database session
    
    Returns:
        Dict[str, Any]: Detailed video analytics
    
    Raises:
        HTTPException: If error occurs
    """
    try:
        logger.info(f"Getting video details for dashboard, user_id: {user_id}, video_id: {video_id}")
        
        video_details = get_video_details_dashboard(user_id, video_id, db)
        
        if video_details is None:
            logger.error(f"Failed to get video details for user_id: {user_id}, video_id: {video_id}")
            raise HTTPException(
                status_code=500,
                detail="Failed to retrieve video details. Please check your YouTube API credentials."
            )
        
        if not video_details:
            logger.warning(f"Video not found or no access: user_id: {user_id}, video_id: {video_id}")
            return None
        
        logger.info(f"Successfully retrieved video details for video_id: {video_id}")
        return video_details
        
    except HTTPException:
        # Re-raise HTTP exceptions as they are already properly formatted
        raise
    except Exception as e:
        logger.error(f"Error in get_video_details_controller for user_id {user_id}, video_id {video_id}: {e}")
        raise HTTPException(
            status_code=500,
            detail=f"Failed to get video details: {str(e)}"
        )

def get_playlist_videos_controller(user_id: UUID, playlist_id: str, db: Session) -> List[Dict[str, Any]]:
    """
    Controller function to get all videos in a playlist for dashboard.
    
    Args:
        user_id: UUID of the user
        playlist_id: YouTube playlist ID
        db: Database session
    
    Returns:
        List[Dict[str, Any]]: List of videos with detailed information
    
    Raises:
        HTTPException: If error occurs
    """
    try:
        logger.info(f"Getting playlist videos for dashboard, user_id: {user_id}, playlist_id: {playlist_id}")
        
        videos = get_playlist_videos_dashboard(user_id, playlist_id, db)
        
        if videos is None:
            logger.error(f"Failed to get playlist videos for user_id: {user_id}, playlist_id: {playlist_id}")
            raise HTTPException(
                status_code=500,
                detail="Failed to retrieve playlist videos. Please check your YouTube API credentials."
            )
        
        logger.info(f"Successfully retrieved {len(videos)} videos from playlist {playlist_id}")
        return videos
        
    except HTTPException:
        # Re-raise HTTP exceptions as they are already properly formatted
        raise
    except Exception as e:
        logger.error(f"Error in get_playlist_videos_controller for user_id {user_id}, playlist_id {playlist_id}: {e}")
        raise HTTPException(
            status_code=500,
            detail=f"Failed to get playlist videos: {str(e)}"
        )

 

 