"""
Dashboard Fetch Controller - Handles fetching data from YouTube and storing in database
"""
from typing import Dict, Any, List, Optional
from uuid import UUID
from sqlmodel import Session
from fastapi import HTTPException

from ..services.dashboard_data_service import DashboardDataService
from ..services.dashboard_service import get_channel_info, get_all_playlists_comprehensive, get_all_user_videos_dashboard
from ..services.youtube_auth_service import get_youtube_client
from ..utils.my_logger import get_logger

logger = get_logger("DASHBOARD_FETCH_CONTROLLER")

def fetch_and_store_overview_data(user_id: UUID, db: Session) -> Dict[str, Any]:
    """Fetch overview data from YouTube and store in database"""
    try:
        logger.info(f"Fetching overview data for user_id: {user_id}")
        
        # Get YouTube client
        youtube = get_youtube_client(user_id, db)
        if not youtube:
            raise HTTPException(
                status_code=500,
                detail="Failed to get YouTube client. Please check your YouTube API credentials."
            )
        
        # Import the dashboard overview service
        from ..services.dashboard_overview_service import generate_dashboard_overview_data
        
        # Get overview data using the service
        overview_data = generate_dashboard_overview_data(youtube, user_id, db)
        
        if not overview_data:
            raise HTTPException(
                status_code=500,
                detail="Failed to fetch overview data from YouTube API."
            )
        
        # Store in database
        success = DashboardDataService.store_overview_data(user_id, overview_data, db)
        
        if not success:
            raise HTTPException(
                status_code=500,
                detail="Failed to store overview data in database."
            )
        
        logger.info(f"Successfully fetched and stored overview data for user_id: {user_id}")
        
        return {
            "success": True,
            "message": "Overview data fetched and stored successfully",
            "data": overview_data
        }
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error fetching overview data for user_id {user_id}: {e}")
        raise HTTPException(
            status_code=500,
            detail="Internal server error while fetching overview data"
        )

def fetch_and_store_playlists_data(user_id: UUID, db: Session) -> Dict[str, Any]:
    """Fetch playlists data from YouTube and store in database"""
    try:
        logger.info(f"Fetching playlists data for user_id: {user_id}")
        
        # Get YouTube client
        youtube = get_youtube_client(user_id, db)
        if not youtube:
            raise HTTPException(
                status_code=500,
                detail="Failed to get YouTube client. Please check your YouTube API credentials."
            )
        
        # Get playlists data using existing service
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
                    'default_thumbnail': playlist.get('default_thumbnail', ''),
                    'high_thumbnail': playlist.get('high_thumbnail', ''),
                    'maxres_thumbnail': playlist.get('maxres_thumbnail', ''),
                    'standard_thumbnail': playlist.get('standard_thumbnail', ''),
                    'item_count': playlist.get('video_count', 0),
                    'video_count': playlist.get('video_count', 0),
                    'published_at': playlist.get('published_at', ''),
                    'channel_id': playlist.get('channel_id', ''),
                    'channel_title': playlist.get('channel_title', '')
                },
                'analytics': playlist.get('analytics', {})
            }
            playlists_data.append(playlist_data)
        
        # Store in database
        success = DashboardDataService.store_playlists_data(user_id, playlists_data, db)
        
        if not success:
            raise HTTPException(
                status_code=500,
                detail="Failed to store playlists data in database."
            )
        
        logger.info(f"Successfully fetched and stored {len(playlists_data)} playlists for user_id: {user_id}")
        
        return {
            "success": True,
            "message": f"Playlists data fetched and stored successfully ({len(playlists_data)} playlists)",
            "data": playlists_data,
            "count": len(playlists_data)
        }
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error fetching playlists data for user_id {user_id}: {e}")
        raise HTTPException(
            status_code=500,
            detail="Internal server error while fetching playlists data"
        )

def fetch_and_store_videos_data(user_id: UUID, db: Session) -> Dict[str, Any]:
    """Fetch videos data from YouTube and store in database"""
    try:
        logger.info(f"Fetching videos data for user_id: {user_id}")
        
        # Get YouTube client
        youtube = get_youtube_client(user_id, db)
        if not youtube:
            raise HTTPException(
                status_code=500,
                detail="Failed to get YouTube client. Please check your YouTube API credentials."
            )
        
        # Get videos data using existing service
        videos_data = get_all_user_videos_dashboard(user_id, db)
        
        if not videos_data:
            raise HTTPException(
                status_code=500,
                detail="Failed to fetch videos data from YouTube API."
            )
        
        # Store in database
        success = DashboardDataService.store_videos_data(user_id, videos_data, db)
        
        if not success:
            raise HTTPException(
                status_code=500,
                detail="Failed to store videos data in database."
            )
        
        logger.info(f"Successfully fetched and stored {len(videos_data)} videos for user_id: {user_id}")
        
        return {
            "success": True,
            "message": f"Videos data fetched and stored successfully ({len(videos_data)} videos)",
            "data": videos_data,
            "count": len(videos_data)
        }
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error fetching videos data for user_id {user_id}: {e}")
        raise HTTPException(
            status_code=500,
            detail="Internal server error while fetching videos data"
        )

def fetch_and_store_single_playlist_data(user_id: UUID, playlist_id: str, db: Session) -> Dict[str, Any]:
    """Fetch single playlist data from YouTube and store in database"""
    try:
        logger.info(f"Fetching playlist data for playlist_id: {playlist_id}, user_id: {user_id}")
        
        # Get YouTube client
        youtube = get_youtube_client(user_id, db)
        if not youtube:
            raise HTTPException(
                status_code=500,
                detail="Failed to get YouTube client. Please check your YouTube API credentials."
            )
        
        # Import the existing comprehensive playlist logic
        from ..controllers.dashboard_controller import get_comprehensive_playlist_controller
        
        # Get playlist data using existing controller
        playlist_data = get_comprehensive_playlist_controller(user_id, playlist_id, db)
        
        if not playlist_data:
            raise HTTPException(
                status_code=404,
                detail="Playlist not found or you don't have permission to access it"
            )
        
        # Store in database (convert to list format for consistency)
        playlists_data = [playlist_data]
        success = DashboardDataService.store_playlists_data(user_id, playlists_data, db)
        
        if not success:
            raise HTTPException(
                status_code=500,
                detail="Failed to store playlist data in database."
            )
        
        logger.info(f"Successfully fetched and stored playlist data for playlist_id: {playlist_id}")
        
        return {
            "success": True,
            "message": f"Playlist data fetched and stored successfully",
            "data": playlist_data
        }
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error fetching playlist data for playlist_id {playlist_id}, user_id {user_id}: {e}")
        raise HTTPException(
            status_code=500,
            detail="Internal server error while fetching playlist data"
        )

def fetch_and_store_single_video_data(user_id: UUID, video_id: str, db: Session) -> Dict[str, Any]:
    """Fetch single video data from YouTube and store in database"""
    try:
        logger.info(f"Fetching video data for video_id: {video_id}, user_id: {user_id}")
        
        # Get YouTube client
        youtube = get_youtube_client(user_id, db)
        if not youtube:
            raise HTTPException(
                status_code=500,
                detail="Failed to get YouTube client. Please check your YouTube API credentials."
            )
        
        # Import the existing video details logic
        from ..controllers.dashboard_controller import get_video_details_controller
        
        # Get video data using existing controller
        video_data = get_video_details_controller(user_id, video_id, db)
        
        if not video_data:
            raise HTTPException(
                status_code=404,
                detail="Video not found or you don't have permission to access it"
            )
        
        # Store in database (convert to list format for consistency)
        videos_data = [video_data]
        success = DashboardDataService.store_videos_data(user_id, videos_data, db)
        
        if not success:
            raise HTTPException(
                status_code=500,
                detail="Failed to store video data in database."
            )
        
        logger.info(f"Successfully fetched and stored video data for video_id: {video_id}")
        
        return {
            "success": True,
            "message": f"Video data fetched and stored successfully",
            "data": video_data
        }
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error fetching video data for video_id {video_id}, user_id {user_id}: {e}")
        raise HTTPException(
            status_code=500,
            detail="Internal server error while fetching video data"
        )


def fetch_and_store_single_playlist_video_data(user_id: UUID, playlist_id: str, video_id: str, db: Session) -> Dict[str, Any]:
    """Fetch single video data within a playlist from YouTube and store in database"""
    try:
        logger.info(f"Fetching playlist video data for playlist_id: {playlist_id}, video_id: {video_id}, user_id: {user_id}")
        
        # Get YouTube client
        youtube = get_youtube_client(user_id, db)
        if not youtube:
            raise HTTPException(
                status_code=500,
                detail="Failed to get YouTube client. Please check your YouTube API credentials."
            )
        
        # Import the existing video details logic
        from ..controllers.dashboard_controller import get_video_details_controller
        
        # Get video data using existing controller
        video_data = get_video_details_controller(user_id, video_id, db)
        
        if not video_data:
            raise HTTPException(
                status_code=404,
                detail="Video not found or you don't have permission to access it"
            )
        
        # Verify the video belongs to the playlist by checking playlist data
        from ..controllers.dashboard_controller import get_comprehensive_playlist_controller
        
        playlist_data = get_comprehensive_playlist_controller(user_id, playlist_id, db)
        
        if not playlist_data:
            raise HTTPException(
                status_code=404,
                detail="Playlist not found or you don't have permission to access it"
            )
        
        # Check if video exists in playlist
        playlist_videos = playlist_data.get('analytics', {}).get('videos', [])
        video_in_playlist = any(v.get('video_id') == video_id for v in playlist_videos)
        
        if not video_in_playlist:
            raise HTTPException(
                status_code=404,
                detail="Video not found in this playlist"
            )
        
        # Store video data in database
        videos_data = [video_data]
        success = DashboardDataService.store_videos_data(user_id, videos_data, db)
        
        if not success:
            raise HTTPException(
                status_code=500,
                detail="Failed to store video data in database."
            )
        
        # Update playlist data to ensure relationship is maintained
        playlists_data = [playlist_data]
        success = DashboardDataService.store_playlists_data(user_id, playlists_data, db)
        
        if not success:
            raise HTTPException(
                status_code=500,
                detail="Failed to store playlist data in database."
            )
        
        logger.info(f"Successfully fetched and stored playlist video data for playlist_id: {playlist_id}, video_id: {video_id}")
        
        return {
            "success": True,
            "message": f"Playlist video data fetched and stored successfully",
            "data": {
                "playlist_id": playlist_id,
                "video_id": video_id,
                "video_data": video_data
            }
        }
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error fetching playlist video data for playlist_id {playlist_id}, video_id {video_id}, user_id {user_id}: {e}")
        raise HTTPException(
            status_code=500,
            detail="Internal server error while fetching playlist video data"
        )


def fetch_and_store_playlist_videos_data(user_id: UUID, playlist_id: str, db: Session) -> Dict[str, Any]:
    """Fetch all videos in a specific playlist from YouTube and store in database"""
    try:
        logger.info(f"Fetching playlist videos data for playlist_id: {playlist_id}, user_id: {user_id}")
        
        # Get YouTube client
        youtube = get_youtube_client(user_id, db)
        if not youtube:
            raise HTTPException(
                status_code=500,
                detail="Failed to get YouTube client. Please check your YouTube API credentials."
            )
        
        # Import the playlist videos service
        from ..services.dashboard_service import get_playlist_videos_by_id
        
        # Get videos directly from playlist
        videos = get_playlist_videos_by_id(youtube, playlist_id)
        
        if not videos:
            raise HTTPException(
                status_code=404,
                detail="No videos found in this playlist"
            )
        
        # Get detailed video information for each video
        detailed_videos = []
        logger.info(f"Processing {len(videos)} videos from playlist {playlist_id}")
        
        for i, video in enumerate(videos):
            video_id = video['video_id']
            logger.info(f"Processing video {i+1}/{len(videos)}: {video_id}")
            
            try:
                # Get detailed video information
                video_request = youtube.videos().list(
                    part='snippet,statistics,contentDetails,status',
                    id=video_id
                )
                video_response = video_request.execute()
                
                if video_response['items']:
                    video_data = video_response['items'][0]
                    snippet = video_data['snippet']
                    statistics = video_data['statistics']
                    content_details = video_data['contentDetails']
                    status = video_data['status']
                    
                    detailed_video = {
                        'video_id': video_id,
                        'title': snippet.get('title', ''),
                        'description': snippet.get('description', ''),
                        'published_at': snippet.get('publishedAt', ''),
                        'thumbnail_url': snippet.get('thumbnails', {}).get('medium', {}).get('url', ''),
                        'channel_title': snippet.get('channelTitle', ''),
                        'channel_id': snippet.get('channelId', ''),
                        'category_id': snippet.get('categoryId', ''),
                        'tags': snippet.get('tags', []),
                        'default_language': snippet.get('defaultLanguage', ''),
                        'default_audio_language': snippet.get('defaultAudioLanguage', ''),
                        'duration': content_details.get('duration', 'PT0S'),
                        'dimension': content_details.get('dimension', {}),
                        'definition': content_details.get('definition', 'sd'),
                        'caption': content_details.get('caption', 'false'),
                        'licensed_content': content_details.get('licensedContent', False),
                        'projection': content_details.get('projection', 'rectangular'),
                        'has_custom_thumbnail': content_details.get('hasCustomThumbnail', False),
                        'view_count': int(statistics.get('viewCount', 0)),
                        'like_count': int(statistics.get('likeCount', 0)),
                        'comment_count': int(statistics.get('commentCount', 0)),
                        'favorite_count': int(statistics.get('favoriteCount', 0)),
                        'privacy_status': status.get('privacyStatus', 'private'),
                        'upload_status': status.get('uploadStatus', 'processed'),
                        'embeddable': status.get('embeddable', True),
                        'license': status.get('license', 'youtube'),
                        'public_stats_viewable': status.get('publicStatsViewable', True),
                        'made_for_kids': status.get('madeForKids', False),
                        'youtube_url': f"https://www.youtube.com/watch?v={video_id}",
                        'embed_html': f"<iframe width='560' height='315' src='https://www.youtube.com/embed/{video_id}' frameborder='0' allowfullscreen></iframe>"
                    }
                    detailed_videos.append(detailed_video)
                    logger.info(f"Successfully processed video {video_id}")
                else:
                    logger.warning(f"No video data returned for video {video_id}, using basic info")
                    # Add basic video info if no detailed data
                    detailed_videos.append({
                        'video_id': video_id,
                        'title': video.get('title', ''),
                        'published_at': video.get('published_at', ''),
                        'thumbnail_url': video.get('thumbnail_url', ''),
                        'youtube_url': f"https://www.youtube.com/watch?v={video_id}"
                    })
                    
            except Exception as e:
                logger.error(f"Error getting detailed info for video {video_id}: {e}")
                # Add basic video info if detailed info fails
                detailed_videos.append({
                    'video_id': video_id,
                    'title': video.get('title', ''),
                    'published_at': video.get('published_at', ''),
                    'thumbnail_url': video.get('thumbnail_url', ''),
                    'youtube_url': f"https://www.youtube.com/watch?v={video_id}"
                })
                logger.info(f"Added basic info for video {video_id} after error")
        
        logger.info(f"Successfully processed {len(detailed_videos)} videos out of {len(videos)} total videos")
        
        # Store videos data in database
        success = DashboardDataService.store_videos_data(user_id, detailed_videos, db)
        
        if not success:
            raise HTTPException(
                status_code=500,
                detail="Failed to store videos data in database."
            )
        
        # Store playlist-video relationships
        for i, video in enumerate(detailed_videos):
            DashboardDataService.store_playlist_video_relationship(user_id, playlist_id, video['video_id'], i + 1, db)
        
        logger.info(f"Successfully fetched and stored {len(detailed_videos)} videos for playlist_id: {playlist_id}")
        
        return {
            "success": True,
            "message": f"Successfully fetched and stored {len(detailed_videos)} videos for playlist",
            "data": {
                "playlist_id": playlist_id,
                "videos_count": len(detailed_videos),
                "videos": detailed_videos
            }
        }
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error fetching playlist videos data for playlist_id {playlist_id}, user_id {user_id}: {e}")
        raise HTTPException(
            status_code=500,
            detail="Internal server error while fetching playlist videos data"
        )
