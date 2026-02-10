"""
Unit tests for GitHub service
"""
import pytest
from unittest.mock import Mock, patch
from app.services.github_service import GitHubService
from github import GithubException


@pytest.fixture
def github_service():
    """Fixture for GitHubService instance"""
    with patch('app.services.github_service.Github'):
        service = GitHubService()
        service.org = Mock()
        return service


@pytest.mark.asyncio
async def test_create_repository_success(github_service):
    """Test successful repository creation"""
    # Mock repository
    mock_repo = Mock()
    mock_repo.id = 123456
    mock_repo.name = "test-repo"
    mock_repo.full_name = "org/test-repo"
    mock_repo.html_url = "https://github.com/org/test-repo"
    mock_repo.clone_url = "https://github.com/org/test-repo.git"
    mock_repo.created_at = "2026-02-10T10:30:00Z"
    mock_repo.private = False
    
    github_service.org.create_repo = Mock(return_value=mock_repo)
    
    # Call the method
    result = await github_service.create_repository(
        repo_name="test-repo",
        description="Test repository"
    )
    
    # Assertions
    assert result.name == "test-repo"
    assert result.html_url == "https://github.com/org/test-repo"
    assert result.private == False


@pytest.mark.asyncio
async def test_create_repository_failure(github_service):
    """Test repository creation failure"""
    # Mock a GitHub error
    github_service.org.create_repo = Mock(
        side_effect=GithubException(422, {"message": "Repository already exists"})
    )
    
    # Call should raise exception
    with pytest.raises(GithubException):
        await github_service.create_repository(
            repo_name="test-repo"
        )


@pytest.mark.asyncio
async def test_get_repository(github_service):
    """Test getting an existing repository"""
    # Mock repository
    mock_repo = Mock()
    mock_repo.id = 123456
    mock_repo.name = "test-repo"
    mock_repo.full_name = "org/test-repo"
    mock_repo.html_url = "https://github.com/org/test-repo"
    mock_repo.clone_url = "https://github.com/org/test-repo.git"
    mock_repo.created_at = "2026-02-10T10:30:00Z"
    mock_repo.private = False
    
    github_service.org.get_repo = Mock(return_value=mock_repo)
    
    # Call the method
    result = await github_service.get_repository("test-repo")
    
    # Assertions
    assert result is not None
    assert result.name == "test-repo"
