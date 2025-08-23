from pydantic_settings import BaseSettings
from dotenv import load_dotenv
import os
load_dotenv()

class Settings(BaseSettings):
    DATABASE_URL: str = os.getenv("DATABASE_URL")
    SECRET_KEY: str = os.getenv("SECRET_KEY", "your-secret-key-change-in-production")

    # Other settings
    PORT: int = os.getenv("PORT")

    # GEMINI API KEY
    GEMINI_API_KEY: str = os.getenv("GEMINI_API_KEY")
    
    class Config:
        env_file = ".env"

settings = Settings() 