from agents import Agent, Runner, AgentOutputSchema, set_tracing_disabled ,OpenAIChatCompletionsModel,AsyncOpenAI
from agents.extensions.models.litellm_model import LitellmModel
from dotenv import load_dotenv
import os
from pydantic import BaseModel, Field
import re
from datetime import datetime, timedelta
import asyncio
import json
load_dotenv()
set_tracing_disabled(True)

# model = LitellmModel(
#     model="gemini/gemini-2.0-flash",
#     api_key="AIzaSyBf-7p-DiTq3s1rLwwnC_jaXVWEK8naVjE",
# )

class TimeStampsGeneratorOutput(BaseModel):
            timestamps: list[str] = Field(
                description="List of timestamps in format 'MM:SS Topic Name' (e.g., '00:00 Introduction', '01:30 Main Topic')",
                examples=[
                    ["00:00 Introduction", "01:30 Main Topic", "03:45 Conclusion"]
                ]
            )



def validate_and_fix_timestamps(timestamps_text: str) -> str:
    """
    Validate and fix timestamps to ensure they are in proper MM:SS format.
    
    Args:
        timestamps_text (str): Raw timestamps text from agent
    
    Returns:
        str: Fixed timestamps text
    """
    # Extract timestamps using regex
    timestamp_pattern = r'(\d{1,2}):(\d{1,2})'
    
    def fix_timestamp(match):
        minutes = int(match.group(1))
        seconds = int(match.group(2))
        
        # Fix invalid seconds (should be 0-59)
        if seconds >= 60:
            minutes += seconds // 60
            seconds = seconds % 60
        
        # Ensure minutes don't exceed reasonable limits (e.g., 999)
        if minutes > 999:
            minutes = 999
        
        # Format as MM:SS
        return f"{minutes:02d}:{seconds:02d}"
    
    # Fix all timestamps in the text
    fixed_text = re.sub(timestamp_pattern, fix_timestamp, timestamps_text)
    
    return fixed_text

async def time_stamps_generator(transcript: str,api_key: str) -> str:
    
    if api_key:
        client = AsyncOpenAI(
            api_key=api_key,
            base_url="https://generativelanguage.googleapis.com/v1beta/openai/"
        )
    else:
        client = AsyncOpenAI(
            api_key="AIzaSyBf-7p-DiTq3s1rLwwnC_jaXVWEK8naVjE",
            base_url="https://generativelanguage.googleapis.com/v1beta/openai/"
        )
    model = OpenAIChatCompletionsModel(
            openai_client=client,
            model="gemini-2.0-flash",
        )
       

    agent = Agent(
            model=model,
            name="YouTube Video Time Stamps Generator",
            instructions="""Your job is to generate time stamps for a youtube video based on its transcript
            in english create chapters for the video for example discussion , topic start, topic end  example , discussion , introduction , conclusion , etc.
            
            You should generate time stamps in the following format:
            - Each timestamp should be a string in format: "MM:SS Topic Name"
            - Example: "00:00 Introduction", "01:30 Main Topic", "03:45 Conclusion"
            
            # 🧠 Rules for YouTube Chapters to Work:
            
                1. Must start with 00:00

                2. Each timestamp must be followed by a space and then a title

                3. There must be at least 3 timestamps

                4. Each timestamp must be chronologically increasing

                5. dont create too many chapters just important and bigger chapters

                6. dont create chapters that are too short like 00:01 , 00:02 , 00:03 , etc.

                7. IMPORTANT: Seconds must be between 00-59 (never 60 or higher)
                Examples: 00:00, 00:30, 01:00, 01:45, 02:30 (✅ CORRECT)
                Examples: 00:60, 01:78, 02:99 (❌ WRONG - seconds > 59)

                8. Minutes can be any number but seconds must be 0-59

                9. Format must be MM:SS where MM = minutes, SS = seconds (0-59)

                10. Return as a list of strings, not a dictionary

            """,
            output_type=TimeStampsGeneratorOutput,
        )
    
    result = await Runner.run(
        agent,
        input="Generate timestamps for the youtube video. Create important chapters only, start with 00:00, and ensure all timestamps are in MM:SS format with seconds 0-59: " + transcript,
    )
    
    # Get the structured output
    output = result.final_output
    
    # Validate and fix each timestamp
    fixed_timestamps = []
    for timestamp_entry in output.timestamps:
        # Extract the timestamp part (before the first space)
        parts = timestamp_entry.split(' ', 1)
        if len(parts) >= 2:
            timestamp = parts[0]
            topic = parts[1]
            fixed_timestamp = validate_and_fix_timestamps(timestamp)
            fixed_timestamps.append(f"{fixed_timestamp} {topic}")
        else:
            # If no space found, just fix the timestamp
            fixed_timestamps.append(validate_and_fix_timestamps(timestamp_entry))
    
    # Join with newlines
    return "\n".join(fixed_timestamps)
