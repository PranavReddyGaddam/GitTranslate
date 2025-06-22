# utils/config.py
import os
from dotenv import load_dotenv
from pydantic_settings import BaseSettings

# Load variables from .env file (for local development)
load_dotenv()

class Settings(BaseSettings):
    """Application settings loaded from environment variables."""
    ORKES_BASE_URL: str = "https://your-orkes-instance.com"
    ORKES_API_KEY: str = "your-orkes-api-key-here"
    DEBUG: bool = False
    
    class Config:
        env_file = ".env"
        case_sensitive = True

# Create settings instance
settings = Settings()

# Note: Validation will happen when the settings are actually used
# This allows the app to start even without proper environment variables
