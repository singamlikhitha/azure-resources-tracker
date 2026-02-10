"""
SharePoint Webhook Router
"""
from fastapi import APIRouter, Request, HTTPException, BackgroundTasks
from typing import Dict
import structlog
import hashlib
import hmac

from app.models import WebhookPayload, ResourceStatus
from app.config import get_settings
from app.services import AzureService, GitHubService, SharePointService

router = APIRouter()
logger = structlog.get_logger()
settings = get_settings()


def verify_webhook_signature(payload: str, signature: str, secret: str) -> bool:
    """
    Verify webhook signature using HMAC
    
    Args:
        payload: Request payload as string
        signature: Signature from request header
        secret: Webhook secret
        
    Returns:
        True if signature is valid
    """
    expected_signature = hmac.new(
        secret.encode(),
        payload.encode(),
        hashlib.sha256
    ).hexdigest()
    
    return hmac.compare_digest(signature, expected_signature)


async def process_sharepoint_update(item_id: str):
    """
    Background task to process SharePoint list item update
    
    Args:
        item_id: SharePoint list item ID
    """
    try:
        logger.info("processing_sharepoint_update", item_id=item_id)
        
        # Initialize services
        sharepoint_service = SharePointService()
        azure_service = AzureService()
        github_service = GitHubService()
        
        # Get SharePoint item
        entry = await sharepoint_service.get_item_by_id(item_id)
        if not entry:
            logger.error("sharepoint_item_not_found", item_id=item_id)
            return
        
        # Update status to In Progress
        await sharepoint_service.update_item_status(
            item_id,
            ResourceStatus.IN_PROGRESS
        )
        
        azure_rg_id = None
        github_repo_url = None
        error_message = None
        
        try:
            # Create Azure Resource Group
            logger.info(
                "creating_azure_resource_group",
                name=entry.resource_group_name
            )
            
            rg = await azure_service.create_resource_group(
                resource_group_name=entry.resource_group_name,
                tags={
                    "ProjectName": entry.project_name,
                    "CreatedBy": entry.user_name,
                    "CreatedAt": entry.date_of_creation.isoformat()
                }
            )
            azure_rg_id = rg.id
            
            # Create GitHub Repository
            logger.info(
                "creating_github_repository",
                name=entry.resource_group_name
            )
            
            repo = await github_service.create_repository(
                repo_name=entry.resource_group_name,
                description=f"{entry.project_name} - Created for {entry.user_name}",
                auto_init=True
            )
            github_repo_url = repo.html_url
            
            # Update SharePoint with success
            await sharepoint_service.update_item_status(
                item_id,
                ResourceStatus.COMPLETED,
                azure_rg_id=azure_rg_id,
                github_repo_url=github_repo_url
            )
            
            logger.info(
                "sharepoint_update_processed_successfully",
                item_id=item_id,
                azure_rg_id=azure_rg_id,
                github_repo_url=github_repo_url
            )
            
        except Exception as e:
            error_message = str(e)
            logger.error(
                "resource_creation_failed",
                item_id=item_id,
                error=error_message
            )
            
            # Update SharePoint with failure
            await sharepoint_service.update_item_status(
                item_id,
                ResourceStatus.FAILED,
                error_message=error_message
            )
            
    except Exception as e:
        logger.error(
            "process_sharepoint_update_failed",
            item_id=item_id,
            error=str(e)
        )


@router.post("/sharepoint")
async def sharepoint_webhook(
    request: Request,
    background_tasks: BackgroundTasks
) -> Dict[str, str]:
    """
    SharePoint webhook endpoint
    
    Receives notifications when SharePoint list is updated
    """
    try:
        # Get request body
        body = await request.body()
        body_str = body.decode()
        
        # Verify webhook signature if present
        signature = request.headers.get("X-SharePoint-Signature")
        if signature:
            if not verify_webhook_signature(
                body_str,
                signature,
                settings.WEBHOOK_SECRET
            ):
                raise HTTPException(status_code=401, detail="Invalid signature")
        
        # Parse webhook payload
        payload = await request.json()
        
        logger.info("webhook_received", payload=payload)
        
        # Handle validation request
        if "validationToken" in payload:
            logger.info("webhook_validation_request")
            return {"validationToken": payload["validationToken"]}
        
        # Process webhook notification
        webhook_data = WebhookPayload(**payload)
        
        # Get changed items (simplified - in production, use change log)
        sharepoint_service = SharePointService()
        pending_items = await sharepoint_service.get_pending_items()
        
        # Process each pending item in background
        for item in pending_items:
            if item.id:
                background_tasks.add_task(
                    process_sharepoint_update,
                    item.id
                )
        
        return {"status": "accepted", "items_queued": len(pending_items)}
        
    except Exception as e:
        logger.error("webhook_processing_failed", error=str(e))
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/sharepoint/manual-trigger/{item_id}")
async def manual_trigger(
    item_id: str,
    background_tasks: BackgroundTasks
):
    """
    Manually trigger processing of a SharePoint item
    
    Args:
        item_id: SharePoint list item ID
    """
    background_tasks.add_task(process_sharepoint_update, item_id)
    
    return {
        "status": "queued",
        "item_id": item_id,
        "message": "Processing started in background"
    }
