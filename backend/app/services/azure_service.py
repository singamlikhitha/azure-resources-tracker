"""
Azure Resource Management Service
"""
from azure.identity import ClientSecretCredential
from azure.mgmt.resource import ResourceManagementClient, SubscriptionClient
from azure.core.exceptions import AzureError
import structlog
from typing import Optional, List

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
        
        self.subscription_client = SubscriptionClient(
            credential=self.credential
        )
    
    async def list_subscriptions(self) -> List[dict]:
        """
        List all Azure subscriptions accessible by the service principal
        
        Returns:
            List of subscription dictionaries with id, name, and state
        """
        try:
            logger.info("listing_subscriptions")
            subscriptions = []
            
            for sub in self.subscription_client.subscriptions.list():
                subscriptions.append({
                    "subscription_id": sub.subscription_id,
                    "display_name": sub.display_name,
                    "state": sub.state
                })
            
            logger.info("subscriptions_listed", count=len(subscriptions))
            return subscriptions
            
        except AzureError as e:
            logger.error("list_subscriptions_failed", error=str(e))
            raise
    
    async def create_resource_group(
        self,
        resource_group_name: str,
        location: Optional[str] = None,
        tags: Optional[dict] = None,
        subscription_id: Optional[str] = None
    ) -> AzureResourceGroup:
        """
        Create an Azure Resource Group
        
        Args:
            resource_group_name: Name of the resource group
            location: Azure region (defaults to settings)
            tags: Additional tags (merged with default tags)
            subscription_id: Azure subscription ID (defaults to settings)
            
        Returns:
            AzureResourceGroup model
            
        Raises:
            AzureError: If creation fails
        """
        try:
            location = location or settings.AZURE_DEFAULT_LOCATION
            sub_id = subscription_id or settings.AZURE_SUBSCRIPTION_ID
            
            # Create resource client for specific subscription if different
            if subscription_id and subscription_id != settings.AZURE_SUBSCRIPTION_ID:
                resource_client = ResourceManagementClient(
                    credential=self.credential,
                    subscription_id=subscription_id
                )
            else:
                resource_client = self.resource_client
            
            # Merge tags with defaults
            merged_tags = {**settings.AZURE_DEFAULT_TAGS}
            if tags:
                merged_tags.update(tags)
            
            logger.info(
                "creating_resource_group",
                name=resource_group_name,
                location=location,
                subscription_id=sub_id,
                tags=merged_tags
            )
            
            # Create resource group
            rg_result = resource_client.resource_groups.create_or_update(
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
        List all resource groups across all subscriptions
        
        Returns:
            List of AzureResourceGroup models from all subscriptions
        """
        try:
            resource_groups = []
            
            # Get all subscriptions
            subscriptions = self.subscription_client.subscriptions.list()
            
            for sub in subscriptions:
                # Skip disabled subscriptions
                if sub.state.lower() != 'enabled':
                    continue
                
                try:
                    # Create resource client for this subscription
                    sub_resource_client = ResourceManagementClient(
                        credential=self.credential,
                        subscription_id=sub.subscription_id
                    )
                    
                    # List resource groups in this subscription
                    for rg in sub_resource_client.resource_groups.list():
                        resource_groups.append(
                            AzureResourceGroup(
                                id=rg.id,
                                name=rg.name,
                                location=rg.location,
                                tags=rg.tags or {},
                                provisioning_state=rg.properties.provisioning_state
                            )
                        )
                    
                    logger.info(
                        "listed_resource_groups_for_subscription",
                        subscription_id=sub.subscription_id,
                        subscription_name=sub.display_name,
                        count=len([rg for rg in resource_groups if sub.subscription_id in rg.id])
                    )
                    
                except AzureError as e:
                    logger.warning(
                        "failed_to_list_resource_groups_for_subscription",
                        subscription_id=sub.subscription_id,
                        subscription_name=sub.display_name,
                        error=str(e)
                    )
                    # Continue with other subscriptions even if one fails
                    continue
            
            logger.info("list_resource_groups_completed", total_count=len(resource_groups))
            return resource_groups
            
        except AzureError as e:
            logger.error("list_resource_groups_failed", error=str(e))
            return []
