from pydantic import BaseModel, Field
import json
from google import genai
import subprocess
import os
import shutil
from pathlib import Path
from sqlmodel import Session, select
from uuid import UUID
from ..utils.my_logger import get_logger
from ..models.video_model import Video  
logger = get_logger("VIDEO_TRANSCRIPT_GENERATOR")

# Get ffmpeg path - try multiple locations
def get_ffmpeg_path():
    """Get the path to ffmpeg executable"""
    possible_paths = [
        '/usr/bin/ffmpeg',  # Standard Linux location
        '/usr/local/bin/ffmpeg',  # Alternative location
        'ffmpeg',  # Fallback to PATH
    ]
    
    for path in possible_paths:
        if os.path.exists(path) or shutil.which(path):
            logger.info(f"Found ffmpeg at: {path}")
            return path
    
    raise FileNotFoundError("ffmpeg not found in any of the expected locations")


class TranscriptSegment(BaseModel):
    timestamp: str = Field(description="Timestamp in MM:SS format (e.g., '00:00', '01:30')")
    text: str = Field(description="The transcript text for this segment")

class TranscriptOutput(BaseModel):
    segments: list[TranscriptSegment] = Field(
        description="List of transcript segments with timestamps"
    )



def generate_video_transcript(video_path: str) -> TranscriptOutput:
    """
    Extract audio from video and generate transcript using Google GenAI API.
    Automatically cleans up the temporary audio file after transcript generation.
    
    Args:
        video_path (str): Path to input video file
        
    Returns:
        TranscriptOutput: Generated transcript with timestamps
    """
 

    # Generate temporary audio path
    audio_path = str(Path(video_path).with_suffix('.mp3'))

    try:
        # Get ffmpeg path
        ffmpeg_path = get_ffmpeg_path()
        
        # Extract audio using ffmpeg
        cmd = [
            ffmpeg_path,
            '-i', video_path,  # Input file
            '-q:a', '0',       # Highest quality
            '-map', 'a',       # Extract audio only
            '-y',              # Overwrite output file if exists
            audio_path
        ]
        
        logger.info(f"Running ffmpeg command: {' '.join(cmd)}")
        result = subprocess.run(cmd, check=True, capture_output=True, text=True)
        logger.info(f"Audio extracted successfully to: {audio_path}")

        # Generate transcript
        client = genai.Client()
        myfile = client.files.upload(file=audio_path)
        
        prompt = """
        Generate a detailed transcript of this audio clip with timestamps.
        
        Return the response in the following JSON format:
        {
            "segments": [
                {
                    "timestamp": "MM:SS",
                    "text": "transcript text for this segment"
                }
            ]
        }
        
        Rules:
        1. Start with timestamp "00:00"
        3. Timestamps must be in MM:SS format with seconds 0-59
        4. Include all spoken content accurately
        5. Maintain chronological order
        6. Each segment should contain complete thoughts or sentences
        """
        
        response = client.models.generate_content(
            model="gemini-2.5-flash",
            contents=[prompt, myfile],
            config={
                "response_mime_type": "application/json",
                "response_schema": TranscriptOutput.model_json_schema(),
            }
        )
        
        logger.info("Transcript generated successfully")
        
        # Parse response and clean up audio file
        transcript_data = json.loads(response.text)
        os.remove(audio_path)
        logger.info(f"Temporary audio file removed: {audio_path}")
        
        return TranscriptOutput(**transcript_data)
        
    except subprocess.CalledProcessError as e:
        error_msg = f"Error extracting audio: {e.stderr if e.stderr else str(e)}"
        logger.error(error_msg)
        if os.path.exists(audio_path):
            os.remove(audio_path)
        raise Exception(error_msg)
    except Exception as e:
        error_msg = f"Error in transcript generation: {e}"
        logger.error(error_msg)
        if os.path.exists(audio_path):
            os.remove(audio_path)
        raise Exception(error_msg)





async def generate_transcript_background(video_id: UUID, video_path: str, db: Session):
    """
    Background task to generate transcript for a video
    """
    try:
        logger.info(f"Starting background transcript generation for video: {video_path}")
        transcript_output = generate_video_transcript(video_path)
        transcript_json = transcript_output.model_dump_json()
        
        # Update the video record with transcript
        statement = select(Video).where(Video.id == video_id)
        video = db.exec(statement).first()
        if video:
            video.transcript = transcript_json
            db.add(video)
            db.commit()
            logger.info(f"Transcript generated and stored successfully for video: {video_path}")
        else:
            logger.error(f"Video not found for transcript update: {video_id}")
            
    except Exception as e:
        logger.error(f"Failed to generate transcript for video {video_path}: {e}")