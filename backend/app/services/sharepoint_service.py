"""
SharePoint Integration Service
"""
from office365.runtime.auth.client_credential import ClientCredential
from office365.sharepoint.client_context import ClientContext
from office365.sharepoint.listitems.listitem import ListItem
import structlog
from typing import Optional, List
from datetime import datetime

from app.config import get_settings
from app.models import SharePointEntry, ResourceStatus

logger = structlog.get_logger()
settings = get_settings()


class SharePointService:
    """Service for SharePoint list management"""
    
    def __init__(self):
        """Initialize SharePoint service with credentials"""
        self.site_url = settings.SHAREPOINT_SITE_URL
        self.list_name = settings.SHAREPOINT_LIST_NAME
        
        credentials = ClientCredential(
            settings.SHAREPOINT_CLIENT_ID,
            settings.SHAREPOINT_CLIENT_SECRET
        )
        
        self.ctx = ClientContext(self.site_url).with_credentials(credentials)
    
    async def get_pending_items(self) -> List[SharePointEntry]:
        """
        Get all pending items from SharePoint list
        
        Returns:
            List of SharePointEntry models with status=PENDING
        """
        try:
            list_obj = self.ctx.web.lists.get_by_title(self.list_name)
            
            # Query for pending items
            items = list_obj.items.filter("Status eq 'Pending'").get().execute_query()
            
            entries = []
            for item in items:
                try:
                    entry = self._item_to_entry(item)
                    entries.append(entry)
                except Exception as e:
                    logger.warning(
                        "failed_to_parse_item",
                        item_id=item.properties.get("ID"),
                        error=str(e)
                    )
            
            logger.info("retrieved_pending_items", count=len(entries))
            return entries
            
        except Exception as e:
            logger.error("get_pending_items_failed", error=str(e))
            return []
    
    async def get_item_by_id(self, item_id: str) -> Optional[SharePointEntry]:
        """
        Get a specific item from SharePoint list
        
        Args:
            item_id: SharePoint list item ID
            
        Returns:
            SharePointEntry model or None if not found
        """
        try:
            list_obj = self.ctx.web.lists.get_by_title(self.list_name)
            item = list_obj.items.get_by_id(item_id).get().execute_query()
            
            return self._item_to_entry(item)
            
        except Exception as e:
            logger.error(
                "get_item_by_id_failed",
                item_id=item_id,
                error=str(e)
            )
            return None
    
    async def update_item_status(
        self,
        item_id: str,
        status: ResourceStatus,
        azure_rg_id: Optional[str] = None,
        github_repo_url: Optional[str] = None,
        error_message: Optional[str] = None
    ) -> bool:
        """
        Update SharePoint list item with creation results
        
        Args:
            item_id: SharePoint list item ID
            status: New status
            azure_rg_id: Azure resource group ID (optional)
            github_repo_url: GitHub repository URL (optional)
            error_message: Error message if failed (optional)
            
        Returns:
            True if updated successfully
        """
        try:
            list_obj = self.ctx.web.lists.get_by_title(self.list_name)
            item = list_obj.items.get_by_id(item_id)
            
            update_data = {
                "Status": status.value
            }
            
            if azure_rg_id:
                update_data["AzureResourceGroupId"] = azure_rg_id
            
            if github_repo_url:
                update_data["GitHubRepoUrl"] = github_repo_url
            
            if error_message:
                update_data["ErrorMessage"] = error_message
            
            item.update(update_data).execute_query()
            
            logger.info(
                "sharepoint_item_updated",
                item_id=item_id,
                status=status.value
            )
            return True
            
        except Exception as e:
            logger.error(
                "update_item_status_failed",
                item_id=item_id,
                error=str(e)
            )
            return False
    
    async def create_item(self, entry: SharePointEntry) -> Optional[str]:
        """
        Create a new item in SharePoint list
        
        Args:
            entry: SharePointEntry model
            
        Returns:
            Item ID if created successfully, None otherwise
        """
        try:
            list_obj = self.ctx.web.lists.get_by_title(self.list_name)
            
            item_data = {
                "Title": entry.project_name,
                "UserName": entry.user_name,
                "ResourceGroupName": entry.resource_group_name,
                "ProjectName": entry.project_name,
                "DateOfCreation": entry.date_of_creation.isoformat(),
                "Status": entry.status.value
            }
            
            item = list_obj.add_item(item_data).execute_query()
            
            item_id = str(item.properties["ID"])
            logger.info("sharepoint_item_created", item_id=item_id)
            
            return item_id
            
        except Exception as e:
            logger.error("create_item_failed", error=str(e))
            return None
    
    def _item_to_entry(self, item: ListItem) -> SharePointEntry:
        """
        Convert SharePoint list item to SharePointEntry model
        
        Args:
            item: SharePoint list item
            
        Returns:
            SharePointEntry model
        """
        props = item.properties
        
        # Parse datetime
        date_str = props.get("DateOfCreation")
        date_of_creation = (
            datetime.fromisoformat(date_str.replace("Z", "+00:00"))
            if date_str
            else datetime.utcnow()
        )
        
        return SharePointEntry(
            id=str(props.get("ID")),
            user_name=props.get("UserName", ""),
            resource_group_name=props.get("ResourceGroupName", ""),
            project_name=props.get("ProjectName", ""),
            date_of_creation=date_of_creation,
            status=ResourceStatus(props.get("Status", "Pending")),
            azure_resource_group_id=props.get("AzureResourceGroupId"),
            github_repo_url=props.get("GitHubRepoUrl"),
            error_message=props.get("ErrorMessage")
        )
