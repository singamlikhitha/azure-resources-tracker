"""
Resources Router
"""
from fastapi import APIRouter, HTTPException, BackgroundTasks
from fastapi.responses import JSONResponse, Response
from typing import List, Optional
import structlog
from datetime import datetime
import json

from app.models import (
    ResourceCreationRequest,
    ResourceCreationResponse,
    SharePointEntry,
    ResourceStatus,
    AzureResourceGroup,
    CloudPlatform,
    ResourceType
)
from app.services import AzureService, GitHubService, SharePointService
# Optional cloud service imports
try:
    from app.services.gcp_service import GCPService
    GCP_AVAILABLE = True
except ImportError:
    GCP_AVAILABLE = False
    
try:
    from app.services.aws_service import AWSService
    AWS_AVAILABLE = True
except ImportError:
    AWS_AVAILABLE = False
    
from app.config import get_settings

router = APIRouter()
logger = structlog.get_logger()
settings = get_settings()


@router.get("/test_snake_case")
async def test_snake_case():
    """Test endpoint to verify snake_case JSON serialization"""
    test_data = {
        "user_name": "TestUser",
        "resource_group_name": "test-rg",
        "date_of_creation": "2026-02-23T00:00:00",
        "project_name": "Test Project"
    }
    return Response(content=json.dumps(test_data), media_type="application/json")


@router.get("/resources")
async def list_resources():
    """
    List all resource creation entries
    
    Returns SharePoint list items if enabled, otherwise returns Azure resource groups as entries
    """
    if not settings.SHAREPOINT_ENABLED or not settings.SHAREPOINT_SITE_URL:
        logger.info("sharepoint_disabled_returning_azure_resource_groups")
        # Return Azure resource groups as SharePoint-like entries
        try:
            azure_service = AzureService()
            resource_groups = await azure_service.list_resource_groups()
            
            logger.info("fetched_azure_resource_groups", count=len(resource_groups))
            
            # Build response dict directly without Pydantic models
            data = []
            for rg in resource_groups:
                user_name = rg.tags.get("CreatedBy", "Created outside app") if rg.tags else "Created outside app"
                project_name = rg.tags.get("ProjectName", rg.name) if rg.tags else rg.name
                
                # Parse date from tags
                date_of_creation = None
                if rg.tags and "CreatedAt" in rg.tags:
                    date_of_creation = rg.tags["CreatedAt"]
                
                # Construct dict directly with snake_case keys - NO PYDANTIC
                data.append({
                    "id": rg.id,
                    "user_name": user_name,
                    "resource_group_name": rg.name,
                    "date_of_creation": date_of_creation,
                    "project_name": project_name,
                    "status": "Completed",
                    "azure_resource_group_id": rg.id,
                    "github_repo_url": None,
                    "error_message": None
                })

            logger.info("returned_azure_resource_groups_as_entries", count=len(data))
            # Log first entry to verify snake_case
            if data:
                logger.info("first_entry", entry=data[0])
            # Use Response with explicit json.dumps to bypass any Pydantic serialization
            json_content = json.dumps(data)
            logger.info("json_content_preview", preview=json_content[:500] if len(json_content) > 500 else json_content)
            return Response(content=json_content, media_type="application/json")
        except Exception as e:
            logger.error("list_azure_resource_groups_failed", error=str(e))
            return []
    
    try:
        sharepoint_service = SharePointService()
        
        # Get all items (not just pending)
        list_obj = sharepoint_service.ctx.web.lists.get_by_title(
            sharepoint_service.list_name
        )
        items = list_obj.items.get().execute_query()
        
        entries = []
        for item in items:
            try:
                entry = sharepoint_service._item_to_entry(item)
                entries.append(entry)
            except Exception as e:
                logger.warning(
                    "failed_to_parse_item",
                    item_id=item.properties.get("ID"),
                    error=str(e)
                )
        
        # Manually construct response to ensure snake_case field names
        data = [
            {
                "id": entry.id,
                "user_name": entry.user_name,
                "resource_group_name": entry.resource_group_name,
                "date_of_creation": entry.date_of_creation.isoformat() if entry.date_of_creation else None,
                "project_name": entry.project_name,
                "status": entry.status,
                "azure_resource_group_id": entry.azure_resource_group_id,
                "github_repo_url": entry.github_repo_url,
                "error_message": entry.error_message
            }
            for entry in entries
        ]
        # Use Response with explicit json.dumps to bypass any Pydantic serialization
        return Response(content=json.dumps(data), media_type="application/json")
        
    except Exception as e:
        logger.error("list_resources_failed", error=str(e))
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/resources/subscriptions")
async def list_subscriptions():
    """
    List all Azure subscriptions accessible by the service principal
    
    Returns a list of subscriptions with their IDs, names, and states
    """
    try:
        azure_service = AzureService()
        subscriptions = await azure_service.list_subscriptions()
        
        logger.info("listed_subscriptions", count=len(subscriptions))
        return subscriptions
        
    except Exception as e:
        logger.error("list_subscriptions_failed", error=str(e))
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/resources/create", response_model=ResourceCreationResponse)
async def create_resources(
    request: ResourceCreationRequest,
    background_tasks: BackgroundTasks
):
    """
    Create cloud resources (Azure/GCP/AWS) and optionally GitHub repository
    
    Creates resources directly. If SharePoint is enabled, also creates an entry there.
    """
    try:
        logger.info("manual_resource_creation_requested", 
                   platform=request.cloud_platform, 
                   resource_type=request.resource_type,
                   request=request.dict())
        
        item_id: Optional[str] = None
        resource_id = None
        github_repo_url = None
        error_message = None
        status = ResourceStatus.COMPLETED
        
        # Optionally create SharePoint entry
        if settings.SHAREPOINT_ENABLED and settings.SHAREPOINT_SITE_URL:
            try:
                sharepoint_service = SharePointService()
                entry = SharePointEntry(
                    user_name=request.user_name,
                    cloud_platform=request.cloud_platform,
                    resource_type=request.resource_type,
                    resource_group_name=request.resource_group_name,
                    project_name=request.project_name,
                    status=ResourceStatus.IN_PROGRESS
                )
                item_id = await sharepoint_service.create_item(entry)
                logger.info("sharepoint_entry_created", item_id=item_id)
            except Exception as sp_error:
                logger.warning("sharepoint_entry_creation_failed", error=str(sp_error))
                # Continue without SharePoint
        
        try:
            creation_time = datetime.utcnow()
            
            # Route to appropriate cloud service based on platform
            if request.cloud_platform == CloudPlatform.AZURE:
                azure_service = AzureService()
                tags = {
                    "ProjectName": request.project_name,
                    "CreatedBy": request.user_name,
                    "CreatedAt": creation_time.isoformat(),
                    **request.tags
                } if request.tags else {
                    "ProjectName": request.project_name,
                    "CreatedBy": request.user_name,
                    "CreatedAt": creation_time.isoformat()
                }
                
                logger.info("creating_azure_resource_group", name=request.resource_group_name)
                rg = await azure_service.create_resource_group(
                    resource_group_name=request.resource_group_name,
                    location=request.location or "eastus",
                    tags=tags,
                    subscription_id=request.subscription_id
                )
                resource_id = rg.id
                logger.info("azure_resource_group_created", id=resource_id)
                
            elif request.cloud_platform == CloudPlatform.GCP:
                if not GCP_AVAILABLE:
                    raise HTTPException(status_code=501, detail="GCP support not available. Install google-cloud-resourcemanager.")
                gcp_service = GCPService()
                logger.info("creating_gcp_project", project_id=request.resource_group_name)
                labels = {
                    "project-name": request.project_name.lower().replace(" ", "-"),
                    "created-by": request.user_name.lower().replace(" ", "-")
                }
                project = await gcp_service.create_project(
                    project_id=request.resource_group_name,
                    display_name=request.project_name,
                    labels=labels
                )
                resource_id = project["project_id"]
                logger.info("gcp_project_created", project_id=resource_id)
                
            elif request.cloud_platform == CloudPlatform.AWS:
                if not AWS_AVAILABLE:
                    raise HTTPException(status_code=501, detail="AWS support not available. Install boto3.")
                aws_service = AWSService()
                logger.info("creating_aws_account", account_name=request.project_name)
                # For AWS, we need an email address - could be derived from user or passed in
                email = request.tags.get("email") if request.tags else f"{request.user_name.lower().replace(' ', '.')}@example.com"  
                account = await aws_service.create_account(
                    account_name=request.project_name,
                    email=email,
                    tags=[{"Key": "CreatedBy", "Value": request.user_name}] if request.tags is None else [
                        {"Key": k, "Value": v} for k, v in request.tags.items()
                    ]
                )
                resource_id = account.get("account_id") or account["request_id"]
                logger.info("aws_account_created", account_id=resource_id)
            
            # Create GitHub Repository if requested
            if request.create_github_repo:
                github_service = GitHubService()
                logger.info("creating_github_repository", name=request.resource_group_name)
                repo = await github_service.create_repository(
                    repo_name=request.resource_group_name,
                    description=f"{request.project_name} ({request.cloud_platform.value}) - Created for {request.user_name}"
                )
                github_repo_url = repo.html_url
                logger.info("github_repository_created", url=github_repo_url)
            
        except Exception as e:
            error_message = str(e)
            status = ResourceStatus.FAILED
            logger.error("resource_creation_failed", error=error_message)
        
        # Update SharePoint entry if it was created
        if item_id and settings.SHAREPOINT_ENABLED:
            try:
                sharepoint_service = SharePointService()
                await sharepoint_service.update_item_status(
                    item_id,
                    status,
                    resource_id=resource_id,
                    github_repo_url=github_repo_url,
                    error_message=error_message
                )
            except Exception as sp_error:
                logger.warning("sharepoint_update_failed", error=str(sp_error))
        
        return ResourceCreationResponse(
            status=status,
            resource_group_id=resource_id,
            resource_group_name=request.resource_group_name if resource_id else None,
            github_repo_url=github_repo_url,
            sharepoint_item_id=item_id,
            message="Resources created successfully" if status == ResourceStatus.COMPLETED 
                    else f"Failed: {error_message}",
            created_at=datetime.utcnow().isoformat()
        )
    except Exception as e:
        logger.error("create_resources_failed", error=str(e))
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/resources/cloud-platforms")
async def list_cloud_platforms():
    """
    List available cloud platforms
    """
    return [
        {"value": CloudPlatform.AZURE, "label": "Azure"},
        {"value": CloudPlatform.GCP, "label": "Google Cloud Platform"},
        {"value": CloudPlatform.AWS, "label": "Amazon Web Services"}
    ]


@router.get("/resources/resource-types")
async def list_resource_types(cloud_platform: Optional[str] = None):
    """
    List available resource types, optionally filtered by cloud platform
    """
    resource_types_map = {
        CloudPlatform.AZURE: [
            {"value": ResourceType.AZURE_RESOURCE_GROUP, "label": "Resource Group"}
        ],
        CloudPlatform.GCP: [
            {"value": ResourceType.GCP_PROJECT, "label": "Project"}
        ],
        CloudPlatform.AWS: [
            {"value": ResourceType.AWS_ACCOUNT, "label": "Account"}
        ]
    }
    
    if cloud_platform:
        return resource_types_map.get(CloudPlatform(cloud_platform), [])
    
    # Return all resource types
    all_types = []
    for types in resource_types_map.values():
        all_types.extend(types)
    return all_types


@router.get("/resources/azure/resource-groups", response_model=List[AzureResourceGroup])
async def list_azure_resource_groups():
    """
    List all Azure Resource Groups in the subscription
    """
    try:
        azure_service = AzureService()
        resource_groups = await azure_service.list_resource_groups()
        
        return resource_groups
        
    except Exception as e:
        logger.error("list_azure_resource_groups_failed", error=str(e))
        raise HTTPException(status_code=500, detail=str(e))


# Catch-all route - MUST BE LAST to avoid intercepting specific routes
@router.get("/{item_id}", response_model=SharePointEntry)
async def get_resource(item_id: str):
    """
    Get a specific resource entry
    
    Args:
        item_id: SharePoint list item ID
    """
    if not settings.SHAREPOINT_ENABLED or not settings.SHAREPOINT_SITE_URL:
        raise HTTPException(status_code=501, detail="SharePoint is not configured")
    
    try:
        sharepoint_service = SharePointService()
        entry = await sharepoint_service.get_item_by_id(item_id)
        
        if not entry:
            raise HTTPException(status_code=404, detail="Resource not found")
        
        return entry
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error("get_resource_failed", item_id=item_id, error=str(e))
        raise HTTPException(status_code=500, detail=str(e))
