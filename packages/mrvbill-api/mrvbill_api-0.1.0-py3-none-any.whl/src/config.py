from pydantic_settings import BaseSettings
from functools import lru_cache
from typing import Optional

class Settings(BaseSettings):
    # MongoDB settings
    MONGODB_URL: str
    MONGODB_DB_NAME: str = "mrvbill"
    
    # API settings
    API_VERSION: str = "1.0.0"
    DEBUG: bool = False
    
    # Auth0 settings
    AUTH0_DOMAIN: str
    AUTH0_API_AUDIENCE: str
    AUTH0_ALGORITHMS: list[str] = ["RS256"]
    
    # Add other environment variables here
    # Example:
    # AWS_REGION: str = "us-east-1"
    # JWT_SECRET: str
    
    class Config:
        env_file = ".env"
        case_sensitive = True

@lru_cache()
def get_settings() -> Settings:
    return Settings()
