from pydantic_settings import BaseSettings
from functools import lru_cache

class Settings(BaseSettings):

    # Database
    DATABASE_URL: str
    
    # Security
    SECRET_KEY: str
    ALGORITHM: str = "HS256"
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 30
    
    class Config:
        env_file = ".env"
        case_sensitive = True

@lru_cache()
def get_settings():
    """
    Create a cached instance of settings
    lru_cache ensures we only load .env once, not on every request
    """
    return Settings()

# Usage: from app.config import get_settings
# settings = get_settings()