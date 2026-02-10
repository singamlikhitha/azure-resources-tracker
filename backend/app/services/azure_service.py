"""
Azure Resource Management Service
"""
from azure.identity import ClientSecretCredential
from azure.mgmt.resource import ResourceManagementClient
from azure.core.exceptions import AzureError
import structlog
from typing import Optional

from app.config import get_settings
from app.models import AzureResourceGroup

logger = structlog.get_logger()
settings = get_settings()


class AzureService:
    """Service for Azure Resource Group management"""
    
    def __init__(self):
        """Initialize Azure service with credentials"""
        self.credential = ClientSecretCredential(
            tenant_id=settings.AZURE_TENANT_ID,
            client_id=settings.AZURE_CLIENT_ID,
            client_secret=settings.AZURE_CLIENT_SECRET
        )
        
        self.resource_client = ResourceManagementClient(
            credential=self.credential,
            subscription_id=settings.AZURE_SUBSCRIPTION_ID
        )
    
    async def create_resource_group(
        self,
        resource_group_name: str,
        location: Optional[str] = None,
        tags: Optional[dict] = None
    ) -> AzureResourceGroup:
        """
        Create an Azure Resource Group
        
        Args:
            resource_group_name: Name of the resource group
            location: Azure region (defaults to settings)
            tags: Additional tags (merged with default tags)
            
        Returns:
            AzureResourceGroup model
            
        Raises:
            AzureError: If creation fails
        """
        try:
            location = location or settings.AZURE_DEFAULT_LOCATION
            
            # Merge tags with defaults
            merged_tags = {**settings.AZURE_DEFAULT_TAGS}
            if tags:
                merged_tags.update(tags)
            
            logger.info(
                "creating_resource_group",
                name=resource_group_name,
                location=location,
                tags=merged_tags
            )
            
            # Create resource group
            rg_result = self.resource_client.resource_groups.create_or_update(
                resource_group_name,
                {
                    "location": location,
                    "tags": merged_tags
                }
            )
            
            logger.info(
                "resource_group_created",
                id=rg_result.id,
                name=rg_result.name,
                state=rg_result.properties.provisioning_state
            )
            
            return AzureResourceGroup(
                id=rg_result.id,
                name=rg_result.name,
                location=rg_result.location,
                tags=rg_result.tags or {},
                provisioning_state=rg_result.properties.provisioning_state
            )
            
        except AzureError as e:
            logger.error(
                "resource_group_creation_failed",
                name=resource_group_name,
                error=str(e)
            )
            raise
    
    async def get_resource_group(self, resource_group_name: str) -> Optional[AzureResourceGroup]:
        """
        Get an existing resource group
        
        Args:
            resource_group_name: Name of the resource group
            
        Returns:
            AzureResourceGroup model or None if not found
        """
        try:
            rg = self.resource_client.resource_groups.get(resource_group_name)
            
            return AzureResourceGroup(
                id=rg.id,
                name=rg.name,
                location=rg.location,
                tags=rg.tags or {},
                provisioning_state=rg.properties.provisioning_state
            )
        except AzureError as e:
            logger.warning(
                "resource_group_not_found",
                name=resource_group_name,
                error=str(e)
            )
            return None
    
    async def delete_resource_group(self, resource_group_name: str) -> bool:
        """
        Delete a resource group
        
        Args:
            resource_group_name: Name of the resource group
            
        Returns:
            True if deleted successfully
        """
        try:
            logger.info("deleting_resource_group", name=resource_group_name)
            
            poller = self.resource_client.resource_groups.begin_delete(
                resource_group_name
            )
            poller.result()  # Wait for deletion to complete
            
            logger.info("resource_group_deleted", name=resource_group_name)
            return True
            
        except AzureError as e:
            logger.error(
                "resource_group_deletion_failed",
                name=resource_group_name,
                error=str(e)
            )
            return False
    
    async def list_resource_groups(self) -> list[AzureResourceGroup]:
        """
        List all resource groups in the subscription
        
        Returns:
            List of AzureResourceGroup models
        """
        try:
            resource_groups = []
            
            for rg in self.resource_client.resource_groups.list():
                resource_groups.append(
                    AzureResourceGroup(
                        id=rg.id,
                        name=rg.name,
                        location=rg.location,
                        tags=rg.tags or {},
                        provisioning_state=rg.properties.provisioning_state
                    )
                )
            
            return resource_groups
            
        except AzureError as e:
            logger.error("list_resource_groups_failed", error=str(e))
            return []
