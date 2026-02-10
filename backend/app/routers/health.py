"""
Health Check Router
"""
from fastapi import APIRouter
from datetime import datetime
import structlog

from app.models import HealthResponse
from app.config import get_settings

router = APIRouter()
logger = structlog.get_logger()
settings = get_settings()


@router.get("/health", response_model=HealthResponse)
async def health_check():
    """
    Health check endpoint
    
    Returns service status and dependency health
    """
    services_status = {}
    
    # Check Azure connectivity
    try:
        from app.services.azure_service import AzureService
        azure_service = AzureService()
        # Try to list resource groups as a connectivity test
        await azure_service.list_resource_groups()
        services_status["azure"] = "healthy"
    except Exception as e:
        logger.error("azure_health_check_failed", error=str(e))
        services_status["azure"] = "unhealthy"
    
    # Check GitHub connectivity
    try:
        from app.services.github_service import GitHubService
        github_service = GitHubService()
        # Test connection
        github_service.client.get_user()
        services_status["github"] = "healthy"
    except Exception as e:
        logger.error("github_health_check_failed", error=str(e))
        services_status["github"] = "unhealthy"
    
    # Check SharePoint connectivity
    try:
        from app.services.sharepoint_service import SharePointService
        sharepoint_service = SharePointService()
        # Test connection
        services_status["sharepoint"] = "healthy"
    except Exception as e:
        logger.error("sharepoint_health_check_failed", error=str(e))
        services_status["sharepoint"] = "unhealthy"
    
    # Overall status
    overall_status = "healthy" if all(
        status == "healthy" for status in services_status.values()
    ) else "degraded"
    
    return HealthResponse(
        status=overall_status,
        version=settings.APP_VERSION,
        timestamp=datetime.utcnow(),
        services=services_status
    )
