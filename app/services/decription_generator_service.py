from agents import Agent, Runner, set_tracing_disabled,ModelSettings
from agents.extensions.models.litellm_model import LitellmModel
from pydantic import BaseModel, Field
from typing import Optional
from ..utils.gemini_dependency import get_user_gemini_api_key

set_tracing_disabled(True)


class VideoSummaryGeneratorOutput(BaseModel):
    summary_of_the_video : str = Field(..., description=f"summary of the video")
    topics_as_hastages: list[str] = Field(..., description="topics as hastages")
    keywords: list[str] = Field(..., description="keywords SEO friendly for Youtube")




def clean_text_for_youtube(text: str) -> str:
    """
    Clean text to make it YouTube-compatible while preserving formatting and spacing.
    """
    import re

    # Remove markdown formatting but preserve structure
    # text = re.sub(r'#+\s*', '', text)
    text = re.sub(r'\*\*(.*?)\*\*', r'\1', text)
    text = re.sub(r'\*(.*?)\*', r'\1', text)
    text = re.sub(r'`(.*?)`', r'\1', text)
    text = re.sub(r'\[(.*?)\]\(.*?\)', r'\1', text)

    # # Remove code blocks but preserve content
    # text = re.sub(r'```.*?```', '', text, flags=re.DOTALL)

    # Preserve spacing
    # text = re.sub(r'\n{3,}', '\n\n', text)
    # text = re.sub(r'[ \t]+', ' ', text)
    # text = re.sub(r'\n +', '\n', text)
    # text = re.sub(r' +\n', '\n', text)

    # Final cleanup (preserve #)
    # text = re.sub(r'[^\w\s\.\,\!\?\-\:\;\(\)\n\r\t\@\&\+\=\[\]\{\}\|\~\`\'\"\<\>\/\\\#]', '', text)

    return text.strip()


# def extract_hashtags_from_output(summary_output: VideoSummaryGeneratorOutput) -> str:
    """
    Returns the hashtags exactly as received from the agent.
    """
    # return summary_output.topics_as_hastages.strip()
def convert_to_youtube_description(summary_output: VideoSummaryGeneratorOutput, custom_template_for_youtube_description: str, max_length: int = 4900) -> str:
    """
    Convert VideoSummaryGeneratorOutput to YouTube-compatible description format.
    """
    description_parts = []
    
    # Add keywords at the beginning for better SEO (as YouTube suggests)
    if summary_output.keywords:
        keywords = " ".join(summary_output.keywords)
        description_parts.append(keywords)
        description_parts.append("")
    
    description_parts.extend([])

    if summary_output.summary_of_the_video:
        description_parts.append("📚 VIDEO SUMMARY")
        description_parts.append("=" * 50)
        description_parts.append(summary_output.summary_of_the_video)
        description_parts.append("")

    description_parts.append(custom_template_for_youtube_description)

    # Add hashtags section
    if summary_output.topics_as_hastages:
        description_parts.append("🏷️ TAGS")
        description_parts.append("=" * 50)
        hashtags = " ".join(summary_output.topics_as_hastages)
        description_parts.append(hashtags)

    # Join description before cleaning
    full_description = "\n".join(description_parts)
    
    # Clean the main description
    final_output = clean_text_for_youtube(full_description)

    return final_output[:max_length]


async def video_summary_generator_agent(transcript , custom_template_for_youtube_description,api_key):
    """
    Generate a video summary and convert it to YouTube description format.
    """

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
        name="Youbtube Video Summarizer",
        instructions=f"""
        
        You are an expert in summarizing YouTube videos based on their transcript. 
        Your job is to give a detailed summary of the topics taught in the video using your own knowledge. 
        Add attractive explanations, make it easy to understand, and include examples for each topic. 


    """
        ,

        output_type=VideoSummaryGeneratorOutput,
        model=model,
        model_settings=ModelSettings(
            max_tokens=10000,
            temperature=0.7,
            top_p=1,
            frequency_penalty=0.5,
        )
    )


    result = await Runner.run(
        agent,
        input=f"""Generate a short summary for the following transcript of a YouTube video: {transcript} in {500} words""",
    )


    output = result.final_output

    youtube_description = convert_to_youtube_description(output , custom_template_for_youtube_description)


    return youtube_description

