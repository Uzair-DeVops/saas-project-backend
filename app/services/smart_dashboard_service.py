"""
Smart Dashboard Service - Handles all dashboard data scenarios intelligently
"""
from typing import Dict, Any, List, Optional
from uuid import UUID
from sqlmodel import Session
from fastapi import HTTPException
from datetime import datetime

from ..services.dashboard_data_service import DashboardDataService
from ..services.youtube_cache_service import YouTubeCacheService
from ..services.dashboard_service import get_channel_info, get_all_playlists_comprehensive, get_all_user_videos_dashboard
from ..services.youtube_auth_service import get_youtube_client
from ..utils.my_logger import get_logger

logger = get_logger("SMART_DASHBOARD_SERVICE")

class SmartDashboardService:
    """Smart service that handles all dashboard data scenarios"""
    
    @staticmethod
    def get_overview_data(user_id: UUID, db: Session, refresh: bool = False) -> Dict[str, Any]:
        """Get overview data with smart caching and refresh logic"""
        try:
            logger.info(f"Smart overview request for user_id: {user_id}, refresh: {refresh}")
            
            # If refresh is requested, clear cache and fetch fresh data
            if refresh:
                logger.info(f"Refresh requested, clearing cache and fetching fresh data")
                YouTubeCacheService.clear_overview_cache(str(user_id), db)
                return SmartDashboardService._fetch_and_store_overview(user_id, db)
            
            # Check if we have cached data (persistent until user refresh)
            cached_data = YouTubeCacheService.get_overview_cache(str(user_id), db)
            
            if cached_data:
                cache_age = YouTubeCacheService.get_cache_age_minutes(cached_data)
                logger.info(f"Using persistent cached overview data (age: {cache_age} minutes)")
                return {
                    "success": True,
                    "message": f"Using cached overview data (age: {cache_age} minutes) - use ?refresh=true to get fresh data",
                    "data": SmartDashboardService._convert_cached_overview_to_original_structure(cached_data),
                    "cache_info": {
                        "is_cached": True,
                        "age_minutes": cache_age,
                        "last_updated": cached_data.data_updated_at.isoformat()
                    }
                }
            
            # No cached data, fetch fresh data
            logger.info(f"No cached data found, fetching fresh overview data")
            return SmartDashboardService._fetch_and_store_overview(user_id, db)
            
        except Exception as e:
            logger.error(f"Error in smart overview service: {e}")
            raise HTTPException(
                status_code=500,
                detail="Internal server error while getting overview data"
            )
    
    @staticmethod
    def get_playlists_data(user_id: UUID, db: Session, refresh: bool = False) -> Dict[str, Any]:
        """Get playlists data with smart caching and refresh logic"""
        try:
            logger.info(f"Smart playlists request for user_id: {user_id}, refresh: {refresh}")
            
            # If refresh is requested, clear cache and fetch fresh data
            if refresh:
                logger.info(f"Refresh requested, clearing cache and fetching fresh data")
                YouTubeCacheService.clear_playlists_cache(str(user_id), db)
                # For refresh, we'll fetch all playlists individually to ensure proper caching
                return SmartDashboardService._fetch_all_playlists_individually(user_id, db)
            
            # Check if we have cached data (persistent until user refresh)
            cached_data = YouTubeCacheService.get_playlists_cache(str(user_id), db)
            
            if cached_data:
                cache_age = YouTubeCacheService.get_cache_age_minutes(cached_data[0]) if cached_data else 0
                logger.info(f"Using persistent cached playlists data (age: {cache_age} minutes)")
                return {
                    "success": True,
                    "message": f"Using cached playlists data (age: {cache_age} minutes) - use ?refresh=true to get fresh data",
                    "data": [SmartDashboardService._convert_cached_playlist_to_original_structure(playlist) for playlist in cached_data],
                    "count": len(cached_data),
                    "cache_info": {
                        "is_cached": True,
                        "age_minutes": cache_age,
                        "last_updated": cached_data[0].data_updated_at.isoformat() if cached_data else None
                    }
                }
            
            # No cached data, fetch fresh data
            logger.info(f"No cached data found, fetching fresh playlists data")
            return SmartDashboardService._fetch_all_playlists_individually(user_id, db)
            
        except Exception as e:
            logger.error(f"Error in smart playlists service: {e}")
            raise HTTPException(
                status_code=500,
                detail="Internal server error while getting playlists data"
            )
    
    @staticmethod
    def get_videos_data(user_id: UUID, db: Session, refresh: bool = False) -> Dict[str, Any]:
        """Get videos data with smart caching and refresh logic"""
        try:
            logger.info(f"Smart videos request for user_id: {user_id}, refresh: {refresh}")
            
            # If refresh is requested, clear cache and fetch fresh data
            if refresh:
                logger.info(f"Refresh requested, clearing cache and fetching fresh data")
                YouTubeCacheService.clear_videos_cache(str(user_id), db)
                return SmartDashboardService._fetch_and_store_videos(user_id, db)
            
            # Check if we have cached data (persistent until user refresh)
            cached_data = YouTubeCacheService.get_videos_cache(str(user_id), db)
            
            if cached_data:
                cache_age = YouTubeCacheService.get_cache_age_minutes(cached_data[0]) if cached_data else 0
                logger.info(f"Using persistent cached videos data (age: {cache_age} minutes)")
                return {
                    "success": True,
                    "message": f"Using cached videos data (age: {cache_age} minutes) - use ?refresh=true to get fresh data",
                    "data": SmartDashboardService._convert_cached_videos_to_original_structure(cached_data),
                    "count": len(cached_data),
                    "cache_info": {
                        "is_cached": True,
                        "age_minutes": cache_age,
                        "last_updated": cached_data[0].data_updated_at.isoformat() if cached_data else None
                    }
                }
            
            # No cached data, fetch fresh data
            logger.info(f"No cached data found, fetching fresh videos data")
            return SmartDashboardService._fetch_and_store_videos(user_id, db)
            
        except Exception as e:
            logger.error(f"Error in smart videos service: {e}")
            raise HTTPException(
                status_code=500,
                detail="Internal server error while getting videos data"
            )
    
    @staticmethod
    def get_playlist_data(user_id: UUID, playlist_id: str, db: Session, refresh: bool = False) -> Dict[str, Any]:
        """Get single playlist data with smart caching and refresh logic"""
        try:
            logger.info(f"Smart playlist request for user_id: {user_id}, playlist_id: {playlist_id}, refresh: {refresh}")
            
            # If refresh is requested, clear cache and fetch fresh data
            if refresh:
                logger.info(f"Refresh requested, clearing cache and fetching fresh data")
                YouTubeCacheService.clear_playlist_videos_cache(str(user_id), playlist_id, db)
                return SmartDashboardService._fetch_and_store_single_playlist(user_id, playlist_id, db)
            
            # Check if we have cached data
            cached_data = YouTubeCacheService.get_single_playlist_cache(str(user_id), playlist_id, db)
            
            if cached_data:
                cache_age = YouTubeCacheService.get_cache_age_minutes(cached_data)
                logger.info(f"Using cached playlist data (age: {cache_age} minutes)")
                return {
                    "success": True,
                    "message": f"Using cached playlist data (age: {cache_age} minutes)",
                    "data": SmartDashboardService._convert_cached_playlist_to_original_structure(cached_data),
                    "cache_info": {
                        "is_cached": True,
                        "age_minutes": cache_age,
                        "last_updated": cached_data.data_updated_at.isoformat()
                    }
                }
            
            # No cached data, fetch fresh data
            logger.info(f"No cached data found, fetching fresh playlist data")
            return SmartDashboardService._fetch_and_store_single_playlist(user_id, playlist_id, db)
            
        except Exception as e:
            logger.error(f"Error in smart playlist service: {e}")
            raise HTTPException(
                status_code=500,
                detail="Internal server error while getting playlist data"
            )
    
    @staticmethod
    def get_video_data(user_id: UUID, video_id: str, db: Session, refresh: bool = False) -> Dict[str, Any]:
        """Get single video data with smart caching and refresh logic"""
        try:
            logger.info(f"Smart video request for user_id: {user_id}, video_id: {video_id}, refresh: {refresh}")
            
            # If refresh is requested, fetch fresh data
            if refresh:
                logger.info(f"Refresh requested, fetching fresh video data")
                return SmartDashboardService._fetch_and_store_single_video(user_id, video_id, db)
            
            # Check if we have cached data
            cached_data = YouTubeCacheService.get_single_video_cache(str(user_id), video_id, db)
            
            if cached_data:
                cache_age = YouTubeCacheService.get_cache_age_minutes(cached_data)
                logger.info(f"Using cached video data (age: {cache_age} minutes)")
                return {
                    "success": True,
                    "message": f"Using cached video data (age: {cache_age} minutes)",
                    "data": SmartDashboardService._convert_cached_video_to_original_structure(cached_data),
                    "cache_info": {
                        "is_cached": True,
                        "age_minutes": cache_age,
                        "last_updated": cached_data.data_updated_at.isoformat()
                    }
                }
            
            # No cached data, fetch fresh data
            logger.info(f"No cached data found, fetching fresh video data")
            return SmartDashboardService._fetch_and_store_single_video(user_id, video_id, db)
            
        except Exception as e:
            logger.error(f"Error in smart video service: {e}")
            raise HTTPException(
                status_code=500,
                detail="Internal server error while getting video data"
            )
    
    @staticmethod
    def get_playlist_videos_data(user_id: UUID, playlist_id: str, db: Session, refresh: bool = False) -> Dict[str, Any]:
        """Get playlist videos data with smart caching and refresh logic"""
        try:
            logger.info(f"Smart playlist videos request for user_id: {user_id}, playlist_id: {playlist_id}, refresh: {refresh}")
            
            # If refresh is requested, clear cache and fetch fresh data
            if refresh:
                logger.info(f"Refresh requested, clearing cache and fetching fresh data")
                YouTubeCacheService.clear_playlist_videos_cache(str(user_id), playlist_id, db)
                return SmartDashboardService._fetch_and_store_playlist_videos(user_id, playlist_id, db)
            
            # Check if we have cached data
            cached_data = YouTubeCacheService.get_playlist_videos_cache(str(user_id), playlist_id, db)
            
            if cached_data:
                # cached_data is now a list of tuples (video, position)
                first_video = cached_data[0][0] if cached_data else None
                cache_age = YouTubeCacheService.get_cache_age_minutes(first_video) if first_video else 0
                logger.info(f"Using persistent cached playlist videos data (age: {cache_age} minutes)")
                return {
                    "success": True,
                    "message": f"Using cached playlist videos data (age: {cache_age} minutes) - use ?refresh=true to get fresh data",
                    "data": SmartDashboardService._convert_cached_playlist_videos_to_original_structure(cached_data),
                    "count": len(cached_data),
                    "cache_info": {
                        "is_cached": True,
                        "age_minutes": cache_age,
                        "last_updated": first_video.data_updated_at.isoformat() if first_video else None
                    }
                }
            
            # No cached data, fetch fresh data
            logger.info(f"No cached data found, fetching fresh playlist videos data")
            return SmartDashboardService._fetch_and_store_playlist_videos(user_id, playlist_id, db)
            
        except Exception as e:
            logger.error(f"Error in smart playlist videos service: {e}")
            raise HTTPException(
                status_code=500,
                detail="Internal server error while getting playlist videos data"
            )

    @staticmethod
    def get_playlist_names_data(user_id: UUID, db: Session, refresh: bool = False) -> Dict[str, Any]:
        """Get playlist names and IDs with smart caching and refresh logic"""
        try:
            logger.info(f"Smart playlist names request for user_id: {user_id}, refresh: {refresh}")
            
            # If refresh is requested, clear cache and fetch fresh data
            if refresh:
                logger.info(f"Refresh requested, clearing cache and fetching fresh data")
                YouTubeCacheService.clear_playlist_names_cache(str(user_id), db)
                return SmartDashboardService._fetch_playlist_names_fresh(user_id, db)
            
            # Check if we have cached data (persistent until user refresh)
            cached_data = YouTubeCacheService.get_playlist_names_cache(str(user_id), db)
            
            if cached_data:
                cache_age = YouTubeCacheService.get_cache_age_minutes(cached_data[0]) if cached_data else 0
                logger.info(f"Using persistent cached playlist names data (age: {cache_age} minutes)")
                
                # Convert cached data to simple name/ID format
                playlist_names = []
                for playlist in cached_data:
                    playlist_names.append({
                        'playlist_id': playlist.playlist_id,
                        'title': playlist.title
                    })
                
                return {
                    "success": True,
                    "message": f"Using cached playlist names data (age: {cache_age} minutes) - use ?refresh=true to get fresh data",
                    "data": playlist_names,
                    "count": len(playlist_names),
                    "cache_info": {
                        "is_cached": True,
                        "age_minutes": cache_age,
                        "last_updated": cached_data[0].data_updated_at.isoformat() if cached_data else None
                    }
                }
            
            # No cached data, fetch fresh data
            logger.info(f"No cached data found, fetching fresh playlist names data")
            return SmartDashboardService._fetch_playlist_names_fresh(user_id, db)
            
        except Exception as e:
            logger.error(f"Error in smart playlist names service: {e}")
            raise HTTPException(
                status_code=500,
                detail="Internal server error while getting playlist names data"
            )

    # Private methods for fetching and storing data
    @staticmethod
    def _convert_cached_overview_to_original_structure(cached_data) -> Dict[str, Any]:
        """Convert cached overview data back to original nested structure"""
        try:
            import json
            
            # Parse JSON strings back to objects
            top_performing_content = json.loads(cached_data.top_performing_content) if cached_data.top_performing_content else {}
            monthly_analytics = json.loads(cached_data.monthly_analytics) if cached_data.monthly_analytics else {}
            content_analysis = json.loads(cached_data.content_analysis) if cached_data.content_analysis else {}
            advanced_analytics = json.loads(cached_data.advanced_analytics) if cached_data.advanced_analytics else {}
            performance_scoring = json.loads(cached_data.performance_scoring) if cached_data.performance_scoring else {}
            weekly_analytics = json.loads(cached_data.weekly_analytics) if cached_data.weekly_analytics else {}
            content_insights = json.loads(cached_data.content_insights) if cached_data.content_insights else {}
            enhanced_channel_info = json.loads(cached_data.enhanced_channel_info) if cached_data.enhanced_channel_info else {}
            monetization_data = json.loads(cached_data.monetization_data) if cached_data.monetization_data else {}
            audience_insights = json.loads(cached_data.audience_insights) if cached_data.audience_insights else {}
            seo_metrics = json.loads(cached_data.seo_metrics) if cached_data.seo_metrics else {}
            content_strategy = json.loads(cached_data.content_strategy) if cached_data.content_strategy else {}
            technical_metrics = json.loads(cached_data.technical_metrics) if cached_data.technical_metrics else {}
            business_metrics = json.loads(cached_data.business_metrics) if cached_data.business_metrics else {}
            
            # Reconstruct the original nested structure
            return {
                'channel_info': {
                    'title': cached_data.channel_title,
                    'description': cached_data.channel_description,
                    'subscriber_count': cached_data.subscriber_count,
                    'total_views': cached_data.total_views,
                    'total_videos': cached_data.total_videos,
                    'total_likes': cached_data.total_likes,
                    'total_comments': cached_data.total_comments,
                    'total_duration': cached_data.total_duration,
                    'created_at': cached_data.created_at.isoformat() if cached_data.created_at else None,
                    'thumbnail_url': cached_data.thumbnail_url,
                    'country': cached_data.country,
                    'custom_url': cached_data.custom_url,
                    'keywords': cached_data.keywords,
                    'featured_channels_title': cached_data.featured_channels_title,
                    'featured_channels_urls': json.loads(cached_data.featured_channels_urls) if cached_data.featured_channels_urls else []
                },
                'performance_metrics': {
                    'avg_views_per_video': cached_data.avg_views_per_video,
                    'avg_likes_per_video': cached_data.avg_likes_per_video,
                    'avg_comments_per_video': cached_data.avg_comments_per_video,
                    'avg_duration_per_video': cached_data.avg_duration_per_video,
                    'overall_engagement_rate': cached_data.overall_engagement_rate,
                    'videos_per_month': cached_data.videos_per_month,
                    'views_per_month': cached_data.views_per_month,
                    'subscribers_per_month': cached_data.subscribers_per_month,
                    'days_since_created': cached_data.days_since_created,
                    'channel_age_months': cached_data.channel_age_months
                },
                'recent_performance': {
                    'recent_videos_count': cached_data.recent_videos_count,
                    'recent_views': cached_data.recent_views,
                    'recent_likes': cached_data.recent_likes,
                    'recent_comments': cached_data.recent_comments,
                    'recent_engagement_rate': cached_data.recent_engagement_rate,
                    'recent_avg_views': cached_data.recent_avg_views
                },
                'top_performing_content': top_performing_content,
                'monthly_analytics': monthly_analytics,
                'content_analysis': content_analysis,
                'channel_status': {
                    'is_active': cached_data.is_active,
                    'engagement_level': cached_data.engagement_level,
                    'growth_stage': cached_data.growth_stage,
                    'content_quality': cached_data.content_quality,
                    'upload_consistency': cached_data.upload_consistency
                },
                'summary_stats': {
                    'total_watch_time_hours': cached_data.total_watch_time_hours,
                    'avg_video_length_minutes': cached_data.avg_video_length_minutes,
                    'total_interactions': cached_data.total_interactions,
                    'interaction_rate': cached_data.interaction_rate,
                    'subscriber_to_view_ratio': cached_data.subscriber_to_view_ratio
                },
                'growth_insights': {
                    'subscriber_growth_rate': cached_data.subscriber_growth_rate,
                    'view_growth_rate': cached_data.view_growth_rate,
                    'video_upload_frequency': cached_data.video_upload_frequency,
                    'engagement_growth': cached_data.engagement_growth
                },
                'advanced_analytics': advanced_analytics,
                'performance_scoring': performance_scoring,
                'weekly_analytics': weekly_analytics,
                'content_insights': content_insights,
                'competitive_analysis': {
                    'channel_health_score': cached_data.channel_health_score,
                    'growth_potential': cached_data.growth_potential,
                    'audience_loyalty': cached_data.audience_loyalty,
                    'content_consistency': cached_data.content_consistency
                },
                'enhanced_channel_info': enhanced_channel_info,
                'monetization_data': monetization_data,
                'audience_insights': audience_insights,
                'seo_metrics': seo_metrics,
                'content_strategy': content_strategy,
                'technical_metrics': technical_metrics,
                'business_metrics': business_metrics
            }
        except Exception as e:
            logger.error(f"Error converting cached overview data: {e}")
            # Fallback to model_dump if conversion fails
            return cached_data.model_dump()

    @staticmethod
    def _convert_cached_playlist_to_original_structure(cached_data) -> Dict[str, Any]:
        """Convert cached playlist data back to original nested structure"""
        try:
            import json
            
            # Parse JSON strings back to objects
            analytics = json.loads(cached_data.analytics) if cached_data.analytics else {}
            
            # Reconstruct the original nested structure
            return {
                'playlist_info': {
                    'playlist_id': cached_data.playlist_id,
                    'title': cached_data.title,
                    'description': cached_data.description,
                    'published_at': cached_data.published_at.isoformat() if cached_data.published_at else None,
                    'thumbnail_url': cached_data.standard_thumbnail or cached_data.default_thumbnail or cached_data.high_thumbnail or cached_data.maxres_thumbnail or "",
                    'channel_title': cached_data.channel_title,
                    'channel_id': cached_data.channel_id,
                    'privacy_status': 'public' if cached_data.is_public else 'private' if cached_data.is_private else 'unlisted',
                    'video_count': cached_data.video_count,
                    'tags': [],  # Playlist model doesn't store tags
                    'default_language': "",  # Playlist model doesn't store default_language
                    'localized': {
                        'title': cached_data.title,
                        'description': cached_data.description
                    }
                },
                'analytics': analytics
            }
        except Exception as e:
            logger.error(f"Error converting cached playlist data: {e}")
            # Fallback to model_dump if conversion fails
            return cached_data.model_dump()

    @staticmethod
    def _convert_cached_playlist_videos_to_original_structure(cached_videos_with_positions: List) -> List[Dict[str, Any]]:
        """Convert cached playlist videos data back to original structure"""
        try:
            import json
            from datetime import datetime
            
            converted_videos = []
            for video, position in cached_videos_with_positions:
                # Parse JSON strings back to objects
                tags = json.loads(video.tags) if video.tags else []
                analytics = json.loads(video.analytics) if video.analytics else {}
                
                # Clean up analytics object to only include non-repetitive fields
                cleaned_analytics = {
                    'category_id': analytics.get('category_id'),
                    'default_language': analytics.get('default_language'),
                    'default_audio_language': analytics.get('default_audio_language')
                }
                
                # Calculate days since published
                days_since_published = 0
                if video.published_at:
                    days_since_published = (datetime.now() - video.published_at).days
                
                # Calculate engagement rate
                engagement_rate = 0
                if video.view_count and video.view_count > 0:
                    total_engagement = (video.like_count or 0) + (video.comment_count or 0)
                    engagement_rate = round((total_engagement / video.view_count) * 100, 2)
                
                # Calculate performance score
                performance_score = 0
                if video.view_count:
                    performance_score = round(
                        (video.view_count * 0.4) + 
                        ((video.like_count or 0) * 10) + 
                        ((video.comment_count or 0) * 5) + 
                        (engagement_rate * 2), 1
                    )
                
                converted_video = {
                    'title': video.title,
                    'url': f"https://www.youtube.com/watch?v={video.video_id}",
                    'video_id': video.video_id,
                    'published_at': video.published_at.isoformat() + 'Z' if video.published_at else None,
                    'description': video.description,
                    'thumbnail_url': video.thumbnail_url,
                    'position': position,  # Use position from tuple
                    'view_count': video.view_count,
                    'like_count': video.like_count,
                    'comment_count': video.comment_count,
                    'duration': video.duration,
                    'privacy_status': video.privacy_status,
                    'engagement_rate': engagement_rate,
                    'performance_score': performance_score,
                    'days_since_published': days_since_published,
                    'analytics': cleaned_analytics
                }
                converted_videos.append(converted_video)
            
            return converted_videos
        except Exception as e:
            logger.error(f"Error converting cached playlist videos data: {e}")
            # Fallback to model_dump if conversion fails
            return [video.model_dump() for video, _ in cached_videos_with_positions]

    @staticmethod
    def _convert_cached_videos_to_original_structure(cached_videos: List) -> List[Dict[str, Any]]:
        """Convert cached videos data back to original structure"""
        try:
            import json
            from datetime import datetime
            
            converted_videos = []
            for video in cached_videos:
                # Parse JSON strings back to objects
                tags = json.loads(video.tags) if video.tags else []
                analytics = json.loads(video.analytics) if video.analytics else {}
                
                # Clean up analytics object to only include non-repetitive fields
                cleaned_analytics = {
                    'category_id': analytics.get('category_id'),
                    'default_language': analytics.get('default_language'),
                    'default_audio_language': analytics.get('default_audio_language')
                }
                
                # Calculate days since published
                days_since_published = 0
                if video.published_at:
                    days_since_published = (datetime.now() - video.published_at).days
                
                # Calculate engagement rate
                engagement_rate = 0
                if video.view_count and video.view_count > 0:
                    total_engagement = (video.like_count or 0) + (video.comment_count or 0)
                    engagement_rate = round((total_engagement / video.view_count) * 100, 2)
                
                # Calculate performance score
                performance_score = 0
                if video.view_count:
                    performance_score = round(
                        (video.view_count * 0.4) + 
                        ((video.like_count or 0) * 10) + 
                        ((video.comment_count or 0) * 5) + 
                        (engagement_rate * 2), 1
                    )
                
                converted_video = {
                    'video_id': video.video_id,
                    'title': video.title,
                    'url': f"https://www.youtube.com/watch?v={video.video_id}",
                    'description': video.description,
                    'thumbnail_url': video.thumbnail_url,
                    'published_at': video.published_at.isoformat() + 'Z' if video.published_at else None,
                    'duration': video.duration,
                    'duration_seconds': video.duration_seconds,
                    'channel_id': video.channel_id,
                    'channel_title': video.channel_title,
                    'view_count': video.view_count,
                    'like_count': video.like_count,
                    'comment_count': video.comment_count,
                    'privacy_status': video.privacy_status,
                    'upload_status': video.upload_status,
                    'license': video.license,
                    'made_for_kids': video.made_for_kids,
                    'category_id': video.category_id,
                    'tags': tags,
                    'default_language': video.default_language,
                    'default_audio_language': video.default_audio_language,
                    'engagement_rate': engagement_rate,
                    'performance_score': performance_score,
                    'days_since_published': days_since_published,
                    'analytics': cleaned_analytics
                }
                converted_videos.append(converted_video)
            
            return converted_videos
        except Exception as e:
            logger.error(f"Error converting cached videos data: {e}")
            # Fallback to model_dump if conversion fails
            return [video.model_dump() for video in cached_videos]

    @staticmethod
    def _convert_cached_video_to_original_structure(cached_video) -> Dict[str, Any]:
        """Convert cached single video data back to original structure"""
        try:
            import json
            from datetime import datetime
            
            # Parse JSON strings back to objects
            tags = json.loads(cached_video.tags) if cached_video.tags else []
            analytics = json.loads(cached_video.analytics) if cached_video.analytics else {}
            
            # Clean up analytics object to only include non-repetitive fields
            cleaned_analytics = {
                'category_id': analytics.get('category_id'),
                'default_language': analytics.get('default_language'),
                'default_audio_language': analytics.get('default_audio_language')
            }
            
            # Calculate days since published
            days_since_published = 0
            if cached_video.published_at:
                days_since_published = (datetime.now() - cached_video.published_at).days
            
            # Calculate engagement rate
            engagement_rate = 0
            if cached_video.view_count and cached_video.view_count > 0:
                total_engagement = (cached_video.like_count or 0) + (cached_video.comment_count or 0)
                engagement_rate = round((total_engagement / cached_video.view_count) * 100, 2)
            
            # Calculate performance score
            performance_score = 0
            if cached_video.view_count:
                performance_score = round(
                    (cached_video.view_count * 0.4) + 
                    ((cached_video.like_count or 0) * 10) + 
                    ((cached_video.comment_count or 0) * 5) + 
                    (engagement_rate * 2), 1
                )
            
            return {
                'video_id': cached_video.video_id,
                'title': cached_video.title,
                'url': f"https://www.youtube.com/watch?v={cached_video.video_id}",
                'description': cached_video.description,
                'thumbnail_url': cached_video.thumbnail_url,
                'published_at': cached_video.published_at.isoformat() + 'Z' if cached_video.published_at else None,
                'duration': cached_video.duration,
                'duration_seconds': cached_video.duration_seconds,
                'channel_id': cached_video.channel_id,
                'channel_title': cached_video.channel_title,
                'view_count': cached_video.view_count,
                'like_count': cached_video.like_count,
                'comment_count': cached_video.comment_count,
                'privacy_status': cached_video.privacy_status,
                'upload_status': cached_video.upload_status,
                'license': cached_video.license,
                'made_for_kids': cached_video.made_for_kids,
                'category_id': cached_video.category_id,
                'tags': tags,
                'default_language': cached_video.default_language,
                'default_audio_language': cached_video.default_audio_language,
                'engagement_rate': engagement_rate,
                'performance_score': performance_score,
                'days_since_published': days_since_published,
                'analytics': cleaned_analytics
            }
        except Exception as e:
            logger.error(f"Error converting cached video data: {e}")
            # Fallback to model_dump if conversion fails
            return cached_video.model_dump()

    @staticmethod
    def _fetch_and_store_overview(user_id: UUID, db: Session) -> Dict[str, Any]:
        """Fetch and store overview data"""
        try:
            # Get YouTube client
            youtube = get_youtube_client(user_id, db)
            if not youtube:
                raise HTTPException(
                    status_code=500,
                    detail="Failed to get YouTube client. Please check your YouTube API credentials."
                )
            
            # Import the dashboard overview service
            from ..services.dashboard_overview_service import generate_dashboard_overview_data
            
            # Get overview data
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
            
            logger.info(f"Successfully fetched and stored fresh overview data")
            
            return {
                "success": True,
                "message": "Fresh overview data fetched and stored successfully",
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
            logger.error(f"Error fetching overview data: {e}")
            raise HTTPException(
                status_code=500,
                detail="Internal server error while fetching overview data"
            )
    

    
    @staticmethod
    def _fetch_all_playlists_individually(user_id: UUID, db: Session) -> Dict[str, Any]:
        """Fetch and store all playlists individually to ensure proper caching"""
        try:
            # Get YouTube client
            youtube = get_youtube_client(user_id, db)
            if not youtube:
                raise HTTPException(
                    status_code=500,
                    detail="Failed to get YouTube client. Please check your YouTube API credentials."
                )
            
            # Get all playlists data
            raw_playlists_data = get_all_playlists_comprehensive(youtube)
            
            if not raw_playlists_data:
                raise HTTPException(
                    status_code=500,
                    detail="Failed to fetch playlists data from YouTube API."
                )
            
            # Store each playlist individually
            stored_playlists = []
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
                
                # Store individual playlist
                success = DashboardDataService.store_single_playlist_data(user_id, playlist_data, db)
                if success:
                    stored_playlists.append(playlist_data)
            
            if not stored_playlists:
                raise HTTPException(
                    status_code=500,
                    detail="Failed to store any playlists data in database."
                )
            
            logger.info(f"Successfully fetched and stored {len(stored_playlists)} playlists individually")
            
            return {
                "success": True,
                "message": f"Fresh playlists data fetched and stored successfully ({len(stored_playlists)} playlists)",
                "data": stored_playlists,
                "count": len(stored_playlists),
                "cache_info": {
                    "is_cached": False,
                    "age_minutes": 0,
                    "last_updated": datetime.now().isoformat()
                }
            }
            
        except HTTPException:
            raise
        except Exception as e:
            logger.error(f"Error fetching playlists data: {e}")
            raise HTTPException(
                status_code=500,
                detail="Internal server error while fetching playlists data"
            )

    @staticmethod
    def _fetch_and_store_videos(user_id: UUID, db: Session) -> Dict[str, Any]:
        """Fetch and store videos data"""
        try:
            # Get YouTube client
            youtube = get_youtube_client(user_id, db)
            if not youtube:
                raise HTTPException(
                    status_code=500,
                    detail="Failed to get YouTube client. Please check your YouTube API credentials."
                )
            
            # Get videos data
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
            
            logger.info(f"Successfully fetched and stored {len(videos_data)} videos")
            
            return {
                "success": True,
                "message": f"Fresh videos data fetched and stored successfully ({len(videos_data)} videos)",
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
            logger.error(f"Error fetching videos data: {e}")
            raise HTTPException(
                status_code=500,
                detail="Internal server error while fetching videos data"
            )
    
    @staticmethod
    def _fetch_and_store_single_playlist(user_id: UUID, playlist_id: str, db: Session) -> Dict[str, Any]:
        """Fetch and store single playlist data"""
        try:
            # Get YouTube client
            youtube = get_youtube_client(user_id, db)
            if not youtube:
                raise HTTPException(
                    status_code=500,
                    detail="Failed to get YouTube client. Please check your YouTube API credentials."
                )
            
            # Import the existing comprehensive playlist logic
            from ..controllers.dashboard_controller import get_comprehensive_playlist_controller
            
            # Get single playlist data
            playlist_data = get_comprehensive_playlist_controller(user_id, playlist_id, db)
            
            if not playlist_data:
                raise HTTPException(
                    status_code=404,
                    detail="Playlist not found or you don't have permission to access it"
                )
            
            # Store single playlist in database (without deleting other playlists)
            success = DashboardDataService.store_single_playlist_data(user_id, playlist_data, db)
            
            if not success:
                raise HTTPException(
                    status_code=500,
                    detail="Failed to store playlist data in database."
                )
            
            logger.info(f"Successfully fetched and stored single playlist data")
            
            return {
                "success": True,
                "message": "Fresh playlist data fetched and stored successfully",
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
            logger.error(f"Error fetching playlist data: {e}")
            raise HTTPException(
                status_code=500,
                detail="Internal server error while fetching playlist data"
            )
    
    @staticmethod
    def _fetch_and_store_single_video(user_id: UUID, video_id: str, db: Session) -> Dict[str, Any]:
        """Fetch and store single video data"""
        try:
            # Get YouTube client
            youtube = get_youtube_client(user_id, db)
            if not youtube:
                raise HTTPException(
                    status_code=500,
                    detail="Failed to get YouTube client. Please check your YouTube API credentials."
                )
            
            # Import the existing video details logic
            from ..controllers.dashboard_controller import get_video_details_controller
            
            # Get video data
            video_data = get_video_details_controller(user_id, video_id, db)
            
            if not video_data:
                raise HTTPException(
                    status_code=404,
                    detail="Video not found or you don't have permission to access it"
                )
            
            # Store single video in database (without deleting other videos)
            success = DashboardDataService.store_single_video_data(user_id, video_data, db)
            
            if not success:
                raise HTTPException(
                    status_code=500,
                    detail="Failed to store video data in database."
                )
            
            logger.info(f"Successfully fetched and stored single video data")
            
            return {
                "success": True,
                "message": "Fresh video data fetched and stored successfully",
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
            logger.error(f"Error fetching video data: {e}")
            raise HTTPException(
                status_code=500,
                detail="Internal server error while fetching video data"
            )

    @staticmethod
    def _fetch_and_store_playlist_videos(user_id: UUID, playlist_id: str, db: Session) -> Dict[str, Any]:
        """Fetch and store playlist videos data"""
        try:
            # Get YouTube client
            youtube = get_youtube_client(user_id, db)
            if not youtube:
                raise HTTPException(
                    status_code=500,
                    detail="Failed to get YouTube client. Please check your YouTube API credentials."
                )
            
            # Import the existing playlist videos logic
            from ..controllers.dashboard_controller import get_playlist_videos_controller
            
            # Get playlist videos data
            videos_data = get_playlist_videos_controller(user_id, playlist_id, db)
            
            if not videos_data:
                return {
                    "success": True,
                    "message": "No videos found for this playlist",
                    "data": [],
                    "count": 0,
                    "cache_info": {
                        "is_cached": False,
                        "age_minutes": 0,
                        "last_updated": datetime.now().isoformat()
                    }
                }
            
            # Store in database
            success = DashboardDataService.store_playlist_videos_data(user_id, playlist_id, videos_data, db)
            
            if not success:
                raise HTTPException(
                    status_code=500,
                    detail="Failed to store playlist videos data in database."
                )
            
            logger.info(f"Successfully fetched and stored playlist videos data")
            
            return {
                "success": True,
                "message": "Fresh playlist videos data fetched and stored successfully",
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
            logger.error(f"Error fetching playlist videos data: {e}")
            raise HTTPException(
                status_code=500,
                detail="Internal server error while fetching playlist videos data"
            )

    @staticmethod
    def _fetch_playlist_names_fresh(user_id: UUID, db: Session) -> Dict[str, Any]:
        """Fetch fresh playlist names and IDs from YouTube"""
        try:
            # Get YouTube client
            youtube = get_youtube_client(user_id, db)
            if not youtube:
                raise HTTPException(
                    status_code=500,
                    detail="Failed to get YouTube client. Please check your YouTube API credentials."
                )
            
            # Import the playlist service for simple playlist fetching
            from ..services.playlist_service import get_user_playlists
            
            # Get all playlists (simple call without analytics)
            playlists_data = get_user_playlists(youtube)
            
            if not playlists_data:
                return {
                    "success": True,
                    "message": "No playlists found",
                    "data": [],
                    "count": 0,
                    "cache_info": {
                        "is_cached": False,
                        "age_minutes": 0,
                        "last_updated": datetime.now().isoformat()
                    }
                }
            
            # Extract only playlist_id and title
            playlist_names = []
            for playlist in playlists_data:
                playlist_names.append({
                    'playlist_id': playlist['id'],
                    'title': playlist['title']
                })
            
            # Store playlist names data in cache for future use
            success = DashboardDataService.store_playlist_names_data(user_id, playlist_names, db)
            
            if not success:
                logger.warning("Failed to store full playlist data in cache, but returning playlist names")
            
            logger.info(f"Successfully fetched {len(playlist_names)} playlist names")
            
            return {
                "success": True,
                "message": "Fresh playlist names data fetched successfully",
                "data": playlist_names,
                "count": len(playlist_names),
                "cache_info": {
                    "is_cached": False,
                    "age_minutes": 0,
                    "last_updated": datetime.now().isoformat()
                }
            }
            
        except HTTPException:
            raise
        except Exception as e:
            logger.error(f"Error fetching playlist names data: {e}")
            raise HTTPException(
                status_code=500,
                detail="Internal server error while fetching playlist names data"
            )
