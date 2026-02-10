"""
Input Validators
"""
import re
from typing import Optional


def validate_resource_group_name(name: str) -> tuple[bool, Optional[str]]:
    """
    Validate Azure Resource Group name
    
    Rules:
    - Can contain alphanumerics, underscores, parentheses, hyphens, periods
    - Cannot end with period
    - 1-90 characters
    
    Args:
        name: Resource group name to validate
        
    Returns:
        Tuple of (is_valid, error_message)
    """
    if not name:
        return False, "Resource group name cannot be empty"
    
    if len(name) > 90:
        return False, "Resource group name must be 90 characters or less"
    
    if name.endswith("."):
        return False, "Resource group name cannot end with a period"
    
    pattern = r'^[a-zA-Z0-9_\-\(\)\.]+$'
    if not re.match(pattern, name):
        return False, "Resource group name can only contain alphanumerics, underscores, parentheses, hyphens, and periods"
    
    return True, None


def validate_github_repo_name(name: str) -> tuple[bool, Optional[str]]:
    """
    Validate GitHub repository name
    
    Rules:
    - Alphanumerics, hyphens, underscores
    - Cannot start with hyphen or underscore
    - 1-100 characters
    
    Args:
        name: Repository name to validate
        
    Returns:
        Tuple of (is_valid, error_message)
    """
    if not name:
        return False, "Repository name cannot be empty"
    
    if len(name) > 100:
        return False, "Repository name must be 100 characters or less"
    
    if name.startswith("-") or name.startswith("_"):
        return False, "Repository name cannot start with hyphen or underscore"
    
    pattern = r'^[a-zA-Z0-9_\-\.]+$'
    if not re.match(pattern, name):
        return False, "Repository name can only contain alphanumerics, hyphens, underscores, and periods"
    
    return True, None


def sanitize_name(name: str, max_length: int = 90) -> str:
    """
    Sanitize a name to be valid for Azure/GitHub
    
    Args:
        name: Name to sanitize
        max_length: Maximum length (default 90 for Azure RG)
        
    Returns:
        Sanitized name
    """
    # Replace spaces with hyphens
    name = name.replace(" ", "-")
    
    # Remove invalid characters
    name = re.sub(r'[^a-zA-Z0-9_\-\(\)\.]', '', name)
    
    # Remove leading/trailing special characters
    name = name.strip("-_.")
    
    # Truncate to max length
    name = name[:max_length]
    
    # Ensure it doesn't end with period
    name = name.rstrip(".")
    
    return name if name else "unnamed-resource"
