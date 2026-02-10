"""
Application Configuration
"""
from pydantic_settings import BaseSettings
from functools import lru_cache


class Settings(BaseSettings):
    """Application settings loaded from environment variables"""
    
    # Application
    APP_NAME: str = "Azure Resources Tracker"
    APP_VERSION: str = "1.0.0"
    API_HOST: str = "0.0.0.0"
    API_PORT: int = 8000
    DEBUG: bool = False
    
    # Azure Configuration
    AZURE_SUBSCRIPTION_ID: str
    AZURE_TENANT_ID: str
    AZURE_CLIENT_ID: str
    AZURE_CLIENT_SECRET: str
    AZURE_DEFAULT_LOCATION: str = "eastus"
    AZURE_DEFAULT_TAGS: dict = {
        "ManagedBy": "AzureResourcesTracker",
        "AutoCreated": "true"
    }
    
    # GitHub Configuration
    GITHUB_TOKEN: str
    GITHUB_ORG: str
    GITHUB_DEFAULT_BRANCH: str = "main"
    GITHUB_AUTO_INIT: bool = True
    GITHUB_PRIVATE: bool = False
    
    # SharePoint Configuration
    SHAREPOINT_SITE_URL: str
    SHAREPOINT_LIST_NAME: str = "ResourceRequests"
    SHAREPOINT_CLIENT_ID: str
    SHAREPOINT_CLIENT_SECRET: str
    
    # Webhook Configuration
    WEBHOOK_SECRET: str
    WEBHOOK_VALIDATION_TIMEOUT: int = 5
    
    # Database (Optional - for tracking)
    DATABASE_URL: str = "sqlite:///./azure_tracker.db"
    
    # Redis (Optional - for Celery)
    REDIS_URL: str = "redis://localhost:6379/0"
    
    # Security
    SECRET_KEY: str = "change-this-secret-key-in-production"
    ALGORITHM: str = "HS256"
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 30
    
    # Logging
    LOG_LEVEL: str = "INFO"
    LOG_FORMAT: str = "json"
    
    class Config:
        env_file = ".env"
        case_sensitive = True


@lru_cache()
def get_settings() -> Settings:
    """Get cached settings instance"""
    return Settings()
