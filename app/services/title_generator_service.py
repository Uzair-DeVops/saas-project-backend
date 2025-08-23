import json
import re
from typing import Optional, List
from uuid import UUID
from sqlmodel import Session, select
from pydantic import BaseModel, Field
from agents import Agent, Runner, set_tracing_disabled, SQLiteSession
from agents.extensions.models.litellm_model import LitellmModel, ModelSettings
from dotenv import load_dotenv
import os

from ..models.video_model import Video
from ..utils.my_logger import get_logger
from ..utils.transcript_dependency import get_video_transcript

logger = get_logger("TITLE_GENERATOR")

# Initialize agents session

load_dotenv()

class TitleGeneratorOutput(BaseModel):
    titles: List[str] = Field(..., description="List of 10 eye-catching YouTube titles")

class TitleRequest(BaseModel):
    video_id: UUID
    user_requirements: Optional[str] = None

class TitleResponse(BaseModel):
    video_id: UUID
    generated_titles: List[str]
    success: bool
    message: str

class TitleUpdateRequest(BaseModel):
    video_id: UUID
    title: str


async def generate_title_from_transcript(transcript: str, user_requirements: Optional[str] = None, api_key: Optional[str] = None) -> TitleGeneratorOutput:
    """
    Generate a title from video transcript using the agents library
    """



    # Initialize the model and agent
    if api_key:
        model = LitellmModel(
            model="gemini/gemini-2.0-flash",
            api_key=api_key,
        )
    else:
        model = LitellmModel(
            model="gemini/gemini-2.0-flash",
            api_key="AIzaSyBf-7p-DiTq3s1rLwwnC_jaXVWEK8naVjE",
        )

    agent = Agent(
        name="YouTube Title Generator",
        model_settings=ModelSettings(
            temperature=0.5,
            frequency_penalty=1
        ),
        instructions="""You are a YouTube title generator specialized in creating engaging titles for educational and lecture-style content. You are given a transcript of a YouTube video and you need to generate 10 eye-catching titles that will attract viewers interested in learning.

    # IMPORTANT REQUIREMENTS:
    1. Generate exactly 10 different eye-catching YouTube titles
    2. Each title should be in English language only
    3. Each title should be less than 80 characters
    4. Make titles engaging, clickable, and optimized for YouTube's algorithm
    5. Use different styles: educational, curiosity-driven, problem-solving, skill-building, etc.
    6. Focus on the main topics and learning outcomes from the video
    7. Include relevant keywords, trending terms, and educational markers (e.g. "Tutorial", "Guide", "Masterclass")
    8. Make titles that signal clear value and learning benefits to viewers
    9. Vary the format: some with emojis (📚, ✨, 🎓), some with numbers, some questions, some statements
    10. Ensure each title is unique and different from the others
    11. Emphasize the educational/instructional nature of the content
    12. Use power words that resonate with learners: "Master", "Learn", "Understand", "Discover"
    13. Include skill level indicators where relevant (Beginner, Advanced, etc.)
    14. Consider adding time-saving or efficiency claims when appropriate
    15. Incorporate social proof elements ("Expert Shows", "Professor Explains")

    Generate 10 unique, education-focused titles that will attract viewers seeking quality learning content.
    """,
        model=model,
        output_type=TitleGeneratorOutput,
    )
    try:
        if user_requirements:
            prompt = f"Generate the title of the YouTube video for the following transcript: {transcript}\n\nAdditional requirements: {user_requirements}"
        else:
            prompt = f"Generate the title of the YouTube video for the following transcript: {transcript}"
        
        result = await Runner.run(
            agent,
            input=prompt,
        )
        
        return result.final_output
        
    except Exception as e:
        logger.error(f"Error generating title from transcript: {e}")
        raise



async def generate_video_title(video_id: UUID, user_id: UUID, db: Session, user_requirements: Optional[str] = None, api_key: Optional[str] = None) -> TitleResponse:
    """
    Generate title for a video using its transcript
    """
    try:
        # Get video transcript
        transcript = get_video_transcript(video_id, user_id, db)
        
        if not transcript:
            return TitleResponse(
                video_id=video_id,
                generated_titles=[],
                success=False,
                message="Video transcript not found or not generated yet"
            )
        
        # Parse transcript if it's JSON
            # If not JSON, use as plain text
        transcript_text = transcript
        
        # Generate titles
        title_output = await generate_title_from_transcript(transcript_text, user_requirements, api_key)
        
        return TitleResponse(
            video_id=video_id,
            generated_titles=title_output.titles,
            success=True,
            message="Titles generated successfully"
        )
        
    except Exception as e:
        logger.error(f"Error generating video title: {e}")
        return TitleResponse(
            video_id=video_id,
            generated_titles=[],
            success=False,
            message=f"Error generating titles: {str(e)}"
        )

async def update_video_title(video_id: UUID, user_id: UUID, title: str, db: Session) -> bool:
    """
    Update video title in database
    """
    try:
        statement = select(Video).where(
            Video.id == video_id,
            Video.user_id == user_id
        )
        video = db.exec(statement).first()
        
        if not video:
            logger.error(f"Video not found: {video_id}")
            return False
        
        # Update video title
        video.title = title
        db.add(video)
        db.commit()
        
        logger.info(f"Title updated for video {video_id}: {title}")
        
        return True
        
    except Exception as e:
        logger.error(f"Error updating video title: {e}")
        return False

async def regenerate_title(video_id: UUID, user_id: UUID, db: Session) -> TitleResponse:
    """
    Regenerate title for a video
    """
    return await generate_video_title(video_id, user_id, db)
