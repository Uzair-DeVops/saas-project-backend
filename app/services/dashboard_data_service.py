"""
Dashboard Data Service - Handles database operations for dashboard data
"""
import json
from typing import Dict, Any, List, Optional
from uuid import UUID
from sqlmodel import Session, select
from datetime import datetime
import re

from ..models.dashboard_overview_model import DashboardOverview
from ..models.dashboard_playlist_model import DashboardPlaylist
from ..models.dashboard_video_model import DashboardVideo
from ..models.dashboard_playlist_video_model import DashboardPlaylistVideo
from ..utils.my_logger import get_logger

logger = get_logger("DASHBOARD_DATA_SERVICE")

class DashboardDataService:
    """Service for managing dashboard data in database"""
    
    @staticmethod
    def store_overview_data(user_id: UUID, overview_data: Dict[str, Any], db: Session) -> bool:
        """Store dashboard overview data in database"""
        try:
            # Delete existing overview data for user
            db.query(DashboardOverview).filter(DashboardOverview.user_id == user_id).delete()
            
            # Extract basic fields from overview data
            channel_info = overview_data.get('channel_info', {})
            performance_metrics = overview_data.get('performance_metrics', {})
            recent_performance = overview_data.get('recent_performance', {})
            channel_status = overview_data.get('channel_status', {})
            summary_stats = overview_data.get('summary_stats', {})
            growth_insights = overview_data.get('growth_insights', {})
            competitive_analysis = overview_data.get('competitive_analysis', {})
            
            # Create new overview record
            overview_record = DashboardOverview(
                user_id=user_id,
                
                # Channel Info
                channel_title=channel_info.get('title', ''),
                channel_description=channel_info.get('description', ''),
                subscriber_count=channel_info.get('subscriber_count', 0),
                total_views=channel_info.get('total_views', 0),
                total_videos=channel_info.get('total_videos', 0),
                total_likes=channel_info.get('total_likes', 0),
                total_comments=channel_info.get('total_comments', 0),
                total_duration=channel_info.get('total_duration', 0),
                created_at=parse_datetime(channel_info.get('created_at', datetime.utcnow())),
                thumbnail_url=channel_info.get('thumbnail_url', ''),
                country=channel_info.get('country', ''),
                custom_url=channel_info.get('custom_url', ''),
                keywords=channel_info.get('keywords', ''),
                featured_channels_title=channel_info.get('featured_channels_title', ''),
                featured_channels_urls=json.dumps(channel_info.get('featured_channels_urls', [])),
                
                # Performance Metrics
                avg_views_per_video=performance_metrics.get('avg_views_per_video', 0.0),
                avg_likes_per_video=performance_metrics.get('avg_likes_per_video', 0.0),
                avg_comments_per_video=performance_metrics.get('avg_comments_per_video', 0.0),
                avg_duration_per_video=performance_metrics.get('avg_duration_per_video', 0.0),
                overall_engagement_rate=performance_metrics.get('overall_engagement_rate', 0.0),
                videos_per_month=performance_metrics.get('videos_per_month', 0.0),
                views_per_month=performance_metrics.get('views_per_month', 0.0),
                subscribers_per_month=performance_metrics.get('subscribers_per_month', 0.0),
                days_since_created=performance_metrics.get('days_since_created', 0),
                channel_age_months=performance_metrics.get('channel_age_months', 0.0),
                
                # Recent Performance
                recent_videos_count=recent_performance.get('recent_videos_count', 0),
                recent_views=recent_performance.get('recent_views', 0),
                recent_likes=recent_performance.get('recent_likes', 0),
                recent_comments=recent_performance.get('recent_comments', 0),
                recent_engagement_rate=recent_performance.get('recent_engagement_rate', 0.0),
                recent_avg_views=recent_performance.get('recent_avg_views', 0.0),
                
                # JSON fields for complex data
                top_performing_content=json.dumps(overview_data.get('top_performing_content', {})),
                monthly_analytics=json.dumps(overview_data.get('monthly_analytics', {})),
                content_analysis=json.dumps(overview_data.get('content_analysis', {})),
                
                # Channel Status
                is_active=channel_status.get('is_active', True),
                engagement_level=channel_status.get('engagement_level', 'Low'),
                growth_stage=channel_status.get('growth_stage', 'New'),
                content_quality=channel_status.get('content_quality', 'Low'),
                upload_consistency=channel_status.get('upload_consistency', 'Low'),
                
                # Summary Stats
                total_watch_time_hours=summary_stats.get('total_watch_time_hours', 0.0),
                avg_video_length_minutes=summary_stats.get('avg_video_length_minutes', 0.0),
                total_interactions=summary_stats.get('total_interactions', 0),
                interaction_rate=summary_stats.get('interaction_rate', 0.0),
                subscriber_to_view_ratio=summary_stats.get('subscriber_to_view_ratio', 0.0),
                
                # Growth Insights
                subscriber_growth_rate=growth_insights.get('subscriber_growth_rate', 0.0),
                view_growth_rate=growth_insights.get('view_growth_rate', 0.0),
                video_upload_frequency=growth_insights.get('video_upload_frequency', 0.0),
                engagement_growth=growth_insights.get('engagement_growth', 0.0),
                
                # Competitive Analysis
                channel_health_score=competitive_analysis.get('channel_health_score', 0.0),
                growth_potential=competitive_analysis.get('growth_potential', 'Low'),
                audience_loyalty=competitive_analysis.get('audience_loyalty', 'Low'),
                content_consistency=competitive_analysis.get('content_consistency', 'Low'),
                
                # Additional JSON fields for complex data
                advanced_analytics=json.dumps(overview_data.get('advanced_analytics', {})),
                performance_scoring=json.dumps(overview_data.get('performance_scoring', {})),
                weekly_analytics=json.dumps(overview_data.get('weekly_analytics', {})),
                content_insights=json.dumps(overview_data.get('content_insights', {})),
                
                # JSON fields for complex data
                enhanced_channel_info=json.dumps(overview_data.get('enhanced_channel_info', {})),
                monetization_data=json.dumps(overview_data.get('monetization_data', {})),
                audience_insights=json.dumps(overview_data.get('audience_insights', {})),
                seo_metrics=json.dumps(overview_data.get('seo_metrics', {})),
                content_strategy=json.dumps(overview_data.get('content_strategy', {})),
                technical_metrics=json.dumps(overview_data.get('technical_metrics', {})),
                business_metrics=json.dumps(overview_data.get('business_metrics', {})),
                
                data_updated_at=datetime.utcnow()
            )
            
            db.add(overview_record)
            db.commit()
            db.refresh(overview_record)
            
            logger.info(f"Successfully stored overview data for user_id: {user_id}")
            return True
            
        except Exception as e:
            logger.error(f"Error storing overview data for user_id {user_id}: {e}")
            db.rollback()
            return False
    
    @staticmethod
    def get_overview_data(user_id: UUID, db: Session) -> Optional[Dict[str, Any]]:
        """Get dashboard overview data from database"""
        try:
            overview_record = db.query(DashboardOverview).filter(
                DashboardOverview.user_id == user_id
            ).first()
            
            if not overview_record:
                return None
            
            # Convert back to original format
            overview_data = {
                'channel_info': {
                    'title': overview_record.channel_title,
                    'description': overview_record.channel_description,
                    'subscriber_count': overview_record.subscriber_count,
                    'total_views': overview_record.total_views,
                    'total_videos': overview_record.total_videos,
                    'total_likes': overview_record.total_likes,
                    'total_comments': overview_record.total_comments,
                    'total_duration': overview_record.total_duration,
                    'created_at': overview_record.created_at.isoformat(),
                    'thumbnail_url': overview_record.thumbnail_url,
                    'country': overview_record.country,
                    'custom_url': overview_record.custom_url,
                    'keywords': overview_record.keywords,
                    'featured_channels_title': overview_record.featured_channels_title,
                    'featured_channels_urls': json.loads(overview_record.featured_channels_urls)
                },
                'performance_metrics': {
                    'avg_views_per_video': overview_record.avg_views_per_video,
                    'avg_likes_per_video': overview_record.avg_likes_per_video,
                    'avg_comments_per_video': overview_record.avg_comments_per_video,
                    'avg_duration_per_video': overview_record.avg_duration_per_video,
                    'overall_engagement_rate': overview_record.overall_engagement_rate,
                    'videos_per_month': overview_record.videos_per_month,
                    'views_per_month': overview_record.views_per_month,
                    'subscribers_per_month': overview_record.subscribers_per_month,
                    'days_since_created': overview_record.days_since_created,
                    'channel_age_months': overview_record.channel_age_months
                },
                'recent_performance': {
                    'recent_videos_count': overview_record.recent_videos_count,
                    'recent_views': overview_record.recent_views,
                    'recent_likes': overview_record.recent_likes,
                    'recent_comments': overview_record.recent_comments,
                    'recent_engagement_rate': overview_record.recent_engagement_rate,
                    'recent_avg_views': overview_record.recent_avg_views
                },
                'top_performing_content': json.loads(overview_record.top_performing_content),
                'monthly_analytics': json.loads(overview_record.monthly_analytics),
                'content_analysis': json.loads(overview_record.content_analysis),
                'channel_status': {
                    'is_active': overview_record.is_active,
                    'engagement_level': overview_record.engagement_level,
                    'growth_stage': overview_record.growth_stage,
                    'content_quality': overview_record.content_quality,
                    'upload_consistency': overview_record.upload_consistency
                },
                'summary_stats': {
                    'total_watch_time_hours': overview_record.total_watch_time_hours,
                    'avg_video_length_minutes': overview_record.avg_video_length_minutes,
                    'total_interactions': overview_record.total_interactions,
                    'interaction_rate': overview_record.interaction_rate,
                    'subscriber_to_view_ratio': overview_record.subscriber_to_view_ratio
                },
                'growth_insights': {
                    'subscriber_growth_rate': overview_record.subscriber_growth_rate,
                    'view_growth_rate': overview_record.view_growth_rate,
                    'video_upload_frequency': overview_record.video_upload_frequency,
                    'engagement_growth': overview_record.engagement_growth
                },
                'competitive_analysis': {
                    'channel_health_score': overview_record.channel_health_score,
                    'growth_potential': overview_record.growth_potential,
                    'audience_loyalty': overview_record.audience_loyalty,
                    'content_consistency': overview_record.content_consistency
                },
                'advanced_analytics': json.loads(overview_record.advanced_analytics),
                'performance_scoring': json.loads(overview_record.performance_scoring),
                'weekly_analytics': json.loads(overview_record.weekly_analytics),
                'content_insights': json.loads(overview_record.content_insights),
                # JSON fields
                'enhanced_channel_info': json.loads(overview_record.enhanced_channel_info),
                'monetization_data': json.loads(overview_record.monetization_data),
                'audience_insights': json.loads(overview_record.audience_insights),
                'seo_metrics': json.loads(overview_record.seo_metrics),
                'content_strategy': json.loads(overview_record.content_strategy),
                'technical_metrics': json.loads(overview_record.technical_metrics),
                'business_metrics': json.loads(overview_record.business_metrics)
            }
            
            return overview_data
            
        except Exception as e:
            logger.error(f"Error getting overview data for user_id {user_id}: {e}")
            return None
    
    @staticmethod
    def store_playlists_data(user_id: UUID, playlists_data: List[Dict[str, Any]], db: Session) -> bool:
        """Store dashboard playlists data in database"""
        try:
            # Delete existing playlists data for user
            db.query(DashboardPlaylist).filter(DashboardPlaylist.user_id == user_id).delete()
            db.query(DashboardPlaylistVideo).filter(DashboardPlaylistVideo.user_id == user_id).delete()
            
            for playlist_data in playlists_data:
                playlist_info = playlist_data.get('playlist_info', {})
                analytics = playlist_data.get('analytics', {})
                
                # Create playlist record
                playlist_record = DashboardPlaylist(
                    user_id=user_id,
                    playlist_id=playlist_info.get('playlist_id', ''),
                    title=playlist_info.get('title', ''),
                    description=playlist_info.get('description', ''),
                    playlist_url=playlist_info.get('playlist_url', ''),
                    embed_html=playlist_info.get('embed_html', ''),
                    embed_url=playlist_info.get('embed_url', ''),
                    playlist_type=playlist_info.get('playlist_type', ''),
                    is_editable=playlist_info.get('is_editable', True),
                    is_public=playlist_info.get('is_public', True),
                    is_unlisted=playlist_info.get('is_unlisted', False),
                    is_private=playlist_info.get('is_private', False),
                    default_thumbnail=playlist_info.get('default_thumbnail', ''),
                    high_thumbnail=playlist_info.get('high_thumbnail', ''),
                    maxres_thumbnail=playlist_info.get('maxres_thumbnail', ''),
                    standard_thumbnail=playlist_info.get('standard_thumbnail', ''),
                    item_count=playlist_info.get('item_count', 0),
                    video_count=playlist_info.get('video_count', 0),
                    published_at=parse_datetime(playlist_info.get('published_at', datetime.utcnow())),
                    channel_id=playlist_info.get('channel_id', ''),
                    channel_title=playlist_info.get('channel_title', ''),
                    analytics=json.dumps(analytics),
                    data_updated_at=datetime.utcnow()
                )
                
                db.add(playlist_record)
                
                # Store playlist-video relationships
                videos = analytics.get('videos', [])
                for position, video in enumerate(videos):
                    playlist_video_record = DashboardPlaylistVideo(
                        user_id=user_id,
                        playlist_id=playlist_info.get('playlist_id', ''),
                        video_id=video.get('video_id', ''),
                        position=position,
                        data_updated_at=datetime.utcnow()
                    )
                    db.add(playlist_video_record)
            
            db.commit()
            logger.info(f"Successfully stored {len(playlists_data)} playlists for user_id: {user_id}")
            return True
            
        except Exception as e:
            logger.error(f"Error storing playlists data for user_id {user_id}: {e}")
            db.rollback()
            return False
    
    @staticmethod
    def get_playlists_data(user_id: UUID, db: Session) -> List[Dict[str, Any]]:
        """Get dashboard playlists data from database"""
        try:
            playlists_records = db.query(DashboardPlaylist).filter(
                DashboardPlaylist.user_id == user_id
            ).all()
            
            playlists_data = []
            for playlist_record in playlists_records:
                # Get playlist-video relationships
                playlist_videos = db.query(DashboardPlaylistVideo).filter(
                    DashboardPlaylistVideo.user_id == user_id,
                    DashboardPlaylistVideo.playlist_id == playlist_record.playlist_id
                ).order_by(DashboardPlaylistVideo.position).all()
                
                # Get video IDs from relationships
                video_ids = [pv.video_id for pv in playlist_videos]
                
                # Get video details from dashboard_videos table
                videos_data = []
                if video_ids:
                    video_records = db.query(DashboardVideo).filter(
                        DashboardVideo.user_id == user_id,
                        DashboardVideo.video_id.in_(video_ids)
                    ).all()
                    
                    # Create a map for quick lookup
                    video_map = {v.video_id: v for v in video_records}
                    
                    # Build videos list in correct order
                    for pv in playlist_videos:
                        if pv.video_id in video_map:
                            video_record = video_map[pv.video_id]
                            video_data = {
                                'video_id': video_record.video_id,
                                'title': video_record.title,
                                'description': video_record.description,
                                'thumbnail_url': video_record.thumbnail_url,
                                'published_at': video_record.published_at.isoformat(),
                                'duration': video_record.duration,
                                'duration_seconds': video_record.duration_seconds,
                                'channel_id': video_record.channel_id,
                                'channel_title': video_record.channel_title,
                                'view_count': video_record.view_count,
                                'like_count': video_record.like_count,
                                'comment_count': video_record.comment_count,
                                'privacy_status': video_record.privacy_status,
                                'upload_status': video_record.upload_status,
                                'license': video_record.license,
                                'made_for_kids': video_record.made_for_kids,
                                'category_id': video_record.category_id,
                                'tags': json.loads(video_record.tags),
                                'default_language': video_record.default_language,
                                'default_audio_language': video_record.default_audio_language,
                                'analytics': json.loads(video_record.analytics)
                            }
                            videos_data.append(video_data)
                
                # Get analytics from playlist record
                analytics = json.loads(playlist_record.analytics)
                # Update videos in analytics with the actual video data
                analytics['videos'] = videos_data
                
                playlist_data = {
                    'playlist_info': {
                        'playlist_id': playlist_record.playlist_id,
                        'title': playlist_record.title,
                        'description': playlist_record.description,
                        'playlist_url': playlist_record.playlist_url,
                        'embed_html': playlist_record.embed_html,
                        'embed_url': playlist_record.embed_url,
                        'playlist_type': playlist_record.playlist_type,
                        'is_editable': playlist_record.is_editable,
                        'is_public': playlist_record.is_public,
                        'is_unlisted': playlist_record.is_unlisted,
                        'is_private': playlist_record.is_private,
                        'default_thumbnail': playlist_record.default_thumbnail,
                        'high_thumbnail': playlist_record.high_thumbnail,
                        'maxres_thumbnail': playlist_record.maxres_thumbnail,
                        'standard_thumbnail': playlist_record.standard_thumbnail,
                        'item_count': playlist_record.item_count,
                        'video_count': playlist_record.video_count,
                        'published_at': playlist_record.published_at.isoformat(),
                        'channel_id': playlist_record.channel_id,
                        'channel_title': playlist_record.channel_title
                    },
                    'analytics': analytics
                }
                playlists_data.append(playlist_data)
            
            return playlists_data
            
        except Exception as e:
            logger.error(f"Error getting playlists data for user_id {user_id}: {e}")
            return []
    
    @staticmethod
    def get_playlist_videos(user_id: UUID, playlist_id: str, db: Session) -> List[Dict[str, Any]]:
        """Get videos for a specific playlist using relationship table"""
        try:
            # Get playlist-video relationships for the specific playlist
            playlist_videos = db.query(DashboardPlaylistVideo).filter(
                DashboardPlaylistVideo.user_id == user_id,
                DashboardPlaylistVideo.playlist_id == playlist_id
            ).order_by(DashboardPlaylistVideo.position).all()
            
            if not playlist_videos:
                return []
            
            # Get video IDs
            video_ids = [pv.video_id for pv in playlist_videos]
            
            # Get video details from dashboard_videos table
            video_records = db.query(DashboardVideo).filter(
                DashboardVideo.user_id == user_id,
                DashboardVideo.video_id.in_(video_ids)
            ).all()
            
            # Create a map for quick lookup
            video_map = {v.video_id: v for v in video_records}
            
            # Build videos list in correct order
            videos_data = []
            for pv in playlist_videos:
                if pv.video_id in video_map:
                    video_record = video_map[pv.video_id]
                    video_data = {
                        'video_id': video_record.video_id,
                        'title': video_record.title,
                        'description': video_record.description,
                        'thumbnail_url': video_record.thumbnail_url,
                        'published_at': video_record.published_at.isoformat(),
                        'duration': video_record.duration,
                        'duration_seconds': video_record.duration_seconds,
                        'channel_id': video_record.channel_id,
                        'channel_title': video_record.channel_title,
                        'view_count': video_record.view_count,
                        'like_count': video_record.like_count,
                        'comment_count': video_record.comment_count,
                        'privacy_status': video_record.privacy_status,
                        'upload_status': video_record.upload_status,
                        'license': video_record.license,
                        'made_for_kids': video_record.made_for_kids,
                        'category_id': video_record.category_id,
                        'tags': json.loads(video_record.tags),
                        'default_language': video_record.default_language,
                        'default_audio_language': video_record.default_audio_language,
                        'analytics': json.loads(video_record.analytics)
                    }
                    videos_data.append(video_data)
            
            return videos_data
            
        except Exception as e:
            logger.error(f"Error getting playlist videos for user_id {user_id}, playlist_id {playlist_id}: {e}")
            return []
    
    @staticmethod
    def store_videos_data(user_id: UUID, videos_data: List[Dict[str, Any]], db: Session) -> bool:
        """Store dashboard videos data in database"""
        try:
            # Delete existing videos data for user
            db.query(DashboardVideo).filter(DashboardVideo.user_id == user_id).delete()
            
            for video_data in videos_data:
                # Create video record
                video_record = DashboardVideo(
                    user_id=user_id,
                    video_id=video_data.get('video_id', ''),
                    title=video_data.get('title', ''),
                    description=video_data.get('description', ''),
                    thumbnail_url=video_data.get('thumbnail_url', ''),
                    published_at=parse_datetime(video_data.get('published_at', datetime.utcnow())),
                    duration=video_data.get('duration', ''),
                    duration_seconds=video_data.get('duration_seconds', 0),
                    channel_id=video_data.get('channel_id', ''),
                    channel_title=video_data.get('channel_title', ''),
                    view_count=video_data.get('view_count', 0),
                    like_count=video_data.get('like_count', 0),
                    comment_count=video_data.get('comment_count', 0),
                    privacy_status=video_data.get('privacy_status', 'public'),
                    upload_status=video_data.get('upload_status', 'processed'),
                    license=video_data.get('license', 'youtube'),
                    made_for_kids=video_data.get('made_for_kids', False),
                    category_id=video_data.get('category_id', ''),
                    tags=json.dumps(video_data.get('tags', [])),
                    default_language=video_data.get('default_language', ''),
                    default_audio_language=video_data.get('default_audio_language', ''),
                    analytics=json.dumps(video_data.get('analytics', {})),
                    data_updated_at=datetime.utcnow()
                )
                
                db.add(video_record)
            
            db.commit()
            logger.info(f"Successfully stored {len(videos_data)} videos for user_id: {user_id}")
            return True
            
        except Exception as e:
            logger.error(f"Error storing videos data for user_id {user_id}: {e}")
            db.rollback()
            return False
    
    @staticmethod
    def get_videos_data(user_id: UUID, db: Session) -> List[Dict[str, Any]]:
        """Get dashboard videos data from database"""
        try:
            videos_records = db.query(DashboardVideo).filter(
                DashboardVideo.user_id == user_id
            ).all()
            
            videos_data = []
            for video_record in videos_records:
                video_data = {
                    'video_id': video_record.video_id,
                    'title': video_record.title,
                    'description': video_record.description,
                    'thumbnail_url': video_record.thumbnail_url,
                    'published_at': video_record.published_at.isoformat(),
                    'duration': video_record.duration,
                    'duration_seconds': video_record.duration_seconds,
                    'channel_id': video_record.channel_id,
                    'channel_title': video_record.channel_title,
                    'view_count': video_record.view_count,
                    'like_count': video_record.like_count,
                    'comment_count': video_record.comment_count,
                    'privacy_status': video_record.privacy_status,
                    'upload_status': video_record.upload_status,
                    'license': video_record.license,
                    'made_for_kids': video_record.made_for_kids,
                    'category_id': video_record.category_id,
                    'tags': json.loads(video_record.tags),
                    'default_language': video_record.default_language,
                    'default_audio_language': video_record.default_audio_language,
                    'analytics': json.loads(video_record.analytics)
                }
                videos_data.append(video_data)
            
            return videos_data
            
        except Exception as e:
            logger.error(f"Error getting videos data for user_id {user_id}: {e}")
            return []

    @staticmethod
    def store_playlist_video_relationship(user_id: UUID, playlist_id: str, video_id: str, position: int, db: Session) -> bool:
        """Store playlist-video relationship in database"""
        try:
            # Check if relationship already exists
            existing_relationship = db.query(DashboardPlaylistVideo).filter(
                DashboardPlaylistVideo.user_id == user_id,
                DashboardPlaylistVideo.playlist_id == playlist_id,
                DashboardPlaylistVideo.video_id == video_id
            ).first()
            
            if existing_relationship:
                # Update position
                existing_relationship.position = position
            else:
                # Create new relationship
                relationship = DashboardPlaylistVideo(
                    user_id=user_id,
                    playlist_id=playlist_id,
                    video_id=video_id,
                    position=position
                )
                db.add(relationship)
            
            db.commit()
            return True
            
        except Exception as e:
            logger.error(f"Error storing playlist-video relationship for user_id {user_id}, playlist_id {playlist_id}, video_id {video_id}: {e}")
            db.rollback()
            return False

    @staticmethod
    def store_playlist_videos_data(user_id: UUID, playlist_id: str, videos_data: List[Dict[str, Any]], db: Session) -> bool:
        """Store playlist videos data in database"""
        try:
            # First, store the videos in the DashboardVideo table
            success = DashboardDataService.store_videos_data(user_id, videos_data, db)
            if not success:
                return False
            
            # Clear existing playlist-video relationships for this playlist
            db.query(DashboardPlaylistVideo).filter(
                DashboardPlaylistVideo.user_id == user_id,
                DashboardPlaylistVideo.playlist_id == playlist_id
            ).delete()
            
            # Create playlist-video relationships
            for position, video_data in enumerate(videos_data, 1):
                video_id = video_data.get('video_id', '')
                if video_id:
                    relationship = DashboardPlaylistVideo(
                        user_id=user_id,
                        playlist_id=playlist_id,
                        video_id=video_id,
                        position=position
                    )
                    db.add(relationship)
            
            db.commit()
            logger.info(f"Successfully stored {len(videos_data)} playlist videos for user_id: {user_id}, playlist_id: {playlist_id}")
            return True
            
        except Exception as e:
            logger.error(f"Error storing playlist videos data for user_id {user_id}, playlist_id {playlist_id}: {e}")
            db.rollback()
            return False


def parse_datetime(datetime_value):
    """Parse datetime value from various formats to datetime object"""
    if isinstance(datetime_value, datetime):
        return datetime_value
    
    if isinstance(datetime_value, str):
        # Remove timezone info and parse
        datetime_str = re.sub(r'[+-]\d{2}:\d{2}$', '', datetime_value)
        datetime_str = datetime_str.replace('Z', '')
        
        try:
            # Try parsing with microseconds
            return datetime.fromisoformat(datetime_str)
        except ValueError:
            try:
                # Try parsing without microseconds
                return datetime.strptime(datetime_str, '%Y-%m-%dT%H:%M:%S')
            except ValueError:
                try:
                    # Try parsing just date
                    return datetime.strptime(datetime_str, '%Y-%m-%d')
                except ValueError:
                    logger.error(f"Could not parse datetime: {datetime_value}")
                    return datetime.utcnow()
    
    return datetime.utcnow()
