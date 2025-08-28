from typing import List, Dict, Any
from uuid import UUID
from fastapi import APIRouter, HTTPException, Depends, Path
from sqlmodel import Session
from pydantic import BaseModel
import json

from ..controllers.dashboard_controller import (
    get_playlists_controller,
    get_playlist_videos_controller,
    get_all_user_videos_controller,
    get_video_details_controller,
    get_all_playlists_comprehensive_controller,
    get_comprehensive_playlist_controller
)
from ..utils.database_dependency import get_database_session
from ..controllers.user_controller import get_current_user
from ..models.user_model import UserSignUp
from ..utils.my_logger import get_logger
from ..services.dashboard_data_service import DashboardDataService
from ..models.dashboard_playlist_video_model import DashboardPlaylistVideo
from ..models.dashboard_video_model import DashboardVideo
from ..models.dashboard_playlist_model import DashboardPlaylist

logger = get_logger("DASHBOARD_ROUTES")

router = APIRouter(prefix="/dashboard", tags=["dashboard-get"])

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



# @router.get("/playlists", response_model=PlaylistsResponse)
# async def get_dashboard_playlists(
#     current_user: UserSignUp = Depends(get_current_user),
#     db: Session = Depends(get_database_session)
# ) -> PlaylistsResponse:
#     """
#     Get all playlists with comprehensive analytics for dashboard.
    
#     This endpoint provides detailed information about all playlists including:
#     - Playlist metadata (title, description, thumbnail, etc.)
#     - Comprehensive performance metrics
#     - Content analysis and growth insights
#     - Top performing videos in each playlist
#     - Playlist health and recommendations
    
#     Args:
#         current_user: The authenticated user from JWT token
#         db: Database session dependency
    
#     Returns:
#         PlaylistsResponse: List of playlists with comprehensive analytics
        
#     Raises:
#         HTTPException: If error occurs
#     """
#     try:
#         logger.info(f"Dashboard playlists request received for user_id: {current_user.id}")
        
#         # Get comprehensive playlist data from database
#         playlists = DashboardDataService.get_playlists_data(current_user.id, db)
        
#         # If no data in database, return empty response
#         if not playlists:
#             return PlaylistsResponse(
#                 success=True,
#                 message="No playlist data found. Please fetch data first using /dashboard/playlists/fetch",
#                 data=[],
#                 count=0
#             )
        
#         return PlaylistsResponse(
#             success=True,
#             message=f"Successfully retrieved {len(playlists)} playlists with comprehensive analytics",
#             data=playlists,
#             count=len(playlists)
#         )
        
#     except HTTPException:
#         # Re-raise HTTP exceptions as they are already properly formatted
#         raise
#     except Exception as e:
#         logger.error(f"Unexpected error in get_dashboard_playlists route for user_id {current_user.id}: {e}")
#         raise HTTPException(
#             status_code=500,
#             detail="Internal server error while retrieving playlists"
#         )

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
        
        # Get comprehensive playlist analytics from database
        playlists = DashboardDataService.get_playlists_data(current_user.id, db)
        
        # Find the specific playlist
        playlist_data = None
        for playlist in playlists:
            if playlist.get('playlist_info', {}).get('playlist_id') == playlist_id:
                playlist_data = playlist
                break
        
        if not playlist_data:
            raise HTTPException(
                status_code=404,
                detail="Playlist not found in database. Please fetch data first using /dashboard/playlists/fetch"
            )
        
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
        
        # Get all videos with analytics from database
        videos = DashboardDataService.get_videos_data(current_user.id, db)
        
        # If no data in database, return empty response
        if not videos:
            return VideosResponse(
                success=True,
                message="No video data found. Please fetch data first using /dashboard/videos/fetch",
                data=[],
                count=0
            )
        
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
        
        # Get detailed video analytics from database
        videos = DashboardDataService.get_videos_data(current_user.id, db)
        
        # Find the specific video
        video_details = None
        for video in videos:
            if video.get('video_id') == video_id:
                video_details = video
                break
        
        if not video_details:
            raise HTTPException(
                status_code=404,
                detail="Video not found in database. Please fetch data first using /dashboard/videos/fetch"
            )
        
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
        
        # Get videos for the specific playlist using relationship table
        videos = DashboardDataService.get_playlist_videos(current_user.id, playlist_id, db)
        
        if not videos:
            return VideosResponse(
                success=True,
                message="No videos found for this playlist in database. Please fetch data first using /dashboard/playlists/fetch",
                data=[],
                count=0
            )
        
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


@router.get("/playlists/{playlist_id}/videos/{video_id}", response_model=VideoDetailResponse)
async def get_dashboard_playlist_video_details(
    playlist_id: str = Path(..., description="The YouTube playlist ID"),
    video_id: str = Path(..., description="The YouTube video ID"),
    current_user: UserSignUp = Depends(get_current_user),
    db: Session = Depends(get_database_session)
) -> VideoDetailResponse:
    """
    Get detailed analytics for a specific video within a playlist.
    
    This endpoint provides comprehensive information about a single video in a specific playlist
    including video metadata, performance metrics, analytics, and playlist-specific context.
    
    Args:
        playlist_id: The YouTube playlist ID
        video_id: The YouTube video ID
        current_user: The authenticated user from JWT token
        db: Database session dependency
    
    Returns:
        VideoDetailResponse: Detailed video analytics with playlist context
        
    Raises:
        HTTPException: If error occurs
    """
    try:
        logger.info(f"Dashboard playlist video details request received for playlist_id: {playlist_id}, video_id: {video_id}, user_id: {current_user.id}")
        
        # First verify the video belongs to the playlist
        playlist_video = db.query(DashboardPlaylistVideo).filter(
            DashboardPlaylistVideo.user_id == current_user.id,
            DashboardPlaylistVideo.playlist_id == playlist_id,
            DashboardPlaylistVideo.video_id == video_id
        ).first()
        
        if not playlist_video:
            raise HTTPException(
                status_code=404,
                detail="Video not found in this playlist or you don't have permission to access it"
            )
        
        # Get video details from dashboard_videos table
        video_record = db.query(DashboardVideo).filter(
            DashboardVideo.user_id == current_user.id,
            DashboardVideo.video_id == video_id
        ).first()
        
        if not video_record:
            raise HTTPException(
                status_code=404,
                detail="Video details not found in database. Please fetch data first using /dashboard/videos/fetch"
            )
        
        # Get playlist info for context
        playlist_record = db.query(DashboardPlaylist).filter(
            DashboardPlaylist.user_id == current_user.id,
            DashboardPlaylist.playlist_id == playlist_id
        ).first()
        
        # Build video data with playlist context
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
            'analytics': json.loads(video_record.analytics),
            # Add playlist context
            'playlist_context': {
                'playlist_id': playlist_id,
                'playlist_title': playlist_record.title if playlist_record else '',
                'playlist_description': playlist_record.description if playlist_record else '',
                'position_in_playlist': playlist_video.position,
                'total_videos_in_playlist': playlist_record.video_count if playlist_record else 0
            }
        }
        
        return VideoDetailResponse(
            success=True,
            message=f"Successfully retrieved details for video '{video_data['title']}' in playlist '{video_data['playlist_context']['playlist_title']}'",
            data=video_data
        )
        
    except HTTPException:
        # Re-raise HTTP exceptions as they are already properly formatted
        raise
    except Exception as e:
        logger.error(f"Unexpected error in get_dashboard_playlist_video_details route for playlist_id {playlist_id}, video_id {video_id}, user_id {current_user.id}: {e}")
        raise HTTPException(
            status_code=500,
            detail="Internal server error while retrieving playlist video details"
        )



@router.get("/overview", response_model=DashboardResponse)
async def get_dashboard_overview(
    current_user: UserSignUp = Depends(get_current_user),
    db: Session = Depends(get_database_session)
) -> DashboardResponse:
    """
    Get dashboard overview with summary statistics from database.
    
    This endpoint provides a high-level overview of the user's YouTube channel
    including total playlists, total videos, overall performance metrics, etc.
    
    Args:
        current_user: The authenticated user from JWT token
        db: Database session dependency
    
    Returns:
        DashboardResponse: Dashboard overview data from database
        
    Raises:
        HTTPException: If error occurs or no data found
    """
    try:
        logger.info(f"Dashboard overview request received for user_id: {current_user.id}")
        
        # Get overview data from database
        overview_data = DashboardDataService.get_overview_data(current_user.id, db)
        
        if not overview_data:
            raise HTTPException(
                status_code=404,
                detail="No overview data found in database. Please fetch data first using /dashboard/overview/fetch"
            )
        
        # Return the overview data from database
        return DashboardResponse(
            success=True,
            message="Dashboard overview retrieved successfully from database",
            data=overview_data
        )
        
    except HTTPException:
        # Re-raise HTTP exceptions as they are already properly formatted
        raise
    except Exception as e:
        logger.error(f"Unexpected error in get_dashboard_overview route for user_id {current_user.id}: {e}")
        raise HTTPException(
            status_code=500,
            detail="Internal server error while retrieving dashboard overview"
        ) 