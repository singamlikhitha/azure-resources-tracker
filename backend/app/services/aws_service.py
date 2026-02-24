"""
AWS Service - Handles AWS account creation and management
"""
import logging
from typing import Optional, Dict, List
import boto3
from botocore.exceptions import ClientError, BotoCoreError
from ..core.config import settings

logger = logging.getLogger(__name__)


class AWSService:
    """Service for managing AWS accounts"""
    
    def __init__(self):
        """Initialize AWS service with credentials"""
        try:
            self.organizations_client = boto3.client('organizations')
            logger.info("AWS service initialized successfully")
        except Exception as e:
            logger.error(f"Failed to initialize AWS service: {str(e)}")
            raise
    
    async def create_account(
        self,
        account_name: str,
        email: str,
        role_name: str = "OrganizationAccountAccessRole",
        tags: Optional[List[Dict[str, str]]] = None
    ) -> Dict:
        """
        Create a new AWS account within organization
        
        Args:
            account_name: Name of the AWS account
            email: Unique email address for the account
            role_name: Name of IAM role for organization access
            tags: Account tags
            
        Returns:
            Dict containing account creation information
        """
        try:
            logger.info(f"Creating AWS account: {account_name}")
            
            # Prepare create account request
            request_params = {
                'Email': email,
                'AccountName': account_name,
                'RoleName': role_name
            }
            
            if tags:
                request_params['Tags'] = tags
            
            # Create the account (async operation)
            response = self.organizations_client.create_account(**request_params)
            
            create_request_id = response['CreateAccountStatus']['Id']
            logger.info(f"AWS account creation initiated: {create_request_id}")
            
            # Return the status - account creation is async in AWS
            return {
                "request_id": create_request_id,
                "account_name": account_name,
                "email": email,
                "status": response['CreateAccountStatus']['State'],
                "account_id": response['CreateAccountStatus'].get('AccountId')
            }
            
        except ClientError as e:
            error_code = e.response['Error']['Code']
            if error_code == 'DuplicateAccountException':
                logger.warning(f"Account with email {email} already exists")
                raise ValueError(f"Account with email {email} already exists")
            elif error_code == 'AccessDeniedException':
                logger.error(f"Access denied creating account: {str(e)}")
                raise PermissionError(f"Insufficient permissions to create account: {str(e)}")
            else:
                logger.error(f"AWS error creating account: {str(e)}")
                raise
        except Exception as e:
            logger.error(f"Error creating AWS account: {str(e)}")
            raise
    
    async def get_account_creation_status(self, request_id: str) -> Dict:
        """
        Check the status of an account creation request
        
        Args:
            request_id: The create account request ID
            
        Returns:
            Dict containing account creation status
        """
        try:
            response = self.organizations_client.describe_create_account_status(
                CreateAccountRequestId=request_id
            )
            
            status = response['CreateAccountStatus']
            return {
                "request_id": status['Id'],
                "status": status['State'],
                "account_id": status.get('AccountId'),
                "account_name": status.get('AccountName'),
                "completed_timestamp": status.get('CompletedTimestamp'),
                "failure_reason": status.get('FailureReason')
            }
            
        except ClientError as e:
            logger.error(f"Error getting account status: {str(e)}")
            raise
    
    async def get_account(self, account_id: str) -> Optional[Dict]:
        """
        Get AWS account information
        
        Args:
            account_id: AWS account ID
            
        Returns:
            Dict containing account information or None if not found
        """
        try:
            response = self.organizations_client.describe_account(
                AccountId=account_id
            )
            
            account = response['Account']
            return {
                "account_id": account['Id'],
                "account_name": account['Name'],
                "email": account['Email'],
                "status": account['Status'],
                "joined_method": account['JoinedMethod'],
                "joined_timestamp": account.get('JoinedTimestamp')
            }
            
        except ClientError as e:
            if e.response['Error']['Code'] == 'AccountNotFoundException':
                logger.warning(f"Account {account_id} not found")
                return None
            logger.error(f"Error getting AWS account: {str(e)}")
            raise
    
    async def list_accounts(self) -> List[Dict]:
        """
        List all AWS accounts in the organization
        
        Returns:
            List of account dictionaries
        """
        try:
            accounts = []
            paginator = self.organizations_client.get_paginator('list_accounts')
            
            for page in paginator.paginate():
                for account in page['Accounts']:
                    accounts.append({
                        "account_id": account['Id'],
                        "account_name": account['Name'],
                        "email": account['Email'],
                        "status": account['Status'],
                        "joined_method": account['JoinedMethod'],
                        "joined_timestamp": account.get('JoinedTimestamp')
                    })
            
            logger.info(f"Found {len(accounts)} AWS accounts")
            return accounts
            
        except ClientError as e:
            logger.error(f"Error listing AWS accounts: {str(e)}")
            raise
    
    async def close_account(self, account_id: str) -> bool:
        """
        Close an AWS account
        
        Args:
            account_id: Account ID to close
            
        Returns:
            True if successful
        """
        try:
            self.organizations_client.close_account(
                AccountId=account_id
            )
            
            logger.info(f"AWS account {account_id} closed successfully")
            return True
            
        except ClientError as e:
            if e.response['Error']['Code'] == 'AccountNotFoundException':
                logger.warning(f"Account {account_id} not found")
                return False
            logger.error(f"Error closing AWS account: {str(e)}")
            raise
