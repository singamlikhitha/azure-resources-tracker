"""
Resources Router
"""
from fastapi import APIRouter, HTTPException, BackgroundTasks
from typing import List
import structlog

from app.models import (
    ResourceCreationRequest,
    ResourceCreationResponse,
    SharePointEntry,
    ResourceStatus,
    AzureResourceGroup
)
from app.services import AzureService, GitHubService, SharePointService

router = APIRouter()
logger = structlog.get_logger()


@router.get("/", response_model=List[SharePointEntry])
async def list_resources():
    """
    List all resource creation entries
    
    Returns all SharePoint list items
    """
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
        
        return entries
        
    except Exception as e:
        logger.error("list_resources_failed", error=str(e))
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/{item_id}", response_model=SharePointEntry)
async def get_resource(item_id: str):
    """
    Get a specific resource entry
    
    Args:
        item_id: SharePoint list item ID
    """
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


@router.post("/create", response_model=ResourceCreationResponse)
async def create_resources(
    request: ResourceCreationRequest,
    background_tasks: BackgroundTasks
):
    """
    Manually create Azure Resource Group and GitHub repository
    
    This endpoint creates resources immediately and adds entry to SharePoint
    """
    try:
        logger.info("manual_resource_creation_requested", request=request.dict())
        
        # Initialize services
        azure_service = AzureService()
        github_service = GitHubService()
        sharepoint_service = SharePointService()
        
        # Create SharePoint entry first
        entry = SharePointEntry(
            user_name=request.user_name,
            resource_group_name=request.resource_group_name,
            project_name=request.project_name,
            status=ResourceStatus.IN_PROGRESS
        )
        
        item_id = await sharepoint_service.create_item(entry)
        
        if not item_id:
            raise HTTPException(
                status_code=500,
                detail="Failed to create SharePoint entry"
            )
        
        azure_rg_id = None
        github_repo_url = None
        error_message = None
        status = ResourceStatus.COMPLETED
        
        try:
            # Merge tags
            tags = {
                "ProjectName": request.project_name,
                "CreatedBy": request.user_name,
                **request.tags
            } if request.tags else {
                "ProjectName": request.project_name,
                "CreatedBy": request.user_name
            }
            
            # Create Azure Resource Group
            rg = await azure_service.create_resource_group(
                resource_group_name=request.resource_group_name,
                location=request.location,
                tags=tags
            )
            azure_rg_id = rg.id
            
            # Create GitHub Repository if requested
            if request.create_github_repo:
                repo = await github_service.create_repository(
                    repo_name=request.resource_group_name,
                    description=f"{request.project_name} - Created for {request.user_name}"
                )
                github_repo_url = repo.html_url
            
        except Exception as e:
            error_message = str(e)
            status = ResourceStatus.FAILED
            logger.error("resource_creation_failed", error=error_message)
        
        # Update SharePoint entry
        await sharepoint_service.update_item_status(
            item_id,
            status,
            azure_rg_id=azure_rg_id,
            github_repo_url=github_repo_url,
            error_message=error_message
        )
        
        return ResourceCreationResponse(
            status=status,
            resource_group_id=azure_rg_id,
            resource_group_name=request.resource_group_name if azure_rg_id else None,
            github_repo_url=github_repo_url,
            sharepoint_item_id=item_id,
            message="Resources created successfully" if status == ResourceStatus.COMPLETED 
                    else f"Failed: {error_message}"
        )
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error("create_resources_failed", error=str(e))
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/azure/resource-groups", response_model=List[AzureResourceGroup])
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
