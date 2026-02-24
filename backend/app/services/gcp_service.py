"""
GCP Service - Handles GCP project creation and management
"""
import logging
from typing import Optional, Dict, List
from google.cloud import resourcemanager_v3
from google.api_core import exceptions
from ..core.config import settings

logger = logging.getLogger(__name__)


class GCPService:
    """Service for managing GCP projects"""
    
    def __init__(self):
        """Initialize GCP service with credentials"""
        try:
            self.projects_client = resourcemanager_v3.ProjectsClient()
            logger.info("GCP service initialized successfully")
        except Exception as e:
            logger.error(f"Failed to initialize GCP service: {str(e)}")
            raise
    
    async def create_project(
        self,
        project_id: str,
        display_name: str,
        parent: Optional[str] = None,
        labels: Optional[Dict[str, str]] = None
    ) -> Dict:
        """
        Create a new GCP project
        
        Args:
            project_id: Unique project ID
            display_name: Human-readable project name
            parent: Parent organization or folder (format: organizations/{org_id} or folders/{folder_id})
            labels: Project labels/tags
            
        Returns:
            Dict containing project information
        """
        try:
            logger.info(f"Creating GCP project: {project_id}")
            
            # Prepare project request
            project = resourcemanager_v3.Project(
                project_id=project_id,
                display_name=display_name,
                labels=labels or {}
            )
            
            if parent:
                project.parent = parent
            
            # Create the project
            request = resourcemanager_v3.CreateProjectRequest(
                project=project
            )
            
            operation = self.projects_client.create_project(request=request)
            
            # Wait for the operation to complete
            response = operation.result()
            
            logger.info(f"GCP project created successfully: {response.name}")
            
            return {
                "project_id": response.project_id,
                "project_number": response.name.split("/")[1],
                "display_name": response.display_name,
                "lifecycle_state": response.state.name,
                "create_time": response.create_time.isoformat() if response.create_time else None
            }
            
        except exceptions.AlreadyExists:
            logger.warning(f"Project {project_id} already exists")
            raise ValueError(f"Project {project_id} already exists")
        except exceptions.PermissionDenied as e:
            logger.error(f"Permission denied creating project: {str(e)}")
            raise PermissionError(f"Insufficient permissions to create project: {str(e)}")
        except Exception as e:
            logger.error(f"Error creating GCP project: {str(e)}")
            raise
    
    async def get_project(self, project_id: str) -> Optional[Dict]:
        """
        Get project information
        
        Args:
            project_id: Project ID or project number
            
        Returns:
            Dict containing project information or None if not found
        """
        try:
            request = resourcemanager_v3.GetProjectRequest(
                name=f"projects/{project_id}"
            )
            project = self.projects_client.get_project(request=request)
            
            return {
                "project_id": project.project_id,
                "project_number": project.name.split("/")[1],
                "display_name": project.display_name,
                "lifecycle_state": project.state.name,
                "create_time": project.create_time.isoformat() if project.create_time else None
            }
        except exceptions.NotFound:
            logger.warning(f"Project {project_id} not found")
            return None
        except Exception as e:
            logger.error(f"Error getting GCP project: {str(e)}")
            raise
    
    async def list_projects(self, parent: Optional[str] = None) -> List[Dict]:
        """
        List all accessible GCP projects
        
        Args:
            parent: Parent organization or folder to filter by
            
        Returns:
            List of project dictionaries
        """
        try:
            request = resourcemanager_v3.ListProjectsRequest(
                parent=parent
            )
            
            projects = []
            for project in self.projects_client.list_projects(request=request):
                projects.append({
                    "project_id": project.project_id,
                    "project_number": project.name.split("/")[1],
                    "display_name": project.display_name,
                    "lifecycle_state": project.state.name,
                    "create_time": project.create_time.isoformat() if project.create_time else None
                })
            
            logger.info(f"Found {len(projects)} GCP projects")
            return projects
            
        except Exception as e:
            logger.error(f"Error listing GCP projects: {str(e)}")
            raise
    
    async def delete_project(self, project_id: str) -> bool:
        """
        Delete a GCP project (marks for deletion)
        
        Args:
            project_id: Project ID to delete
            
        Returns:
            True if successful
        """
        try:
            request = resourcemanager_v3.DeleteProjectRequest(
                name=f"projects/{project_id}"
            )
            operation = self.projects_client.delete_project(request=request)
            operation.result()  # Wait for completion
            
            logger.info(f"GCP project {project_id} marked for deletion")
            return True
            
        except exceptions.NotFound:
            logger.warning(f"Project {project_id} not found")
            return False
        except Exception as e:
            logger.error(f"Error deleting GCP project: {str(e)}")
            raise
