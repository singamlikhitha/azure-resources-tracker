"""
Unit tests for Azure service
"""
import pytest
from unittest.mock import Mock, patch
from app.services.azure_service import AzureService
from azure.core.exceptions import AzureError


@pytest.fixture
def azure_service():
    """Fixture for AzureService instance"""
    with patch('app.services.azure_service.ClientSecretCredential'):
        with patch('app.services.azure_service.ResourceManagementClient'):
            service = AzureService()
            return service


@pytest.mark.asyncio
async def test_create_resource_group_success(azure_service):
    """Test successful resource group creation"""
    # Mock the resource client
    mock_rg = Mock()
    mock_rg.id = "/subscriptions/123/resourceGroups/test-rg"
    mock_rg.name = "test-rg"
    mock_rg.location = "eastus"
    mock_rg.tags = {"test": "true"}
    mock_rg.properties.provisioning_state = "Succeeded"
    
    azure_service.resource_client.resource_groups.create_or_update = Mock(
        return_value=mock_rg
    )
    
    # Call the method
    result = await azure_service.create_resource_group(
        resource_group_name="test-rg",
        location="eastus",
        tags={"test": "true"}
    )
    
    # Assertions
    assert result.name == "test-rg"
    assert result.location == "eastus"
    assert result.provisioning_state == "Succeeded"


@pytest.mark.asyncio
async def test_create_resource_group_failure(azure_service):
    """Test resource group creation failure"""
    # Mock an Azure error
    azure_service.resource_client.resource_groups.create_or_update = Mock(
        side_effect=AzureError("Quota exceeded")
    )
    
    # Call should raise exception
    with pytest.raises(AzureError):
        await azure_service.create_resource_group(
            resource_group_name="test-rg",
            location="eastus"
        )


@pytest.mark.asyncio
async def test_get_resource_group(azure_service):
    """Test getting an existing resource group"""
    # Mock the resource client
    mock_rg = Mock()
    mock_rg.id = "/subscriptions/123/resourceGroups/test-rg"
    mock_rg.name = "test-rg"
    mock_rg.location = "eastus"
    mock_rg.tags = {}
    mock_rg.properties.provisioning_state = "Succeeded"
    
    azure_service.resource_client.resource_groups.get = Mock(
        return_value=mock_rg
    )
    
    # Call the method
    result = await azure_service.get_resource_group("test-rg")
    
    # Assertions
    assert result is not None
    assert result.name == "test-rg"
