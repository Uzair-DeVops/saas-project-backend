from typing import List, Dict, Any, Optional
from uuid import UUID
from googleapiclient.errors import HttpError
from sqlmodel import Session, select
from datetime import datetime, timedelta

from ..models.video_model import Video
from ..services.youtube_auth_service import get_youtube_client
from ..services.playlist_service import get_user_playlists, get_playlist_videos_by_id
from ..utils.my_logger import get_logger

logger = get_logger("DASHBOARD_SERVICE")

def get_user_playlists_dashboard(user_id: UUID, db: Session) -> List[Dict[str, Any]]:
    """
    Get all playlists for dashboard with additional metadata.
    
    Args:
        user_id: UUID of the user
        db: Database session
    
    Returns:
        List[Dict[str, Any]]: List of playlists with metadata
    """
    try:
        # Get YouTube client
        youtube = get_youtube_client(user_id, db)
        if not youtube:
            logger.error(f"Failed to get YouTube client for user {user_id}")
            return []
        
        # Get playlists from YouTube
        playlists = get_user_playlists(youtube)
        
        # Enhance with additional data
        enhanced_playlists = []
        for playlist in playlists:
            try:
                # Get playlist statistics
                playlist_stats = get_playlist_statistics(youtube, playlist['id'])
                
                enhanced_playlist = {
                    **playlist,
                    'total_videos': playlist_stats.get('total_videos', 0),
                    'total_views': playlist_stats.get('total_views', 0),
                    'total_likes': playlist_stats.get('total_likes', 0),
                    'total_comments': playlist_stats.get('total_comments', 0),
                    'average_views': playlist_stats.get('average_views', 0),
                    'last_updated': playlist_stats.get('last_updated'),
                    'created_date': playlist.get('published_at', 'Unknown')
                }
                enhanced_playlists.append(enhanced_playlist)
                
            except Exception as e:
                logger.error(f"Error enhancing playlist {playlist['id']}: {e}")
                enhanced_playlists.append(playlist)
        
        logger.info(f"Successfully retrieved {len(enhanced_playlists)} playlists for user {user_id}")
        return enhanced_playlists
        
    except Exception as e:
        logger.error(f"Error getting playlists for dashboard: {e}")
        return []

def get_all_user_videos_dashboard(user_id: UUID, db: Session) -> List[Dict[str, Any]]:
    """
    Get all videos for dashboard with detailed analytics.
    
    Args:
        user_id: UUID of the user
        db: Database session
    
    Returns:
        List[Dict[str, Any]]: List of all videos with detailed information
    """
    try:
        # Get YouTube client
        youtube = get_youtube_client(user_id, db)
        if not youtube:
            logger.error(f"Failed to get YouTube client for user {user_id}")
            return []
        
        # Get all user's videos from YouTube
        videos = get_user_videos(youtube)
        
        # Enhance with additional analytics
        enhanced_videos = []
        for video in videos:
            try:
                # Get detailed video analytics
                video_analytics = get_video_analytics(youtube, video['video_id'])
                
                enhanced_video = {
                    **video,
                    'analytics': video_analytics,
                    'engagement_rate': calculate_engagement_rate(video_analytics),
                    'performance_score': calculate_performance_score(video_analytics),
                    'days_since_published': calculate_days_since_published(video.get('published_at'))
                }
                enhanced_videos.append(enhanced_video)
                
            except Exception as e:
                logger.error(f"Error enhancing video {video.get('video_id')}: {e}")
                enhanced_videos.append(video)
        
        logger.info(f"Successfully retrieved {len(enhanced_videos)} videos for user {user_id}")
        return enhanced_videos
        
    except Exception as e:
        logger.error(f"Error getting user videos for dashboard: {e}")
        return []

def get_video_details_dashboard(user_id: UUID, video_id: str, db: Session) -> Optional[Dict[str, Any]]:
    """
    Get detailed analytics for a specific video.
    
    Args:
        user_id: UUID of the user
        video_id: YouTube video ID
        db: Database session
    
    Returns:
        Dict[str, Any]: Detailed video analytics or None if not found
    """
    try:
        # Get YouTube client
        youtube = get_youtube_client(user_id, db)
        if not youtube:
            logger.error(f"Failed to get YouTube client for user {user_id}")
            return None
        
        # Get detailed video analytics
        video_analytics = get_video_analytics(youtube, video_id)
        
        if not video_analytics:
            logger.warning(f"Video not found or no access: {video_id}")
            return None
        
        # Enhance with calculated metrics
        enhanced_video = {
            'video_id': video_id,
            'analytics': video_analytics,
            'engagement_rate': calculate_engagement_rate(video_analytics),
            'performance_score': calculate_performance_score(video_analytics),
            'days_since_published': calculate_days_since_published(video_analytics.get('published_at')),
            'youtube_url': f"https://www.youtube.com/watch?v={video_id}",
            'thumbnail_url': f"https://img.youtube.com/vi/{video_id}/maxresdefault.jpg"
        }
        
        logger.info(f"Successfully retrieved video details for {video_id}")
        return enhanced_video
        
    except Exception as e:
        logger.error(f"Error getting video details for dashboard: {e}")
        return None

def get_playlist_videos_dashboard(user_id: UUID, playlist_id: str, db: Session) -> List[Dict[str, Any]]:
    """
    Get all videos in a playlist with detailed information.
    
    Args:
        user_id: UUID of the user
        playlist_id: YouTube playlist ID
        db: Database session
    
    Returns:
        List[Dict[str, Any]]: List of videos with detailed information
    """
    try:
        # Get YouTube client
        youtube = get_youtube_client(user_id, db)
        if not youtube:
            logger.error(f"Failed to get YouTube client for user {user_id}")
            return []
        
        # Get videos from playlist
        videos = get_playlist_videos_by_id(youtube, playlist_id)
        
        # Enhance with additional analytics
        enhanced_videos = []
        for video in videos:
            try:
                # Get detailed video analytics
                video_analytics = get_video_analytics(youtube, video['video_id'])
                
                enhanced_video = {
                    **video,
                    'analytics': video_analytics,
                    'engagement_rate': calculate_engagement_rate(video_analytics),
                    'performance_score': calculate_performance_score(video_analytics),
                    'days_since_published': calculate_days_since_published(video.get('published_at'))
                }
                enhanced_videos.append(enhanced_video)
                
            except Exception as e:
                logger.error(f"Error enhancing video {video.get('video_id')}: {e}")
                enhanced_videos.append(video)
        
        logger.info(f"Successfully retrieved {len(enhanced_videos)} videos from playlist {playlist_id}")
        return enhanced_videos
        
    except Exception as e:
        logger.error(f"Error getting playlist videos for dashboard: {e}")
        return []

def get_playlist_analytics_dashboard(user_id: UUID, playlist_id: str, db: Session) -> Dict[str, Any]:
    """
    Get comprehensive analytics for all videos in a playlist.
    
    Args:
        user_id: UUID of the user
        playlist_id: YouTube playlist ID
        db: Database session
    
    Returns:
        Dict[str, Any]: Comprehensive analytics data
    """
    try:
        # Get YouTube client
        youtube = get_youtube_client(user_id, db)
        if not youtube:
            logger.error(f"Failed to get YouTube client for user {user_id}")
            return {}
        
        # Get playlist videos
        videos = get_playlist_videos_by_id(youtube, playlist_id)
        
        if not videos:
            return {
                'playlist_id': playlist_id,
                'total_videos': 0,
                'analytics': {},
                'message': 'No videos found in playlist'
            }
        
        # Calculate comprehensive analytics
        total_views = 0
        total_likes = 0
        total_comments = 0
        total_duration = 0
        video_analytics = []
        
        for video in videos:
            try:
                analytics = get_video_analytics(youtube, video['video_id'])
                
                total_views += analytics.get('view_count', 0)
                total_likes += analytics.get('like_count', 0)
                total_comments += analytics.get('comment_count', 0)
                
                video_analytics.append({
                    'video_id': video['video_id'],
                    'title': video['title'],
                    'analytics': analytics,
                    'engagement_rate': calculate_engagement_rate(analytics),
                    'performance_score': calculate_performance_score(analytics)
                })
                
            except Exception as e:
                logger.error(f"Error getting analytics for video {video.get('video_id')}: {e}")
        
        # Calculate playlist-level metrics
        average_views = total_views / len(videos) if videos else 0
        average_likes = total_likes / len(videos) if videos else 0
        average_comments = total_comments / len(videos) if videos else 0
        average_engagement_rate = sum(v.get('engagement_rate', 0) for v in video_analytics) / len(video_analytics) if video_analytics else 0
        
        # Sort videos by performance
        video_analytics.sort(key=lambda x: x.get('performance_score', 0), reverse=True)
        
        analytics_data = {
            'playlist_id': playlist_id,
            'total_videos': len(videos),
            'total_views': total_views,
            'total_likes': total_likes,
            'total_comments': total_comments,
            'average_views': average_views,
            'average_likes': average_likes,
            'average_comments': average_comments,
            'average_engagement_rate': average_engagement_rate,
            'top_performing_videos': video_analytics[:5],  # Top 5 videos
            'video_analytics': video_analytics,
            'performance_summary': {
                'best_performing_video': video_analytics[0] if video_analytics else None,
                'worst_performing_video': video_analytics[-1] if video_analytics else None,
                'most_engaged_video': max(video_analytics, key=lambda x: x.get('engagement_rate', 0)) if video_analytics else None
            }
        }
        
        logger.info(f"Successfully generated analytics for playlist {playlist_id}")
        return analytics_data
        
    except Exception as e:
        logger.error(f"Error getting playlist analytics: {e}")
        return {}

def get_user_videos(youtube) -> List[Dict[str, Any]]:
    """Get all videos uploaded by the user"""
    try:
        # Get user's uploaded videos
        request = youtube.search().list(
            part='snippet',
            forMine=True,
            type='video',
            maxResults=50,
            order='date'
        )
        response = request.execute()
        
        videos = []
        for item in response.get('items', []):
            video = {
                'video_id': item['id']['videoId'],
                'title': item['snippet']['title'],
                'description': item['snippet']['description'],
                'published_at': item['snippet']['publishedAt'],
                'thumbnail_url': item['snippet']['thumbnails'].get('medium', {}).get('url', ''),
                'channel_title': item['snippet']['channelTitle']
            }
            videos.append(video)
        
        return videos
        
    except Exception as e:
        logger.error(f"Error getting user videos: {e}")
        return []

def get_playlist_statistics(youtube, playlist_id: str) -> Dict[str, Any]:
    """Get basic statistics for a playlist"""
    try:
        videos = get_playlist_videos_by_id(youtube, playlist_id)
        
        total_views = 0
        total_likes = 0
        total_comments = 0
        last_updated = None
        
        for video in videos:
            analytics = get_video_analytics(youtube, video['video_id'])
            total_views += analytics.get('view_count', 0)
            total_likes += analytics.get('like_count', 0)
            total_comments += analytics.get('comment_count', 0)
            
            # Track last updated
            published_date = video.get('published_at')
            if published_date:
                try:
                    date_obj = datetime.fromisoformat(published_date.replace('Z', '+00:00'))
                    if not last_updated or date_obj > last_updated:
                        last_updated = date_obj
                except:
                    pass
        
        return {
            'total_videos': len(videos),
            'total_views': total_views,
            'total_likes': total_likes,
            'total_comments': total_comments,
            'average_views': total_views / len(videos) if videos else 0,
            'last_updated': last_updated.isoformat() if last_updated else None
        }
        
    except Exception as e:
        logger.error(f"Error getting playlist statistics: {e}")
        return {}

def get_video_analytics(youtube, video_id: str) -> Dict[str, Any]:
    """Get detailed analytics for a single video"""
    try:
        # Get video statistics
        request = youtube.videos().list(
            part='statistics,contentDetails,snippet,status',
            id=video_id
        )
        response = request.execute()
        
        if not response['items']:
            return {}
        
        video = response['items'][0]
        statistics = video['statistics']
        content_details = video['contentDetails']
        snippet = video['snippet']
        
        # Convert string numbers to integers
        view_count = int(statistics.get('viewCount', 0))
        like_count = int(statistics.get('likeCount', 0))
        comment_count = int(statistics.get('commentCount', 0))
        
        return {
            'view_count': view_count,
            'like_count': like_count,
            'comment_count': comment_count,
            'duration': content_details.get('duration', 'PT0S'),
            'privacy_status': video['status'].get('privacyStatus', 'private'),
            'published_at': snippet.get('publishedAt'),
            'title': snippet.get('title'),
            'description': snippet.get('description'),
            'tags': snippet.get('tags', []),
            'category_id': snippet.get('categoryId'),
            'default_language': snippet.get('defaultLanguage'),
            'default_audio_language': snippet.get('defaultAudioLanguage')
        }
        
    except Exception as e:
        logger.error(f"Error getting video analytics for {video_id}: {e}")
        return {}

def calculate_engagement_rate(analytics: Dict[str, Any]) -> float:
    """Calculate engagement rate (likes + comments) / views"""
    try:
        views = analytics.get('view_count', 0)
        likes = analytics.get('like_count', 0)
        comments = analytics.get('comment_count', 0)
        
        if views == 0:
            return 0.0
        
        engagement_rate = ((likes + comments) / views) * 100
        return round(engagement_rate, 2)
        
    except Exception as e:
        logger.error(f"Error calculating engagement rate: {e}")
        return 0.0

def calculate_performance_score(analytics: Dict[str, Any]) -> float:
    """Calculate performance score based on views, likes, and comments"""
    try:
        views = analytics.get('view_count', 0)
        likes = analytics.get('like_count', 0)
        comments = analytics.get('comment_count', 0)
        
        # Simple scoring algorithm
        score = (views * 0.5) + (likes * 10) + (comments * 20)
        return round(score, 2)
        
    except Exception as e:
        logger.error(f"Error calculating performance score: {e}")
        return 0.0

def calculate_days_since_published(published_at: str) -> int:
    """Calculate days since video was published"""
    try:
        if not published_at:
            return 0
        
        published_date = datetime.fromisoformat(published_at.replace('Z', '+00:00'))
        current_date = datetime.now(published_date.tzinfo)
        days_diff = (current_date - published_date).days
        return max(0, days_diff)
        
    except Exception as e:
        logger.error(f"Error calculating days since published: {e}")
        return 0 