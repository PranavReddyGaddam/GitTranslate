# utils/config.py
import os
from dotenv import load_dotenv
from pydantic_settings import BaseSettings

# Load variables from .env file (for local development)
load_dotenv()

class Settings(BaseSettings):
    """Application settings loaded from environment variables."""
    ORKES_BASE_URL: str = "https://developer.orkescloud.com/api/"
    ORKES_KEY_ID: str = "47hs2be26735-4ee7-11f0-a795-d685533af8e3"
    ORKES_KEY_SECRET: str = "kosQVUbCtvFarR8AmaG8RWomGLtm67ulTJWMUlLZIxoMkEXk"
    DEBUG: bool = False
    
    class Config:
        env_file = ".env"
        case_sensitive = True

# Create settings instance
settings = Settings()

# Note: Validation will happen when the settings are actually used
# This allows the app to start even without proper environment variables
