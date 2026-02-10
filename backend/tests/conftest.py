"""
Test configuration and fixtures
"""
import pytest
import os


@pytest.fixture(scope="session")
def test_env():
    """Set up test environment variables"""
    os.environ.update({
        "AZURE_SUBSCRIPTION_ID": "test-sub-id",
        "AZURE_TENANT_ID": "test-tenant-id",
        "AZURE_CLIENT_ID": "test-client-id",
        "AZURE_CLIENT_SECRET": "test-client-secret",
        "GITHUB_TOKEN": "test-github-token",
        "GITHUB_ORG": "test-org",
        "SHAREPOINT_SITE_URL": "https://test.sharepoint.com",
        "SHAREPOINT_CLIENT_ID": "test-sp-client-id",
        "SHAREPOINT_CLIENT_SECRET": "test-sp-client-secret",
        "WEBHOOK_SECRET": "test-webhook-secret",
    })
