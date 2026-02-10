"""
Data Models
"""
from pydantic import BaseModel, Field
from typing import Optional
from datetime import datetime
from enum import Enum


class ResourceStatus(str, Enum):
    """Resource creation status"""
    PENDING = "Pending"
    IN_PROGRESS = "In Progress"
    COMPLETED = "Completed"
    FAILED = "Failed"


class SharePointEntry(BaseModel):
    """SharePoint list entry model"""
    id: Optional[str] = None
    user_name: str = Field(..., alias="UserName")
    resource_group_name: str = Field(..., alias="ResourceGroupName")
    date_of_creation: datetime = Field(default_factory=datetime.utcnow, alias="DateOfCreation")
    project_name: str = Field(..., alias="ProjectName")
    status: ResourceStatus = Field(default=ResourceStatus.PENDING, alias="Status")
    azure_resource_group_id: Optional[str] = Field(None, alias="AzureResourceGroupId")
    github_repo_url: Optional[str] = Field(None, alias="GitHubRepoUrl")
    error_message: Optional[str] = Field(None, alias="ErrorMessage")
    
    class Config:
        populate_by_name = True
        json_schema_extra = {
            "example": {
                "UserName": "John Doe",
                "ResourceGroupName": "rg-myproject-dev",
                "ProjectName": "My Project",
                "DateOfCreation": "2026-02-10T10:30:00Z"
            }
        }


class ResourceCreationRequest(BaseModel):
    """Manual resource creation request"""
    user_name: str = Field(..., description="Name of the requesting user")
    resource_group_name: str = Field(..., description="Azure resource group name")
    project_name: str = Field(..., description="Project name")
    location: Optional[str] = Field(None, description="Azure region")
    create_github_repo: bool = Field(True, description="Create GitHub repository")
    tags: Optional[dict] = Field(None, description="Additional tags")
    
    class Config:
        json_schema_extra = {
            "example": {
                "user_name": "John Doe",
                "resource_group_name": "rg-myproject-dev",
                "project_name": "My Project",
                "location": "eastus",
                "create_github_repo": True,
                "tags": {"Environment": "Development"}
            }
        }


class ResourceCreationResponse(BaseModel):
    """Resource creation response"""
    status: ResourceStatus
    resource_group_id: Optional[str] = None
    resource_group_name: Optional[str] = None
    github_repo_url: Optional[str] = None
    sharepoint_item_id: Optional[str] = None
    message: str
    created_at: datetime = Field(default_factory=datetime.utcnow)
    
    
class AzureResourceGroup(BaseModel):
    """Azure Resource Group model"""
    id: str
    name: str
    location: str
    tags: dict
    provisioning_state: str


class GitHubRepository(BaseModel):
    """GitHub Repository model"""
    id: int
    name: str
    full_name: str
    html_url: str
    clone_url: str
    created_at: datetime
    private: bool


class WebhookPayload(BaseModel):
    """SharePoint webhook payload"""
    subscription_id: str
    client_state: Optional[str] = None
    expiration_date_time: Optional[datetime] = None
    resource: str
    tenant_id: str
    site_url: str
    web_id: str


class HealthResponse(BaseModel):
    """Health check response"""
    status: str
    version: str
    timestamp: datetime = Field(default_factory=datetime.utcnow)
    services: dict
