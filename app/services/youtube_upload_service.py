import os
from typing import Optional, Dict, Any
from uuid import UUID
from googleapiclient.http import MediaFileUpload
from googleapiclient.errors import HttpError
from sqlmodel import Session, select

from ..models.video_model import Video
from ..services.youtube_auth_service import get_youtube_client
from ..utils.my_logger import get_logger

logger = get_logger("YOUTUBE_UPLOAD_SERVICE")

def upload_video_to_youtube(video_id: UUID, user_id: UUID, db: Session) -> Optional[Dict[str, Any]]:
    """
    Upload a video to YouTube with all data from database.
    
    Args:
        video_id: UUID of the video to upload
        user_id: UUID of the user
        db: Database session
        
    Returns:
        Dict containing upload result or None if failed
    """
    try:
        logger.info(f"Starting YouTube upload for video {video_id}, user {user_id}")
        
        # Get YouTube client
        youtube = get_youtube_client(user_id, db)
        if not youtube:
            logger.error(f"Failed to get YouTube client for user {user_id}")
            return None
        
        # Get video from database
        statement = select(Video).where(Video.id == video_id, Video.user_id == user_id)
        video = db.exec(statement).first()
        
        if not video:
            logger.error(f"Video not found: {video_id}")
            return None
        
        # Validate video file exists
        if not os.path.exists(video.video_path):
            logger.error(f"Video file not found: {video.video_path}")
            return None
        
        # Determine upload privacy status
        if video.schedule_datetime:
            upload_privacy_status = 'private'  # Always private when scheduling
        else:
            upload_privacy_status = video.privacy_status or 'private'
        
        # Prepare video metadata
        body = {
            'snippet': {
                'title': video.title or 'Untitled Video',
                'description': video.description or '',
                'tags': ['auto-generated', 'transcript-based'],
                'categoryId': '22'  # People & Blogs
            },
            'status': {
                'privacyStatus': upload_privacy_status,
                'selfDeclaredMadeForKids': False
            }
        }
        
        # Add scheduling if provided
        if video.schedule_datetime:
            body['status']['publishAt'] = video.schedule_datetime
        
        # Create media upload object
        media = MediaFileUpload(
            video.video_path,
            chunksize=-1,
            resumable=True,
            mimetype='video/mp4'
        )
        
        logger.info(f"Uploading video: {video.title} ({upload_privacy_status})")
        
        # Upload video
        upload_request = youtube.videos().insert(
            part=','.join(body.keys()),
            body=body,
            media_body=media,
        )
        
        # Monitor upload progress
        response = None
        while response is None:
            status, response = upload_request.next_chunk()
            if status:
                progress = int(status.progress() * 100)
                logger.info(f"Upload progress: {progress}%")
        
        youtube_video_id = response['id']
        logger.info(f"Video uploaded successfully! YouTube ID: {youtube_video_id}")
        
        # Upload thumbnail if available in database
        thumbnail_result = None
        if video.thumbnail_path and os.path.exists(video.thumbnail_path):
            try:
                logger.info(f"Uploading thumbnail: {video.thumbnail_path}")
                
                # Upload thumbnail
                youtube.thumbnails().set(
                    videoId=youtube_video_id,
                    media_body=MediaFileUpload(video.thumbnail_path, mimetype='image/jpeg')
                ).execute()
                
                thumbnail_result = {
                    'success': True,
                    'thumbnail_path': video.thumbnail_path,
                    'message': 'Thumbnail uploaded successfully'
                }
                logger.info(f"Thumbnail uploaded successfully for video {youtube_video_id}")
                
            except HttpError as e:
                logger.error(f"Error uploading thumbnail: {e}")
                thumbnail_result = {
                    'success': False,
                    'error': str(e),
                    'message': 'Failed to upload thumbnail'
                }
            except Exception as e:
                logger.error(f"Unexpected error uploading thumbnail: {e}")
                thumbnail_result = {
                    'success': False,
                    'error': str(e),
                    'message': 'Failed to upload thumbnail'
                }
        elif video.thumbnail_path:
            logger.warning(f"Thumbnail file not found: {video.thumbnail_path}")
            thumbnail_result = {
                'success': False,
                'error': 'Thumbnail file not found',
                'message': 'Thumbnail file not found on disk'
            }
        else:
            logger.info("No thumbnail available for upload")
            thumbnail_result = {
                'success': False,
                'message': 'No thumbnail available'
            }
        
        # Update database
        video.youtube_video_id = youtube_video_id
        video.video_status = 'uploaded'
        db.add(video)
        db.commit()
        db.refresh(video)
        
        # Add to playlist if video has saved playlist name
        playlist_result = None
        if video.playlist_name:
            try:
                # Get user's playlists
                playlists_response = youtube.playlists().list(
                    part='snippet',
                    mine=True,
                    maxResults=50
                ).execute()
                
                # Find or create playlist
                playlist_id = None
                for playlist in playlists_response.get('items', []):
                    if playlist['snippet']['title'].lower() == video.playlist_name.lower():
                        playlist_id = playlist['id']
                        break
                
                if not playlist_id:
                    # Create new playlist
                    playlist_body = {
                        'snippet': {
                            'title': video.playlist_name,
                            'description': f'Playlist created by {video.playlist_name}'
                        },
                        'status': {
                            'privacyStatus': 'private'
                        }
                    }
                    playlist_response = youtube.playlists().insert(
                        part='snippet,status',
                        body=playlist_body
                    ).execute()
                    playlist_id = playlist_response['id']
                
                # Add video to playlist
                youtube.playlistItems().insert(
                    part='snippet',
                    body={
                        'snippet': {
                            'playlistId': playlist_id,
                            'resourceId': {
                                'kind': 'youtube#video',
                                'videoId': youtube_video_id
                            }
                        }
                    }
                ).execute()
                
                playlist_result = {
                    'playlist_name': video.playlist_name,
                    'playlist_id': playlist_id,
                    'success': True
                }
                logger.info(f"Video added to playlist: {video.playlist_name}")
                
            except Exception as e:
                logger.error(f"Error adding to playlist: {e}")
                playlist_result = {'success': False, 'error': str(e)}
        else:
            logger.info("No playlist selected for this video")
            playlist_result = {
                'success': False,
                'message': 'No playlist selected'
            }
        
        # Prepare response
        result = {
            'success': True,
            'youtube_video_id': youtube_video_id,
            'video_title': video.title,
            'privacy_status': video.privacy_status,
            'schedule_datetime': video.schedule_datetime,
            'youtube_url': f"https://www.youtube.com/watch?v={youtube_video_id}",
            'playlist_result': playlist_result,
            'thumbnail_result': thumbnail_result
        }
        
        if video.schedule_datetime:
            result['message'] = f"Video uploaded and scheduled for {video.schedule_datetime}"
        else:
            result['message'] = "Video uploaded successfully"
        
        logger.info(f"YouTube upload completed for video {video_id}")
        return result
        
    except HttpError as e:
        logger.error(f"YouTube API error: {e}")
        return None
    except Exception as e:
        logger.error(f"Error uploading video: {e}")
        return None 