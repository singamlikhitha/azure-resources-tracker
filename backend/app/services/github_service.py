"""
GitHub Repository Management Service
"""
from github import Github, GithubException
import structlog
from typing import Optional

from app.config import get_settings
from app.models import GitHubRepository

logger = structlog.get_logger()
settings = get_settings()


class GitHubService:
    """Service for GitHub repository management"""
    
    def __init__(self):
        """Initialize GitHub service with token"""
        self.client = Github(settings.GITHUB_TOKEN)
        self.org = self.client.get_organization(settings.GITHUB_ORG)
    
    async def create_repository(
        self,
        repo_name: str,
        description: Optional[str] = None,
        private: Optional[bool] = None,
        auto_init: Optional[bool] = None
    ) -> GitHubRepository:
        """
        Create a GitHub repository
        
        Args:
            repo_name: Repository name
            description: Repository description
            private: Whether the repo is private
            auto_init: Initialize with README
            
        Returns:
            GitHubRepository model
            
        Raises:
            GithubException: If creation fails
        """
        try:
            private = private if private is not None else settings.GITHUB_PRIVATE
            auto_init = auto_init if auto_init is not None else settings.GITHUB_AUTO_INIT
            
            logger.info(
                "creating_github_repository",
                name=repo_name,
                org=settings.GITHUB_ORG,
                private=private
            )
            
            # Create repository in organization
            repo = self.org.create_repo(
                name=repo_name,
                description=description or f"Repository for {repo_name}",
                private=private,
                auto_init=auto_init,
                gitignore_template="Python" if auto_init else None
            )
            
            logger.info(
                "github_repository_created",
                id=repo.id,
                name=repo.name,
                url=repo.html_url
            )
            
            return GitHubRepository(
                id=repo.id,
                name=repo.name,
                full_name=repo.full_name,
                html_url=repo.html_url,
                clone_url=repo.clone_url,
                created_at=repo.created_at,
                private=repo.private
            )
            
        except GithubException as e:
            logger.error(
                "github_repository_creation_failed",
                name=repo_name,
                error=str(e)
            )
            raise
    
    async def get_repository(self, repo_name: str) -> Optional[GitHubRepository]:
        """
        Get an existing repository
        
        Args:
            repo_name: Repository name
            
        Returns:
            GitHubRepository model or None if not found
        """
        try:
            repo = self.org.get_repo(repo_name)
            
            return GitHubRepository(
                id=repo.id,
                name=repo.name,
                full_name=repo.full_name,
                html_url=repo.html_url,
                clone_url=repo.clone_url,
                created_at=repo.created_at,
                private=repo.private
            )
        except GithubException as e:
            logger.warning(
                "github_repository_not_found",
                name=repo_name,
                error=str(e)
            )
            return None
    
    async def delete_repository(self, repo_name: str) -> bool:
        """
        Delete a repository
        
        Args:
            repo_name: Repository name
            
        Returns:
            True if deleted successfully
        """
        try:
            logger.info("deleting_github_repository", name=repo_name)
            
            repo = self.org.get_repo(repo_name)
            repo.delete()
            
            logger.info("github_repository_deleted", name=repo_name)
            return True
            
        except GithubException as e:
            logger.error(
                "github_repository_deletion_failed",
                name=repo_name,
                error=str(e)
            )
            return False
    
    async def add_collaborator(
        self,
        repo_name: str,
        username: str,
        permission: str = "push"
    ) -> bool:
        """
        Add a collaborator to a repository
        
        Args:
            repo_name: Repository name
            username: GitHub username
            permission: Permission level (pull, push, admin)
            
        Returns:
            True if added successfully
        """
        try:
            repo = self.org.get_repo(repo_name)
            user = self.client.get_user(username)
            
            repo.add_to_collaborators(user, permission=permission)
            
            logger.info(
                "collaborator_added",
                repo=repo_name,
                user=username,
                permission=permission
            )
            return True
            
        except GithubException as e:
            logger.error(
                "add_collaborator_failed",
                repo=repo_name,
                user=username,
                error=str(e)
            )
            return False
