from typing import List, Dict, Any, Optional
from uuid import UUID
from googleapiclient.errors import HttpError
from sqlmodel import Session, select
from ..models.video_model import Video
from ..services.youtube_auth_service import get_youtube_client
from ..utils.my_logger import get_logger

logger = get_logger("PLAYLIST_SERVICE")

# Default values for playlist creation
DEFAULT_PLAYLIST_DESCRIPTION = "Playlist created by {name}"
DEFAULT_PRIVACY_STATUS = "private"

def _get_playlists_response(youtube):
    """
    Helper function to get playlists response from YouTube API.
    
    Args:
        youtube: Authenticated YouTube API client
    
    Returns:
        dict: YouTube API response for playlists
    """
    return youtube.playlists().list(
        part='snippet',
        mine=True,
        maxResults=50
    ).execute()

def get_user_playlists(youtube):
    """
    Get all playlists from the user's channel.
    
    Args:
        youtube: Authenticated YouTube API client
    
    Returns:
        list: List of playlist dictionaries with id, title, and description
    """
    try:
        playlists_response = _get_playlists_response(youtube)
        
        playlists = []
        for playlist in playlists_response.get('items', []):
            playlists.append({
                'id': playlist['id'],
                'title': playlist['snippet']['title'],
                'description': playlist['snippet'].get('description', ''),
                'privacy': playlist['snippet'].get('privacyStatus', 'private')
            })
        
        logger.info(f"Successfully fetched {len(playlists)} playlists")
        return playlists
        
    except HttpError as e:
        logger.error(f"❌ Error fetching playlists: {e}")
        return []

def create_new_playlist(youtube, playlist_name, description="", privacy_status="private"):
    """
    Create a new playlist.
    
    Args:
        youtube: Authenticated YouTube API client
        playlist_name (str): Name of the playlist
        description (str): Description for the playlist
        privacy_status (str): Privacy status of the playlist (private, public, unlisted)
    
    Returns:
        str: Playlist ID
    """
    try:
        return _execute_playlist_creation(youtube, playlist_name, description, privacy_status)
    except HttpError as e:
        logger.error(f"❌ Error creating playlist: {e}")
        raise

def add_video_to_playlist(youtube, playlist_id: str, video_id: str) -> bool:
    """
    Add a video to a playlist.
    
    Args:
        youtube: Authenticated YouTube API client
        playlist_id (str): YouTube playlist ID
        video_id (str): YouTube video ID
    
    Returns:
        bool: True if successful, False otherwise
    """
    try:
        request_body = {
            'snippet': {
                'playlistId': playlist_id,
                'resourceId': {
                    'kind': 'youtube#video',
                    'videoId': video_id
                }
            }
        }
        
        response = youtube.playlistItems().insert(
            part='snippet',
            body=request_body
        ).execute()
        
        logger.info(f"✅ Successfully added video {video_id} to playlist {playlist_id}")
        return True
        
    except HttpError as e:
        logger.error(f"❌ Error adding video to playlist: {e}")
        return False
    except Exception as e:
        logger.error(f"❌ Unexpected error adding video to playlist: {e}")
        return False

def select_and_save_playlist_for_video(video_id: UUID, user_id: UUID, playlist_name: str, db: Session) -> Optional[Dict[str, Any]]:
    """
    Select a playlist and save it to the video model.
    
    Args:
        video_id: UUID of the video
        user_id: UUID of the user
        playlist_name: Name of the playlist to select
        db: Database session
    
    Returns:
        Dict containing playlist selection result or None if failed
    """
    try:
        # Get video from database
        statement = select(Video).where(Video.id == video_id, Video.user_id == user_id)
        video = db.exec(statement).first()
        
        if not video:
            logger.error(f"Video not found: {video_id}")
            return None
        
        # Get YouTube client
        youtube = get_youtube_client(user_id, db)
        if not youtube:
            logger.error(f"Failed to get YouTube client for user {user_id}")
            return None
        
        # Get user's playlists
        playlists = get_user_playlists(youtube)
        
        # Find existing playlist or create new one
        playlist_id = None
        playlist_exists = False
        
        for playlist in playlists:
            if playlist['title'].lower() == playlist_name.lower():
                playlist_id = playlist['id']
                playlist_exists = True
                break
        
        if not playlist_id:
            # Create new playlist
            try:
                playlist_id = create_new_playlist(youtube, playlist_name)
                logger.info(f"Created new playlist: {playlist_name}")
            except Exception as e:
                logger.error(f"Error creating playlist: {e}")
                return None
        
        # Save playlist name to video model
        video.playlist_name = playlist_name
        db.add(video)
        db.commit()
        db.refresh(video)
        
        result = {
            'success': True,
            'playlist_name': playlist_name,
            'playlist_id': playlist_id,
            'playlist_exists': playlist_exists,
            'video_id': str(video_id),
            'message': f"Playlist '{playlist_name}' {'selected' if playlist_exists else 'created and selected'} for video"
        }
        
        logger.info(f"Successfully saved playlist '{playlist_name}' for video {video_id}")
        return result
        
    except Exception as e:
        logger.error(f"Error selecting playlist for video {video_id}: {e}")
        return None

def get_video_playlist(video_id: UUID, user_id: UUID, db: Session) -> Optional[Dict[str, Any]]:
    """
    Get the selected playlist for a video.
    
    Args:
        video_id: UUID of the video
        user_id: UUID of the user
        db: Database session
    
    Returns:
        Dict containing playlist information or None if not found
    """
    try:
        # Get video from database
        statement = select(Video).where(Video.id == video_id, Video.user_id == user_id)
        video = db.exec(statement).first()
        
        if not video:
            logger.error(f"Video not found: {video_id}")
            return None
        
        if not video.playlist_name:
            return None
        
        # Get YouTube client to verify playlist still exists
        youtube = get_youtube_client(user_id, db)
        if not youtube:
            logger.error(f"Failed to get YouTube client for user {user_id}")
            return None
        
        # Get user's playlists to find the playlist ID
        playlists = get_user_playlists(youtube)
        playlist_id = None
        
        for playlist in playlists:
            if playlist['title'].lower() == video.playlist_name.lower():
                playlist_id = playlist['id']
                break
        
        return {
            'playlist_name': video.playlist_name,
            'playlist_id': playlist_id,
            'video_id': str(video_id),
            'playlist_exists': playlist_id is not None
        }
        
    except Exception as e:
        logger.error(f"Error getting playlist for video {video_id}: {e}")
        return None

def _create_playlist_body(title, description="", privacy_status="private"):
    """
    Helper function to create playlist request body.
    
    Args:
        title (str): Playlist title
        description (str): Playlist description
        privacy_status (str): Privacy status of the playlist
    
    Returns:
        dict: Playlist request body
    """
    return {
        'snippet': {
            'title': title,
            'description': description or DEFAULT_PLAYLIST_DESCRIPTION.format(name=title)
        },
        'status': {
            'privacyStatus': privacy_status
        }
    }

def _execute_playlist_creation(youtube, title, description="", privacy_status="private"):
    """
    Helper function to execute playlist creation.
    
    Args:
        youtube: Authenticated YouTube API client
        title (str): Playlist title
        description (str): Playlist description
        privacy_status (str): Privacy status of the playlist
    
    Returns:
        str: Playlist ID
    """
    playlist_response = youtube.playlists().insert(
        part='snippet,status',
        body=_create_playlist_body(title, description, privacy_status)
    ).execute()
    
    playlist_id = playlist_response['id']
    logger.info(f"✅ Created new playlist: {title} with ID: {playlist_id} and privacy: {privacy_status}")
    return playlist_id

def get_playlist_videos_by_id(youtube, playlist_id: str) -> List[Dict[str, Any]]:
    """
    Get videos from a specific playlist using playlist ID.
    
    Args:
        youtube: Authenticated YouTube API client
        playlist_id: YouTube playlist ID
    
    Returns:
        List[Dict[str, Any]]: List of videos with their details
    """
    try:
        # Get playlist items
        request = youtube.playlistItems().list(
            part='snippet,contentDetails',
            playlistId=playlist_id,
            maxResults=50
        )
        
        videos = []
        while request:
            response = request.execute()
            
            for item in response['items']:
                video_id = item['contentDetails']['videoId']
                snippet = item['snippet']
                
                # Get additional video details
                video_details = get_video_details(youtube, video_id)
                
                video_data = {
                    'title': snippet['title'],
                    'url': f"https://www.youtube.com/watch?v={video_id}",
                    'video_id': video_id,
                    'published_at': snippet['publishedAt'],
                    'description': snippet.get('description', ''),
                    'thumbnails': snippet.get('thumbnails', {}),
                    'position': snippet.get('position', 0)
                }
                
                # Add video details if available
                if video_details:
                    video_data.update({
                        'view_count': video_details.get('viewCount', 'N/A'),
                        'like_count': video_details.get('likeCount', 'N/A'),
                        'comment_count': video_details.get('commentCount', 'N/A'),
                        'duration': video_details.get('duration', 'N/A'),
                        'privacy_status': video_details.get('status', 'N/A')
                    })
                
                videos.append(video_data)
            
            request = youtube.playlistItems().list_next(request, response)
        
        logger.info(f"Successfully fetched {len(videos)} videos from playlist ID: {playlist_id}")
        return videos
        
    except HttpError as e:
        logger.error(f"❌ Error fetching playlist videos from YouTube API: {e}")
        return []
    except Exception as e:
        logger.error(f"❌ Unexpected error fetching playlist videos: {e}")
        return []

def get_video_details(youtube, video_id: str) -> Optional[Dict[str, Any]]:
    """
    Get additional details for a specific video.
    
    Args:
        youtube: Authenticated YouTube API client
        video_id: YouTube video ID
    
    Returns:
        Optional[Dict[str, Any]]: Video details or None if error
    """
    try:
        request = youtube.videos().list(
            part='statistics,contentDetails,status',
            id=video_id
        )
        response = request.execute()
        
        if response['items']:
            video = response['items'][0]
            return {
                'viewCount': video['statistics'].get('viewCount', 'N/A'),
                'likeCount': video['statistics'].get('likeCount', 'N/A'),
                'commentCount': video['statistics'].get('commentCount', 'N/A'),
                'duration': video['contentDetails'].get('duration', 'N/A'),
                'status': video['status'].get('privacyStatus', 'N/A')
            }
        return None
        
    except Exception as e:
        logger.error(f"Error getting video details for video ID {video_id}: {e}")
        return None 