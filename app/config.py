import os
from dotenv import load_dotenv
from pydantic_settings import BaseSettings

# Load environment variables from .env file
load_dotenv()

# Database configuration
DATABASE_URL = os.getenv("DATABASE_URL", "postgresql://postgres:postgres@localhost:5432/school_journal")

# Security settings
SECRET_KEY = os.getenv("SECRET_KEY", "your-super-secret-key-change-this-in-production")
ALGORITHM = os.getenv("ALGORITHM", "HS256")
ACCESS_TOKEN_EXPIRE_MINUTES = int(os.getenv("ACCESS_TOKEN_EXPIRE_MINUTES", "1440"))  # 24 hours by default

# Server settings
HOST = os.getenv("HOST", "0.0.0.0")
PORT = int(os.getenv("PORT", "8000"))
DEBUG = os.getenv("DEBUG", "True").lower() == "true"
RELOAD = os.getenv("RELOAD", "True").lower() == "true"

# API settings
API_PREFIX = "/api/v1"

# File uploads
UPLOAD_DIRECTORY = os.getenv("UPLOAD_DIRECTORY", "./uploads")
MAX_UPLOAD_SIZE_MB = int(os.getenv("MAX_UPLOAD_SIZE_MB", "5"))
MAX_CONTENT_LENGTH = MAX_UPLOAD_SIZE_MB * 1024 * 1024  # Convert MB to bytes

# Allowed file extensions
ALLOWED_EXTENSIONS = {
    "image": ["jpg", "jpeg", "png", "gif"],
    "document": ["pdf", "doc", "docx", "txt"],
    "video": ["mp4", "mov", "avi"],
    "audio": ["mp3", "wav"],
}

# Feature flags
ENABLE_GRAPHQL = os.getenv("ENABLE_GRAPHQL", "True").lower() == "true"
ENABLE_FILE_UPLOADS = os.getenv("ENABLE_FILE_UPLOADS", "True").lower() == "true"

# Email settings (commented out until needed)
# SMTP_SERVER = os.getenv("SMTP_SERVER")
# SMTP_PORT = int(os.getenv("SMTP_PORT", "587"))
# SMTP_USERNAME = os.getenv("SMTP_USERNAME")
# SMTP_PASSWORD = os.getenv("SMTP_PASSWORD")
# SMTP_FROM_EMAIL = os.getenv("SMTP_FROM_EMAIL", "noreply@schooljournal.com")

# Class-based settings for validation (optional)
class Settings(BaseSettings):
    """Application settings with validation."""

    # Database
    database_url: str = DATABASE_URL

    # Security
    secret_key: str = SECRET_KEY
    algorithm: str = ALGORITHM
    access_token_expire_minutes: int = ACCESS_TOKEN_EXPIRE_MINUTES

    # Server
    host: str = HOST
    port: int = PORT
    debug: bool = DEBUG
    reload: bool = RELOAD

    # Features
    enable_graphql: bool = ENABLE_GRAPHQL
    enable_file_uploads: bool = ENABLE_FILE_UPLOADS

    class Config:
        env_file = ".env"

# Create settings instance for importing elsewhere
settings = Settings()