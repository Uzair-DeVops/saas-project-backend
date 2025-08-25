from typing import List, Dict, Any
from uuid import UUID
from fastapi import APIRouter, HTTPException, Depends, Path
from sqlmodel import Session
from pydantic import BaseModel

from ..controllers.dashboard_controller import (
    get_playlists_controller,
    get_playlist_videos_controller,
    get_playlist_analytics_controller,
    get_all_user_videos_controller,
    get_video_details_controller,
    get_all_playlists_comprehensive_controller,
    get_comprehensive_playlist_controller
)
from ..utils.database_dependency import get_database_session
from ..controllers.user_controller import get_current_user
from ..models.user_model import UserSignUp
from ..utils.my_logger import get_logger

logger = get_logger("DASHBOARD_ROUTES")

router = APIRouter(prefix="/dashboard", tags=["dashboard"])

# Response models
class DashboardResponse(BaseModel):
    """Response model for dashboard operations"""
    success: bool
    message: str
    data: Dict[str, Any]

class PlaylistsResponse(BaseModel):
    """Response model for playlists"""
    success: bool
    message: str
    data: List[Dict[str, Any]]
    count: int

class VideosResponse(BaseModel):
    """Response model for videos"""
    success: bool
    message: str
    data: List[Dict[str, Any]]
    count: int

class VideoDetailResponse(BaseModel):
    """Response model for individual video details"""
    success: bool
    message: str
    data: Dict[str, Any]

class AnalyticsResponse(BaseModel):
    """Response model for analytics"""
    success: bool
    message: str
    data: Dict[str, Any]



@router.get("/playlists", response_model=PlaylistsResponse)
async def get_dashboard_playlists(
    current_user: UserSignUp = Depends(get_current_user),
    db: Session = Depends(get_database_session)
) -> PlaylistsResponse:
    """
    Get all playlists with comprehensive analytics for dashboard.
    
    This endpoint provides detailed information about all playlists including:
    - Playlist metadata (title, description, thumbnail, etc.)
    - Comprehensive performance metrics
    - Content analysis and growth insights
    - Top performing videos in each playlist
    - Playlist health and recommendations
    
    Args:
        current_user: The authenticated user from JWT token
        db: Database session dependency
    
    Returns:
        PlaylistsResponse: List of playlists with comprehensive analytics
        
    Raises:
        HTTPException: If error occurs
    """
    try:
        logger.info(f"Dashboard playlists request received for user_id: {current_user.id}")
        
        # Get comprehensive playlist data
        playlists = get_all_playlists_comprehensive_controller(current_user.id, db)
        
        return PlaylistsResponse(
            success=True,
            message=f"Successfully retrieved {len(playlists)} playlists with comprehensive analytics",
            data=playlists,
            count=len(playlists)
        )
        
    except HTTPException:
        # Re-raise HTTP exceptions as they are already properly formatted
        raise
    except Exception as e:
        logger.error(f"Unexpected error in get_dashboard_playlists route for user_id {current_user.id}: {e}")
        raise HTTPException(
            status_code=500,
            detail="Internal server error while retrieving playlists"
        )

@router.get("/playlists/{playlist_id}/comprehensive", response_model=AnalyticsResponse)
async def get_dashboard_playlist_comprehensive(
    playlist_id: str = Path(..., description="The YouTube playlist ID"),
    current_user: UserSignUp = Depends(get_current_user),
    db: Session = Depends(get_database_session)
) -> AnalyticsResponse:
    """
    Get comprehensive analytics for a specific playlist.
    
    This endpoint provides extremely detailed analytics for a single playlist including:
    - Complete playlist information and metadata
    - All videos with detailed analytics
    - Performance metrics and distributions
    - Content analysis and growth insights
    - Top performing videos by multiple criteria
    - Playlist health assessment
    - Recent activity analysis
    - Duration and engagement distributions
    - Content recommendations
    
    Args:
        playlist_id: The YouTube playlist ID
        current_user: The authenticated user from JWT token
        db: Database session dependency
    
    Returns:
        AnalyticsResponse: Comprehensive playlist analytics data
        
    Raises:
        HTTPException: If error occurs
    """
    try:
        logger.info(f"Dashboard playlist comprehensive request received for playlist_id: {playlist_id}, user_id: {current_user.id}")
        
        # Get comprehensive playlist analytics
        playlist_data = get_comprehensive_playlist_controller(current_user.id, playlist_id, db)
        
        if not playlist_data:
            raise HTTPException(
                status_code=404,
                detail="Playlist not found or you don't have permission to access it"
            )
        
        return AnalyticsResponse(
            success=True,
            message=f"Successfully generated comprehensive analytics for playlist: {playlist_data.get('playlist_info', {}).get('title', 'Unknown')}",
            data=playlist_data
        )
        
    except HTTPException:
        # Re-raise HTTP exceptions as they are already properly formatted
        raise
    except Exception as e:
        logger.error(f"Unexpected error in get_dashboard_playlist_comprehensive route for playlist_id {playlist_id}, user_id {current_user.id}: {e}")
        raise HTTPException(
            status_code=500,
            detail="Internal server error while generating comprehensive playlist analytics"
        )

@router.get("/videos", response_model=VideosResponse)
async def get_dashboard_videos(
    current_user: UserSignUp = Depends(get_current_user),
    db: Session = Depends(get_database_session)
) -> VideosResponse:
    """
    Get all videos for dashboard with detailed analytics.
    
    This endpoint provides comprehensive information about all user's videos
    including views, likes, comments, engagement rates, and performance scores.
    
    Args:
        current_user: The authenticated user from JWT token
        db: Database session dependency
    
    Returns:
        VideosResponse: List of all videos with detailed analytics
        
    Raises:
        HTTPException: If error occurs
    """
    try:
        logger.info(f"Dashboard videos request received for user_id: {current_user.id}")
        
        # Get all videos with analytics
        videos = get_all_user_videos_controller(current_user.id, db)
        
        return VideosResponse(
            success=True,
            message=f"Successfully retrieved {len(videos)} videos",
            data=videos,
            count=len(videos)
        )
        
    except HTTPException:
        # Re-raise HTTP exceptions as they are already properly formatted
        raise
    except Exception as e:
        logger.error(f"Unexpected error in get_dashboard_videos route for user_id {current_user.id}: {e}")
        raise HTTPException(
            status_code=500,
            detail="Internal server error while retrieving videos"
        )

@router.get("/videos/{video_id}", response_model=VideoDetailResponse)
async def get_dashboard_video_details(
    video_id: str = Path(..., description="The YouTube video ID"),
    current_user: UserSignUp = Depends(get_current_user),
    db: Session = Depends(get_database_session)
) -> VideoDetailResponse:
    """
    Get comprehensive detailed analytics for a specific video.
    
    This endpoint provides extremely detailed information about a single video including:
    - Complete video metadata (title, description, thumbnail, tags, category)
    - Core performance metrics (views, likes, comments, duration)
    - Advanced analytics (engagement rates, performance scores, watch time)
    - Performance analysis (performance level, engagement level, content type)
    - Content analysis (category, language, content type classification)
    - Growth metrics and potential assessment
    - Analytics summary with engagement breakdown
    - Performance indicators (high performing, viral potential, high engagement)
    - Personalized recommendations for improvement
    - Days since published and views per day metrics
    
    Args:
        video_id: The YouTube video ID
        current_user: The authenticated user from JWT token
        db: Database session dependency
    
    Returns:
        VideoDetailResponse: Comprehensive video analytics with recommendations
        
    Raises:
        HTTPException: If error occurs
    """
    try:
        logger.info(f"Dashboard video details request received for video_id: {video_id}, user_id: {current_user.id}")
        
        # Get detailed video analytics
        video_details = get_video_details_controller(current_user.id, video_id, db)
        
        if not video_details:
            raise HTTPException(
                status_code=404,
                detail="Video not found or you don't have permission to access it"
            )
        
        return VideoDetailResponse(
            success=True,
            message=f"Successfully retrieved details for video: {video_details.get('title', 'Unknown')}",
            data=video_details
        )
        
    except HTTPException:
        # Re-raise HTTP exceptions as they are already properly formatted
        raise
    except Exception as e:
        logger.error(f"Unexpected error in get_dashboard_video_details route for video_id {video_id}, user_id {current_user.id}: {e}")
        raise HTTPException(
            status_code=500,
            detail="Internal server error while retrieving video details"
        )

@router.get("/playlists/{playlist_id}/videos", response_model=VideosResponse)
async def get_dashboard_playlist_videos(
    playlist_id: str = Path(..., description="The YouTube playlist ID"),
    current_user: UserSignUp = Depends(get_current_user),
    db: Session = Depends(get_database_session)
) -> VideosResponse:
    """
    Get all videos in a playlist with detailed analytics for dashboard.
    
    This endpoint provides comprehensive information about each video in a playlist
    including views, likes, comments, engagement rates, and performance scores.
    
    Args:
        playlist_id: The YouTube playlist ID
        current_user: The authenticated user from JWT token
        db: Database session dependency
    
    Returns:
        VideosResponse: List of videos with detailed analytics
        
    Raises:
        HTTPException: If error occurs
    """
    try:
        logger.info(f"Dashboard playlist videos request received for playlist_id: {playlist_id}, user_id: {current_user.id}")
        
        # Get videos with analytics
        videos = get_playlist_videos_controller(current_user.id, playlist_id, db)
        
        return VideosResponse(
            success=True,
            message=f"Successfully retrieved {len(videos)} videos from playlist",
            data=videos,
            count=len(videos)
        )
        
    except HTTPException:
        # Re-raise HTTP exceptions as they are already properly formatted
        raise
    except Exception as e:
        logger.error(f"Unexpected error in get_dashboard_playlist_videos route for playlist_id {playlist_id}, user_id {current_user.id}: {e}")
        raise HTTPException(
            status_code=500,
            detail="Internal server error while retrieving playlist videos"
        )

@router.get("/playlists/{playlist_id}/analytics", response_model=AnalyticsResponse)
async def get_dashboard_playlist_analytics(
    playlist_id: str = Path(..., description="The YouTube playlist ID"),
    current_user: UserSignUp = Depends(get_current_user),
    db: Session = Depends(get_database_session)
) -> AnalyticsResponse:
    """
    Get comprehensive analytics for all videos in a playlist.
    
    This endpoint provides detailed analytics including:
    - Total views, likes, comments across all videos
    - Average engagement rates
    - Top performing videos
    - Performance summaries
    - Best and worst performing videos
    
    Args:
        playlist_id: The YouTube playlist ID
        current_user: The authenticated user from JWT token
        db: Database session dependency
    
    Returns:
        AnalyticsResponse: Comprehensive analytics data
        
    Raises:
        HTTPException: If error occurs
    """
    try:
        logger.info(f"Dashboard playlist analytics request received for playlist_id: {playlist_id}, user_id: {current_user.id}")
        
        # Get comprehensive analytics
        analytics = get_playlist_analytics_controller(current_user.id, playlist_id, db)
        
        return AnalyticsResponse(
            success=True,
            message=f"Successfully generated analytics for playlist with {analytics.get('total_videos', 0)} videos",
            data=analytics
        )
        
    except HTTPException:
        # Re-raise HTTP exceptions as they are already properly formatted
        raise
    except Exception as e:
        logger.error(f"Unexpected error in get_dashboard_playlist_analytics route for playlist_id {playlist_id}, user_id {current_user.id}: {e}")
        raise HTTPException(
            status_code=500,
            detail="Internal server error while generating analytics"
        )

@router.get("/overview", response_model=DashboardResponse)
async def get_dashboard_overview(
    current_user: UserSignUp = Depends(get_current_user),
    db: Session = Depends(get_database_session)
) -> DashboardResponse:
    """
    Get dashboard overview with summary statistics.
    
    This endpoint provides a high-level overview of the user's YouTube channel
    including total playlists, total videos, overall performance metrics, etc.
    
    Args:
        current_user: The authenticated user from JWT token
        db: Database session dependency
    
    Returns:
        DashboardResponse: Dashboard overview data
        
    Raises:
        HTTPException: If error occurs
    """
    try:
        logger.info(f"Dashboard overview request received for user_id: {current_user.id}")
        
        # Get YouTube client
        from ..services.youtube_auth_service import get_youtube_client
        youtube = get_youtube_client(current_user.id, db)
        if not youtube:
            raise HTTPException(
                status_code=500,
                detail="Failed to get YouTube client. Please check your YouTube API credentials."
            )
        
        # Get channel information
        from ..services.dashboard_service import get_channel_info
        channel_info = get_channel_info(youtube)
        
        if not channel_info:
            raise HTTPException(
                status_code=500,
                detail="Failed to get channel information. Please check your YouTube API credentials."
            )
        
        # Get channel statistics
        subscriber_count = channel_info.get('subscriber_count', 0)
        total_channel_views = channel_info.get('view_count', 0)
        total_channel_videos = channel_info.get('video_count', 0)
        
        # Get all videos for detailed analytics
        from ..services.dashboard_service import get_user_videos
        all_videos = get_user_videos(youtube)
        
        # Calculate video statistics
        total_likes = sum(int(video.get('like_count', 0)) for video in all_videos)
        total_comments = sum(int(video.get('comment_count', 0)) for video in all_videos)
        total_duration = sum(int(video.get('duration_seconds', 0)) for video in all_videos)
        
        # Calculate additional metrics
        from datetime import datetime, timedelta
        try:
            channel_created_date = datetime.fromisoformat(channel_info.get('published_at', '').replace('Z', '+00:00'))
            current_date = datetime.now(channel_created_date.tzinfo)
            days_since_created = (current_date - channel_created_date).days
        except Exception as e:
            logger.error(f"Error calculating channel age: {e}")
            days_since_created = 0
        
        # Calculate averages
        avg_views_per_video = total_channel_views / total_channel_videos if total_channel_videos > 0 else 0
        avg_likes_per_video = total_likes / total_channel_videos if total_channel_videos > 0 else 0
        avg_comments_per_video = total_comments / total_channel_videos if total_channel_videos > 0 else 0
        avg_duration_per_video = total_duration / total_channel_videos if total_channel_videos > 0 else 0
        
        # Calculate engagement metrics
        total_engagement = total_likes + total_comments
        overall_engagement_rate = (total_engagement / total_channel_views * 100) if total_channel_views > 0 else 0
        
        # Calculate growth rates
        videos_per_month = (total_channel_videos / days_since_created * 30) if days_since_created > 0 else 0
        views_per_month = (total_channel_views / days_since_created * 30) if days_since_created > 0 else 0
        subscribers_per_month = (subscriber_count / days_since_created * 30) if days_since_created > 0 else 0
        
        # Get recent videos (last 30 days)
        thirty_days_ago = current_date - timedelta(days=30)
        recent_videos = [
            video for video in all_videos 
            if video.get('published_at') and datetime.fromisoformat(video['published_at'].replace('Z', '+00:00')) > thirty_days_ago
        ]
        
        # Calculate recent performance
        recent_views = sum(int(video.get('view_count', 0)) for video in recent_videos)
        recent_likes = sum(int(video.get('like_count', 0)) for video in recent_videos)
        recent_comments = sum(int(video.get('comment_count', 0)) for video in recent_videos)
        recent_engagement_rate = ((recent_likes + recent_comments) / recent_views * 100) if recent_views > 0 else 0
        
        # Get top performing videos
        top_videos_by_views = sorted(all_videos, key=lambda x: int(x.get('view_count', 0)), reverse=True)[:10]
        top_videos_by_engagement = sorted(all_videos, key=lambda x: (int(x.get('like_count', 0)) + int(x.get('comment_count', 0))) / int(x.get('view_count', 1)), reverse=True)[:10]
        
        # Calculate monthly breakdown for charts
        monthly_data = {}
        for video in all_videos:
            if video.get('published_at'):
                try:
                    publish_date = datetime.fromisoformat(video['published_at'].replace('Z', '+00:00'))
                    month_key = publish_date.strftime('%Y-%m')
                    
                    if month_key not in monthly_data:
                        monthly_data[month_key] = {
                            'videos': 0,
                            'views': 0,
                            'likes': 0,
                            'comments': 0,
                            'duration': 0
                        }
                    
                    monthly_data[month_key]['videos'] += 1
                    monthly_data[month_key]['views'] += int(video.get('view_count', 0))
                    monthly_data[month_key]['likes'] += int(video.get('like_count', 0))
                    monthly_data[month_key]['comments'] += int(video.get('comment_count', 0))
                    monthly_data[month_key]['duration'] += int(video.get('duration_seconds', 0))
                    
                except Exception as e:
                    logger.error(f"Error processing video date: {e}")
        
        # Sort monthly data by date
        sorted_months = sorted(monthly_data.keys())
        monthly_chart_data = [
            {
                'month': month,
                'videos': monthly_data[month]['videos'],
                'views': monthly_data[month]['views'],
                'likes': monthly_data[month]['likes'],
                'comments': monthly_data[month]['comments'],
                'duration': monthly_data[month]['duration'],
                'engagement_rate': round((monthly_data[month]['likes'] + monthly_data[month]['comments']) / monthly_data[month]['views'] * 100, 2) if monthly_data[month]['views'] > 0 else 0
            }
            for month in sorted_months
        ]
        
        # Calculate video categories/tags analysis
        video_categories = {}
        for video in all_videos:
            tags = video.get('tags', [])
            for tag in tags:
                if tag in video_categories:
                    video_categories[tag] += 1
                else:
                    video_categories[tag] = 1
        
        top_categories = sorted(video_categories.items(), key=lambda x: x[1], reverse=True)[:10]
        
        # Calculate performance distribution
        view_ranges = {
            '0-100': 0,
            '101-500': 0,
            '501-1000': 0,
            '1001-5000': 0,
            '5000+': 0
        }
        
        for video in all_videos:
            views = int(video.get('view_count', 0))
            if views <= 100:
                view_ranges['0-100'] += 1
            elif views <= 500:
                view_ranges['101-500'] += 1
            elif views <= 1000:
                view_ranges['501-1000'] += 1
            elif views <= 5000:
                view_ranges['1001-5000'] += 1
            else:
                view_ranges['5000+'] += 1
        
        # Calculate advanced analytics
        # Video length distribution
        duration_ranges = {
            '0-5min': 0,
            '5-15min': 0,
            '15-30min': 0,
            '30-60min': 0,
            '60min+': 0
        }
        
        for video in all_videos:
            duration_seconds = int(video.get('duration_seconds', 0))
            if duration_seconds <= 300:  # 5 minutes
                duration_ranges['0-5min'] += 1
            elif duration_seconds <= 900:  # 15 minutes
                duration_ranges['5-15min'] += 1
            elif duration_seconds <= 1800:  # 30 minutes
                duration_ranges['15-30min'] += 1
            elif duration_seconds <= 3600:  # 60 minutes
                duration_ranges['30-60min'] += 1
            else:
                duration_ranges['60min+'] += 1
        
        # Engagement distribution
        engagement_ranges = {
            '0-1%': 0,
            '1-3%': 0,
            '3-5%': 0,
            '5-10%': 0,
            '10%+': 0
        }
        
        for video in all_videos:
            views = int(video.get('view_count', 0))
            likes = int(video.get('like_count', 0))
            comments = int(video.get('comment_count', 0))
            
            if views > 0:
                engagement_rate = ((likes + comments) / views) * 100
                if engagement_rate <= 1:
                    engagement_ranges['0-1%'] += 1
                elif engagement_rate <= 3:
                    engagement_ranges['1-3%'] += 1
                elif engagement_rate <= 5:
                    engagement_ranges['3-5%'] += 1
                elif engagement_rate <= 10:
                    engagement_ranges['5-10%'] += 1
                else:
                    engagement_ranges['10%+'] += 1
        
        # Performance scoring
        performance_scores = []
        for video in all_videos:
            views = int(video.get('view_count', 0))
            likes = int(video.get('like_count', 0))
            comments = int(video.get('comment_count', 0))
            duration_seconds = int(video.get('duration_seconds', 0))
            
            # Calculate performance score (views * 0.5 + likes * 10 + comments * 20)
            score = (views * 0.5) + (likes * 10) + (comments * 20)
            performance_scores.append({
                'video_id': video.get('video_id', ''),
                'title': video.get('title', ''),
                'score': round(score, 2),
                'views': views,
                'likes': likes,
                'comments': comments,
                'duration_minutes': round(duration_seconds / 60, 2)
            })
        
        # Sort by performance score
        top_performing_by_score = sorted(performance_scores, key=lambda x: x['score'], reverse=True)[:10]
        
        # Weekly performance analysis (last 4 weeks)
        weekly_data = {}
        for i in range(4):
            week_start = current_date - timedelta(weeks=i+1)
            week_end = current_date - timedelta(weeks=i)
            week_key = f"Week {4-i}"
            
            week_videos = [
                video for video in all_videos 
                if video.get('published_at') and 
                week_start <= datetime.fromisoformat(video['published_at'].replace('Z', '+00:00')) < week_end
            ]
            
            week_views = sum(int(video.get('view_count', 0)) for video in week_videos)
            week_likes = sum(int(video.get('like_count', 0)) for video in week_videos)
            week_comments = sum(int(video.get('comment_count', 0)) for video in week_videos)
            week_engagement = ((week_likes + week_comments) / week_views * 100) if week_views > 0 else 0
            
            weekly_data[week_key] = {
                'videos': len(week_videos),
                'views': week_views,
                'likes': week_likes,
                'comments': week_comments,
                'engagement_rate': round(week_engagement, 2)
            }
        
        # Content type analysis
        content_types = {
            'shorts': 0,
            'tutorials': 0,
            'lectures': 0,
            'other': 0
        }
        
        for video in all_videos:
            title = video.get('title', '').lower()
            duration_seconds = int(video.get('duration_seconds', 0))
            
            if 'shorts' in title or duration_seconds <= 60:
                content_types['shorts'] += 1
            elif 'lecture' in title or 'tutorial' in title:
                if duration_seconds > 600:  # 10+ minutes
                    content_types['lectures'] += 1
                else:
                    content_types['tutorials'] += 1
            else:
                content_types['other'] += 1
        
        # Audience retention analysis
        retention_analysis = {
            'high_retention_videos': 0,  # >5% engagement
            'medium_retention_videos': 0,  # 2-5% engagement
            'low_retention_videos': 0,  # <2% engagement
            'avg_retention_rate': 0
        }
        
        total_retention_rate = 0
        videos_with_views = 0
        
        for video in all_videos:
            views = int(video.get('view_count', 0))
            likes = int(video.get('like_count', 0))
            comments = int(video.get('comment_count', 0))
            
            if views > 0:
                retention_rate = ((likes + comments) / views) * 100
                total_retention_rate += retention_rate
                videos_with_views += 1
                
                if retention_rate > 5:
                    retention_analysis['high_retention_videos'] += 1
                elif retention_rate > 2:
                    retention_analysis['medium_retention_videos'] += 1
                else:
                    retention_analysis['low_retention_videos'] += 1
        
        retention_analysis['avg_retention_rate'] = round(total_retention_rate / videos_with_views, 2) if videos_with_views > 0 else 0
        
        # Growth trajectory analysis
        growth_trajectory = {
            'trending_up': 0,
            'stable': 0,
            'trending_down': 0,
            'new_content': 0
        }
        
        # Compare recent vs older performance
        if len(all_videos) >= 10:
            recent_videos = all_videos[:10]  # Most recent 10
            older_videos = all_videos[-10:]  # Oldest 10
            
            recent_avg_views = sum(int(v.get('view_count', 0)) for v in recent_videos) / len(recent_videos)
            older_avg_views = sum(int(v.get('view_count', 0)) for v in older_videos) / len(older_videos)
            
            if recent_avg_views > older_avg_views * 1.2:
                growth_trajectory['trending_up'] = 1
            elif recent_avg_views < older_avg_views * 0.8:
                growth_trajectory['trending_down'] = 1
            else:
                growth_trajectory['stable'] = 1
        else:
            growth_trajectory['new_content'] = 1
        
        overview_data = {
            'channel_info': {
                'title': channel_info.get('title', ''),
                'description': channel_info.get('description', ''),
                'subscriber_count': subscriber_count,
                'total_views': total_channel_views,
                'total_videos': total_channel_videos,
            'total_likes': total_likes,
            'total_comments': total_comments,
                'total_duration': total_duration,
                'created_at': channel_info.get('published_at', ''),
                'thumbnail_url': channel_info.get('thumbnail_url', ''),
                'country': channel_info.get('country', ''),
                'custom_url': channel_info.get('custom_url', ''),
                'keywords': channel_info.get('keywords', ''),
                'featured_channels_title': channel_info.get('featured_channels_title', ''),
                'featured_channels_urls': channel_info.get('featured_channels_urls', [])
            },
            'performance_metrics': {
                'avg_views_per_video': round(avg_views_per_video, 2),
                'avg_likes_per_video': round(avg_likes_per_video, 2),
                'avg_comments_per_video': round(avg_comments_per_video, 2),
                'avg_duration_per_video': round(avg_duration_per_video, 2),
                'overall_engagement_rate': round(overall_engagement_rate, 2),
                'videos_per_month': round(videos_per_month, 2),
                'views_per_month': round(views_per_month, 2),
                'subscribers_per_month': round(subscribers_per_month, 2),
                'days_since_created': days_since_created,
                'channel_age_months': round(days_since_created / 30, 1)
            },
            'recent_performance': {
                'recent_videos_count': len(recent_videos),
                'recent_views': recent_views,
                'recent_likes': recent_likes,
                'recent_comments': recent_comments,
                'recent_engagement_rate': round(recent_engagement_rate, 2),
                'recent_avg_views': round(recent_views / len(recent_videos), 2) if recent_videos else 0
            },
            'top_performing_content': {
                'top_videos_by_views': [
                    {
                        'video_id': video.get('video_id', ''),
                        'title': video.get('title', ''),
                        'views': int(video.get('view_count', 0)),
                        'likes': int(video.get('like_count', 0)),
                        'comments': int(video.get('comment_count', 0)),
                        'published_at': video.get('published_at', ''),
                        'duration': video.get('duration', ''),
                        'engagement_rate': round((int(video.get('like_count', 0)) + int(video.get('comment_count', 0))) / int(video.get('view_count', 1)) * 100, 2)
                    }
                    for video in top_videos_by_views
                ],
                'top_videos_by_engagement': [
                    {
                        'video_id': video.get('video_id', ''),
                        'title': video.get('title', ''),
                        'views': int(video.get('view_count', 0)),
                        'likes': int(video.get('like_count', 0)),
                        'comments': int(video.get('comment_count', 0)),
                        'published_at': video.get('published_at', ''),
                        'duration': video.get('duration', ''),
                        'engagement_rate': round((int(video.get('like_count', 0)) + int(video.get('comment_count', 0))) / int(video.get('view_count', 1)) * 100, 2)
                    }
                    for video in top_videos_by_engagement
                ]
            },
            'monthly_analytics': {
                'chart_data': monthly_chart_data,
                'total_months': len(monthly_chart_data),
                'best_month': max(monthly_chart_data, key=lambda x: x['views']) if monthly_chart_data else None,
                'worst_month': min(monthly_chart_data, key=lambda x: x['views']) if monthly_chart_data else None
            },
            'content_analysis': {
                'top_categories': [
                    {'tag': tag, 'count': count}
                    for tag, count in top_categories
                ],
                'view_distribution': view_ranges,
                'total_categories': len(video_categories),
                'most_used_tag': top_categories[0] if top_categories else None
            },
            'growth_insights': {
                'subscriber_growth_rate': round((subscriber_count / days_since_created * 30), 2) if days_since_created > 0 else 0,
                'view_growth_rate': round((total_channel_views / days_since_created * 30), 2) if days_since_created > 0 else 0,
                'video_upload_frequency': round(total_channel_videos / (days_since_created / 30), 2) if days_since_created > 0 else 0,
                'engagement_growth': round(recent_engagement_rate - overall_engagement_rate, 2) if recent_videos else 0
            },
            'channel_status': {
                'is_active': total_channel_videos > 0,
                'engagement_level': 'High' if overall_engagement_rate > 5 else 'Medium' if overall_engagement_rate > 2 else 'Low',
                'growth_stage': 'New' if days_since_created < 90 else 'Growing' if days_since_created < 365 else 'Established',
                'content_quality': 'High' if avg_views_per_video > 100 else 'Medium' if avg_views_per_video > 50 else 'Low',
                'upload_consistency': 'High' if videos_per_month > 4 else 'Medium' if videos_per_month > 2 else 'Low'
            },
            'summary_stats': {
                'total_watch_time_hours': round(total_duration / 3600, 2),
                'avg_video_length_minutes': round(avg_duration_per_video / 60, 2),
                'total_interactions': total_likes + total_comments,
                'interaction_rate': round((total_likes + total_comments) / total_channel_views * 100, 2) if total_channel_views > 0 else 0,
                'subscriber_to_view_ratio': round(subscriber_count / total_channel_views * 100, 2) if total_channel_views > 0 else 0
            },
            'advanced_analytics': {
                'duration_distribution': duration_ranges,
                'engagement_distribution': engagement_ranges,
                'content_type_breakdown': content_types,
                'retention_analysis': retention_analysis,
                'growth_trajectory': growth_trajectory
            },
            'performance_scoring': {
                'top_videos_by_score': top_performing_by_score,
                'avg_performance_score': round(sum(score['score'] for score in performance_scores) / len(performance_scores), 2) if performance_scores else 0,
                'total_videos_scored': len(performance_scores)
            },
            'weekly_analytics': {
                'weekly_data': weekly_data,
                'weekly_trend': 'increasing' if len(weekly_data) >= 2 and weekly_data.get('Week 1', {}).get('views', 0) > weekly_data.get('Week 4', {}).get('views', 0) else 'decreasing' if len(weekly_data) >= 2 else 'stable',
                'best_week': max(weekly_data.items(), key=lambda x: x[1]['views']) if weekly_data else None,
                'most_engaging_week': max(weekly_data.items(), key=lambda x: x[1]['engagement_rate']) if weekly_data else None
            },
            'content_insights': {
                'most_effective_content_type': max(content_types.items(), key=lambda x: x[1])[0] if content_types else 'none',
                'optimal_video_length': max(duration_ranges.items(), key=lambda x: x[1])[0] if duration_ranges else 'none',
                'engagement_sweet_spot': max(engagement_ranges.items(), key=lambda x: x[1])[0] if engagement_ranges else 'none',
                'content_recommendations': [
                    'Focus on content types that perform best',
                    'Optimize video length based on audience preference',
                    'Improve engagement through better thumbnails and titles',
                    'Maintain consistent upload schedule'
                ]
            },
            'competitive_analysis': {
                'channel_health_score': round((overall_engagement_rate * 0.4 + (avg_views_per_video / 100) * 0.3 + (videos_per_month * 10) * 0.3), 2),
                'growth_potential': 'High' if overall_engagement_rate > 3 and videos_per_month > 2 else 'Medium' if overall_engagement_rate > 1.5 else 'Low',
                'audience_loyalty': 'High' if retention_analysis['avg_retention_rate'] > 5 else 'Medium' if retention_analysis['avg_retention_rate'] > 2 else 'Low',
                'content_consistency': 'High' if videos_per_month > 4 else 'Medium' if videos_per_month > 2 else 'Low'
            }
        }
        
        return DashboardResponse(
            success=True,
            message=f"Dashboard overview generated successfully",
            data=overview_data
        )
        
    except HTTPException:
        # Re-raise HTTP exceptions as they are already properly formatted
        raise
    except Exception as e:
        logger.error(f"Unexpected error in get_dashboard_overview route for user_id {current_user.id}: {e}")
        raise HTTPException(
            status_code=500,
            detail="Internal server error while generating dashboard overview"
        ) 