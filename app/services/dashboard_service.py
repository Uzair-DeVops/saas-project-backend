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
    Get comprehensive detailed analytics for a specific video.
    
    Args:
        user_id: UUID of the user
        video_id: YouTube video ID
        db: Database session
    
    Returns:
        Dict[str, Any]: Comprehensive video analytics or None if not found
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
        
        # Calculate additional metrics
        engagement_rate = calculate_engagement_rate(video_analytics)
        performance_score = calculate_performance_score(video_analytics)
        days_since_published = calculate_days_since_published(video_analytics.get('published_at'))
        
        # Calculate advanced metrics
        views = video_analytics.get('view_count', 0)
        likes = video_analytics.get('like_count', 0)
        comments = video_analytics.get('comment_count', 0)
        duration_seconds = video_analytics.get('duration_seconds', 0)
        
        # Calculate additional performance metrics
        likes_per_view = (likes / views * 100) if views > 0 else 0
        comments_per_view = (comments / views * 100) if views > 0 else 0
        views_per_day = (views / days_since_published) if days_since_published > 0 else views
        watch_time_hours = (views * duration_seconds) / 3600 if duration_seconds > 0 else 0
        
        # Performance analysis
        performance_level = "Excellent" if performance_score > 1000 else "Good" if performance_score > 500 else "Average" if performance_score > 100 else "Poor"
        engagement_level = "High" if engagement_rate > 5 else "Medium" if engagement_rate > 2 else "Low"
        
        # Content analysis
        content_type = "Short" if duration_seconds < 60 else "Medium" if duration_seconds < 600 else "Long"
        content_category = get_content_category(video_analytics.get('category_id', ''))
        
        # Growth metrics
        growth_potential = calculate_growth_potential(views, likes, comments, days_since_published)
        
        # Enhanced video details
        enhanced_video = {
            # Basic video information
            'video_id': video_id,
            'title': video_analytics.get('title', ''),
            'description': video_analytics.get('description', ''),
            'published_at': video_analytics.get('published_at', ''),
            'youtube_url': f"https://www.youtube.com/watch?v={video_id}",
            'thumbnail_url': f"https://img.youtube.com/vi/{video_id}/maxresdefault.jpg",
            'privacy_status': video_analytics.get('privacy_status', 'private'),
            
            # Core metrics
            'view_count': views,
            'like_count': likes,
            'comment_count': comments,
            'duration': video_analytics.get('duration', 'PT0S'),
            'duration_seconds': duration_seconds,
            'duration_minutes': round(duration_seconds / 60, 2),
            
            # Calculated metrics
            'engagement_rate': engagement_rate,
            'performance_score': performance_score,
            'days_since_published': days_since_published,
            
            # Advanced metrics
            'likes_per_view_percentage': round(likes_per_view, 2),
            'comments_per_view_percentage': round(comments_per_view, 2),
            'views_per_day': round(views_per_day, 2),
            'watch_time_hours': round(watch_time_hours, 2),
            
            # Performance analysis
            'performance_level': performance_level,
            'engagement_level': engagement_level,
            'content_type': content_type,
            'content_category': content_category,
            'growth_potential': growth_potential,
            
            # Content details
            'tags': video_analytics.get('tags', []),
            'category_id': video_analytics.get('category_id', ''),
            'default_language': video_analytics.get('default_language', ''),
            'default_audio_language': video_analytics.get('default_audio_language', ''),
            
            # Analytics summary
            'analytics_summary': {
                'total_engagement': likes + comments,
                'engagement_breakdown': {
                    'likes_percentage': round((likes / (likes + comments) * 100), 2) if (likes + comments) > 0 else 0,
                    'comments_percentage': round((comments / (likes + comments) * 100), 2) if (likes + comments) > 0 else 0
                },
                'performance_indicators': {
                    'is_high_performing': performance_score > 500,
                    'is_viral_potential': views_per_day > 100,
                    'is_high_engagement': engagement_rate > 5
                }
            },
            
            # Recommendations
            'recommendations': generate_video_recommendations(views, likes, comments, engagement_rate, performance_score, days_since_published)
        }
        
        logger.info(f"Successfully retrieved comprehensive video details for {video_id}")
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
        
        # Clean up video data and add essential metrics
        enhanced_videos = []
        for video in videos:
            try:
                # Get basic video analytics for essential metrics only
                video_analytics = get_video_analytics(youtube, video['video_id'])
                
                enhanced_video = {
                    'title': video['title'],
                    'url': video['url'],
                    'video_id': video['video_id'],
                    'published_at': video['published_at'],
                    'description': video['description'],
                    'thumbnail_url': video.get('thumbnail_url', ''),
                    'position': video['position'],
                    'view_count': video_analytics.get('view_count', 0),
                    'like_count': video_analytics.get('like_count', 0),
                    'comment_count': video_analytics.get('comment_count', 0),
                    'duration': video_analytics.get('duration', 'PT0S'),
                    'privacy_status': video_analytics.get('privacy_status', 'public'),
                    'engagement_rate': calculate_engagement_rate(video_analytics),
                    'performance_score': calculate_performance_score(video_analytics),
                    'days_since_published': calculate_days_since_published(video.get('published_at'))
                }
                enhanced_videos.append(enhanced_video)
                
            except Exception as e:
                logger.error(f"Error enhancing video {video.get('video_id')}: {e}")
                # Add basic video data without analytics
                enhanced_videos.append({
                    'title': video['title'],
                    'url': video['url'],
                    'video_id': video['video_id'],
                    'published_at': video['published_at'],
                    'description': video['description'],
                    'thumbnail_url': video.get('thumbnail_url', ''),
                    'position': video['position'],
                    'view_count': 0,
                    'like_count': 0,
                    'comment_count': 0,
                    'duration': 'PT0S',
                    'privacy_status': 'public',
                    'engagement_rate': 0,
                    'performance_score': 0,
                    'days_since_published': calculate_days_since_published(video.get('published_at'))
                })
        
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
    """Get all videos uploaded by the user with complete analytics"""
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
            video_id = item['id']['videoId']
            
            # Get detailed video analytics
            video_analytics = get_video_analytics(youtube, video_id)
            
            video = {
                'video_id': video_id,
                'title': item['snippet']['title'],
                'description': item['snippet']['description'],
                'published_at': item['snippet']['publishedAt'],
                'thumbnail_url': item['snippet']['thumbnails'].get('medium', {}).get('url', ''),
                'channel_title': item['snippet']['channelTitle'],
                'tags': item['snippet'].get('tags', []),
                # Add analytics data
                'view_count': video_analytics.get('view_count', 0),
                'like_count': video_analytics.get('like_count', 0),
                'comment_count': video_analytics.get('comment_count', 0),
                'duration': video_analytics.get('duration', 'PT0S'),
                'duration_seconds': video_analytics.get('duration_seconds', 0),
                'privacy_status': video_analytics.get('privacy_status', 'private')
            }
            videos.append(video)
        
        logger.info(f"Successfully retrieved {len(videos)} videos with analytics")
        return videos
        
    except Exception as e:
        logger.error(f"Error getting user videos: {e}")
        return []

def get_all_playlists_comprehensive(youtube) -> List[Dict[str, Any]]:
    """Get all playlists with comprehensive analytics"""
    try:
        # Get all playlists
        request = youtube.playlists().list(
            part='snippet,contentDetails,status',
            mine=True,
            maxResults=50
        )
        response = request.execute()
        
        playlists = []
        for item in response.get('items', []):
            playlist_id = item['id']
            snippet = item['snippet']
            content_details = item['contentDetails']
            status = item['status']
            
            # Get detailed playlist analytics
            playlist_analytics = get_comprehensive_playlist_analytics(youtube, playlist_id)
            
            playlist = {
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
                'localized': snippet.get('localized', {}),
                # Comprehensive analytics (all data in one place)
                'analytics': playlist_analytics
            }
            playlists.append(playlist)
        
        logger.info(f"Successfully retrieved {len(playlists)} playlists with comprehensive analytics")
        return playlists
        
    except Exception as e:
        logger.error(f"Error getting all playlists comprehensive: {e}")
        return []

def get_comprehensive_playlist_analytics(youtube, playlist_id: str) -> Dict[str, Any]:
    """Get comprehensive analytics for a specific playlist"""
    try:
        # Get playlist details
        playlist_request = youtube.playlists().list(
            part='snippet,contentDetails,status',
            id=playlist_id
        )
        playlist_response = playlist_request.execute()
        
        if not playlist_response['items']:
            return {}
        
        playlist_info = playlist_response['items'][0]
        snippet = playlist_info['snippet']
        content_details = playlist_info['contentDetails']
        
        # Get all videos in playlist
        videos = get_playlist_videos_by_id(youtube, playlist_id)
        
        if not videos:
            return {
                'playlist_id': playlist_id,
                'total_videos': 0,
                'message': 'No videos found in playlist'
            }
        
        # Calculate comprehensive metrics
        total_views = 0
        total_likes = 0
        total_comments = 0
        total_duration = 0
        video_analytics = []
        
        for video in videos:
            try:
                analytics = get_video_analytics(youtube, video['video_id'])
                
                views = analytics.get('view_count', 0)
                likes = analytics.get('like_count', 0)
                comments = analytics.get('comment_count', 0)
                duration_seconds = analytics.get('duration_seconds', 0)
                
                total_views += views
                total_likes += likes
                total_comments += comments
                total_duration += duration_seconds
                
                engagement_rate = calculate_engagement_rate(analytics)
                performance_score = calculate_performance_score(analytics)
                days_since_published = calculate_days_since_published(video.get('published_at'))
                
                video_analytics.append({
                    'video_id': video['video_id'],
                    'title': video['title'],
                    'published_at': video.get('published_at', ''),
                    'thumbnail_url': video.get('thumbnail_url', ''),
                    'duration': analytics.get('duration', 'PT0S'),
                    'duration_seconds': duration_seconds,
                    'duration_minutes': round(duration_seconds / 60, 2),
                    'views': views,
                    'likes': likes,
                    'comments': comments,
                    'engagement_rate': engagement_rate,
                    'performance_score': performance_score,
                    'days_since_published': days_since_published,
                    'privacy_status': analytics.get('privacy_status', 'private'),
                    'tags': analytics.get('tags', []),
                    'category_id': analytics.get('category_id', ''),
                    'youtube_url': f"https://www.youtube.com/watch?v={video['video_id']}"
                })
                
            except Exception as e:
                logger.error(f"Error getting analytics for video {video.get('video_id')}: {e}")
        
        # Calculate averages
        avg_views_per_video = total_views / len(videos) if videos else 0
        avg_likes_per_video = total_likes / len(videos) if videos else 0
        avg_comments_per_video = total_comments / len(videos) if videos else 0
        avg_duration_per_video = total_duration / len(videos) if videos else 0
        overall_engagement_rate = ((total_likes + total_comments) / total_views * 100) if total_views > 0 else 0
        
        # Calculate performance score for playlist
        playlist_performance_score = sum(v.get('performance_score', 0) for v in video_analytics)
        
        # Sort videos by different metrics - get only the top performer in each category
        top_video_by_views = sorted(video_analytics, key=lambda x: x['views'], reverse=True)[0] if video_analytics else None
        top_video_by_engagement = sorted(video_analytics, key=lambda x: x['engagement_rate'], reverse=True)[0] if video_analytics else None
        top_video_by_performance = sorted(video_analytics, key=lambda x: x['performance_score'], reverse=True)[0] if video_analytics else None
        
        # Growth metrics
        growth_metrics = calculate_playlist_growth_metrics(video_analytics)
        
        # Playlist health
        playlist_health = calculate_playlist_health(video_analytics, overall_engagement_rate, avg_views_per_video)
        

        
        analytics_data = {
            'playlist_id': playlist_id,
            'total_videos': len(videos),
            'total_views': total_views,
            'total_likes': total_likes,
            'total_comments': total_comments,
            'total_duration': total_duration,
            'total_watch_time_hours': round(total_duration / 3600, 2),
            'avg_views_per_video': round(avg_views_per_video, 2),
            'avg_likes_per_video': round(avg_likes_per_video, 2),
            'avg_comments_per_video': round(avg_comments_per_video, 2),
            'avg_duration_per_video': round(avg_duration_per_video, 2),
            'avg_duration_minutes': round(avg_duration_per_video / 60, 2),
            'overall_engagement_rate': round(overall_engagement_rate, 2),
            'performance_score': round(playlist_performance_score, 2),
            'top_performing_videos': {
                'top_by_views': top_video_by_views,
                'top_by_engagement': top_video_by_engagement,
                'top_by_performance_score': top_video_by_performance
            },
            'growth_metrics': growth_metrics,
            'playlist_health': playlist_health,

        }
        
        logger.info(f"Successfully generated comprehensive analytics for playlist {playlist_id}")
        return analytics_data
        
    except Exception as e:
        logger.error(f"Error getting comprehensive playlist analytics: {e}")
        return {}

def analyze_playlist_content(video_analytics: List[Dict[str, Any]]) -> Dict[str, Any]:
    """Analyze content patterns in playlist"""
    try:
        # Content type analysis
        content_types = {
            'shorts': 0,
            'tutorials': 0,
            'lectures': 0,
            'other': 0
        }
        
        # Tag analysis
        all_tags = []
        for video in video_analytics:
            title = video.get('title', '').lower()
            duration_seconds = video.get('duration_seconds', 0)
            tags = video.get('tags', [])
            all_tags.extend(tags)
            
            if 'shorts' in title or duration_seconds <= 60:
                content_types['shorts'] += 1
            elif 'lecture' in title or 'tutorial' in title:
                if duration_seconds > 600:  # 10+ minutes
                    content_types['lectures'] += 1
                else:
                    content_types['tutorials'] += 1
            else:
                content_types['other'] += 1
        
        # Most common tags
        tag_counts = {}
        for tag in all_tags:
            tag_counts[tag] = tag_counts.get(tag, 0) + 1
        
        top_tags = sorted(tag_counts.items(), key=lambda x: x[1], reverse=True)[:10]
        
        return {
            'content_types': content_types,
            'most_common_tags': [{'tag': tag, 'count': count} for tag, count in top_tags],
            'total_unique_tags': len(tag_counts),
            'most_effective_content_type': max(content_types.items(), key=lambda x: x[1])[0] if content_types else 'none'
        }
        
    except Exception as e:
        logger.error(f"Error analyzing playlist content: {e}")
        return {}

def calculate_playlist_growth_metrics(video_analytics: List[Dict[str, Any]]) -> Dict[str, Any]:
    """Calculate growth metrics for playlist"""
    try:
        if len(video_analytics) < 2:
            return {
                'growth_trend': 'new_playlist',
                'avg_views_growth': 0,
                'avg_engagement_growth': 0,
                'consistency_score': 0
            }
        
        # Sort by publish date
        sorted_videos = sorted(video_analytics, key=lambda x: x.get('published_at', ''))
        
        # Calculate growth trends
        recent_videos = sorted_videos[-5:] if len(sorted_videos) >= 5 else sorted_videos
        older_videos = sorted_videos[:5] if len(sorted_videos) >= 5 else sorted_videos
        
        recent_avg_views = sum(v['views'] for v in recent_videos) / len(recent_videos)
        older_avg_views = sum(v['views'] for v in older_videos) / len(older_videos)
        
        recent_avg_engagement = sum(v['engagement_rate'] for v in recent_videos) / len(recent_videos)
        older_avg_engagement = sum(v['engagement_rate'] for v in older_videos) / len(older_videos)
        
        views_growth = ((recent_avg_views - older_avg_views) / older_avg_views * 100) if older_avg_views > 0 else 0
        engagement_growth = ((recent_avg_engagement - older_avg_engagement) / older_avg_engagement * 100) if older_avg_engagement > 0 else 0
        
        # Consistency score (based on view variance)
        view_values = [v['views'] for v in video_analytics]
        view_variance = sum((v - sum(view_values) / len(view_values)) ** 2 for v in view_values) / len(view_values)
        consistency_score = max(0, 100 - (view_variance / 1000))  # Normalize to 0-100
        
        return {
            'growth_trend': 'increasing' if views_growth > 10 else 'decreasing' if views_growth < -10 else 'stable',
            'avg_views_growth': round(views_growth, 2),
            'avg_engagement_growth': round(engagement_growth, 2),
            'consistency_score': round(consistency_score, 2)
        }
        
    except Exception as e:
        logger.error(f"Error calculating playlist growth metrics: {e}")
        return {}

def analyze_recent_playlist_activity(video_analytics: List[Dict[str, Any]]) -> Dict[str, Any]:
    """Analyze recent activity in playlist"""
    try:
        from datetime import datetime, timedelta
        
        # Get a timezone-aware current date
        current_date = datetime.now()
        # Make it timezone-aware by using UTC
        current_date = current_date.replace(tzinfo=None)
        
        thirty_days_ago = current_date - timedelta(days=30)
        seven_days_ago = current_date - timedelta(days=7)
        
        recent_videos = []
        very_recent_videos = []
        
        for v in video_analytics:
            if v.get('published_at'):
                try:
                    # Parse the published date and make it timezone-aware
                    published_date = datetime.fromisoformat(v['published_at'].replace('Z', '+00:00'))
                    # Convert to naive datetime for comparison
                    published_date = published_date.replace(tzinfo=None)
                    
                    if published_date > thirty_days_ago:
                        recent_videos.append(v)
                    if published_date > seven_days_ago:
                        very_recent_videos.append(v)
                except Exception as e:
                    logger.error(f"Error parsing date {v.get('published_at')}: {e}")
                    continue
        
        recent_views = sum(v['views'] for v in recent_videos)
        recent_likes = sum(v['likes'] for v in recent_videos)
        recent_comments = sum(v['comments'] for v in recent_videos)
        recent_engagement_rate = ((recent_likes + recent_comments) / recent_views * 100) if recent_views > 0 else 0
        
        return {
            'recent_videos_count': len(recent_videos),
            'very_recent_videos_count': len(very_recent_videos),
            'recent_views': recent_views,
            'recent_likes': recent_likes,
            'recent_comments': recent_comments,
            'recent_engagement_rate': round(recent_engagement_rate, 2),
            'recent_avg_views': round(recent_views / len(recent_videos), 2) if recent_videos else 0,
            'activity_level': 'high' if len(recent_videos) >= 5 else 'medium' if len(recent_videos) >= 2 else 'low'
        }
        
    except Exception as e:
        logger.error(f"Error analyzing recent playlist activity: {e}")
        return {}

def calculate_playlist_health(video_analytics: List[Dict[str, Any]], overall_engagement_rate: float, avg_views_per_video: float) -> Dict[str, Any]:
    """Calculate playlist health metrics"""
    try:
        # Health indicators
        health_score = 0
        health_factors = []
        
        # Engagement health
        if overall_engagement_rate > 5:
            health_score += 25
            health_factors.append('High engagement rate')
        elif overall_engagement_rate > 2:
            health_score += 15
            health_factors.append('Good engagement rate')
        else:
            health_factors.append('Low engagement rate')
        
        # View health
        if avg_views_per_video > 100:
            health_score += 25
            health_factors.append('High average views')
        elif avg_views_per_video > 50:
            health_score += 15
            health_factors.append('Good average views')
        else:
            health_factors.append('Low average views')
        
        # Consistency health
        view_values = [v['views'] for v in video_analytics]
        view_variance = sum((v - sum(view_values) / len(view_values)) ** 2 for v in view_values) / len(view_values)
        if view_variance < 1000:
            health_score += 25
            health_factors.append('Consistent performance')
        elif view_variance < 5000:
            health_score += 15
            health_factors.append('Moderate consistency')
        else:
            health_factors.append('Inconsistent performance')
        
        # Content quality health
        high_quality_videos = len([v for v in video_analytics if v['engagement_rate'] > 3 and v['views'] > 50])
        quality_ratio = high_quality_videos / len(video_analytics) if video_analytics else 0
        
        if quality_ratio > 0.7:
            health_score += 25
            health_factors.append('High quality content')
        elif quality_ratio > 0.4:
            health_score += 15
            health_factors.append('Good quality content')
        else:
            health_factors.append('Needs quality improvement')
        
        health_level = 'Excellent' if health_score >= 80 else 'Good' if health_score >= 60 else 'Fair' if health_score >= 40 else 'Poor'
        
        return {
            'health_score': health_score,
            'health_level': health_level,
            'health_factors': health_factors
        }
        
    except Exception as e:
        logger.error(f"Error calculating playlist health: {e}")
        return {}

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

def parse_duration_to_seconds(duration_str: str) -> int:
    """Parse YouTube duration (ISO 8601 format) to seconds"""
    try:
        import re
        
        # Parse ISO 8601 duration format (PT1H2M3S)
        pattern = r'PT(?:(\d+)H)?(?:(\d+)M)?(?:(\d+)S)?'
        match = re.match(pattern, duration_str)
        
        if not match:
            return 0
        
        hours = int(match.group(1) or 0)
        minutes = int(match.group(2) or 0)
        seconds = int(match.group(3) or 0)
        
        total_seconds = hours * 3600 + minutes * 60 + seconds
        return total_seconds
        
    except Exception as e:
        logger.error(f"Error parsing duration {duration_str}: {e}")
        return 0

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
        
        # Convert duration from ISO 8601 to seconds
        duration_str = content_details.get('duration', 'PT0S')
        duration_seconds = parse_duration_to_seconds(duration_str)
        
        return {
            'view_count': view_count,
            'like_count': like_count,
            'comment_count': comment_count,
            'duration': duration_str,
            'duration_seconds': duration_seconds,
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

def get_content_category(category_id: str) -> str:
    """Get content category name from category ID"""
    categories = {
        '1': 'Film & Animation',
        '2': 'Autos & Vehicles',
        '10': 'Music',
        '15': 'Pets & Animals',
        '17': 'Sports',
        '19': 'Travel & Events',
        '20': 'Gaming',
        '22': 'People & Blogs',
        '23': 'Comedy',
        '24': 'Entertainment',
        '25': 'News & Politics',
        '26': 'Howto & Style',
        '27': 'Education',
        '28': 'Science & Technology',
        '29': 'Nonprofits & Activism'
    }
    return categories.get(category_id, 'Other')

def calculate_growth_potential(views: int, likes: int, comments: int, days_since_published: int) -> str:
    """Calculate growth potential based on current performance"""
    try:
        if days_since_published == 0:
            return "New"
        
        views_per_day = views / days_since_published
        engagement_rate = ((likes + comments) / views * 100) if views > 0 else 0
        
        if views_per_day > 100 and engagement_rate > 5:
            return "High"
        elif views_per_day > 50 and engagement_rate > 2:
            return "Medium"
        elif views_per_day > 10:
            return "Low"
        else:
            return "Limited"
            
    except Exception as e:
        logger.error(f"Error calculating growth potential: {e}")
        return "Unknown"

def generate_video_recommendations(views: int, likes: int, comments: int, engagement_rate: float, performance_score: float, days_since_published: int) -> List[str]:
    """Generate recommendations for video improvement"""
    recommendations = []
    
    try:
        # Engagement recommendations
        if engagement_rate < 2:
            recommendations.append("Focus on creating more engaging content to increase likes and comments")
        elif engagement_rate < 5:
            recommendations.append("Consider adding calls-to-action to boost engagement")
        
        # Performance recommendations
        if performance_score < 100:
            recommendations.append("Optimize title and thumbnail for better click-through rates")
        elif performance_score < 500:
            recommendations.append("Consider promoting this video to increase visibility")
        
        # Content recommendations
        views_per_day = views / days_since_published if days_since_published > 0 else views
        if days_since_published < 7:
            recommendations.append("Video is new - give it time to gain traction")
        elif views_per_day < 10:
            recommendations.append("Consider updating thumbnail or title to improve performance")
        
        # Growth recommendations
        if views > 1000 and engagement_rate > 5:
            recommendations.append("This video is performing well - consider creating similar content")
        
        # Default recommendation if none apply
        if not recommendations:
            recommendations.append("Continue creating quality content and engaging with your audience")
            
    except Exception as e:
        logger.error(f"Error generating recommendations: {e}")
        recommendations.append("Focus on creating engaging content")
    
    return recommendations 

def get_channel_info(youtube) -> Dict[str, Any]:
    """Get channel information from YouTube API"""
    try:
        # Get channel information
        request = youtube.channels().list(
            part='snippet,statistics,brandingSettings',
            mine=True
        )
        response = request.execute()
        
        if not response['items']:
            return {}
        
        channel = response['items'][0]
        snippet = channel['snippet']
        statistics = channel['statistics']
        branding = channel.get('brandingSettings', {})
        
        return {
            'title': snippet.get('title', ''),
            'description': snippet.get('description', ''),
            'subscriber_count': int(statistics.get('subscriberCount', 0)),
            'view_count': int(statistics.get('viewCount', 0)),
            'video_count': int(statistics.get('videoCount', 0)),
            'published_at': snippet.get('publishedAt', ''),
            'thumbnail_url': snippet.get('thumbnails', {}).get('default', {}).get('url', ''),
            'country': snippet.get('country', ''),
            'custom_url': snippet.get('customUrl', ''),
            'keywords': branding.get('channel', {}).get('keywords', ''),
            'default_tab': branding.get('channel', {}).get('defaultTab', ''),
            'featured_channels_title': branding.get('channel', {}).get('featuredChannelsTitle', ''),
            'featured_channels_urls': branding.get('channel', {}).get('featuredChannelsUrls', [])
        }
        
    except Exception as e:
        logger.error(f"Error getting channel info: {e}")
        return {}

 