#!/usr/bin/env python3

"""
Azure Resources Tracker - Automated Deployment Script
Deploys backend and frontend to Azure Container Apps with subscription selection
"""

# ───────── Auto-install Required Packages ─────────
import sys
import subprocess

def install_package(package_name):
    """Install a package using pip"""
    print(f"Installing {package_name}...")
    try:
        subprocess.check_call(
            [sys.executable, "-m", "pip", "install", package_name, "--quiet"],
            stdout=subprocess.DEVNULL,
            stderr=subprocess.PIPE
        )
        print(f"✓ {package_name} installed successfully")
    except subprocess.CalledProcessError as e:
        print(f"✗ Failed to install {package_name}")
        print(f"Error: {e.stderr.decode() if e.stderr else 'Unknown error'}")
        sys.exit(1)

def check_and_install_packages():
    """Check for required packages and install if missing"""
    required_packages = [
        ("docker", "docker"),
        ("azure-identity", "azure.identity"),
        ("azure-mgmt-resource", "azure.mgmt.resource"),
        ("azure-mgmt-containerregistry", "azure.mgmt.containerregistry"),
        ("azure-core", "azure.core")
    ]
    
    packages_to_install = []
    
    # Check which packages are missing
    for pip_name, import_name in required_packages:
        try:
            __import__(import_name)
        except ImportError:
            packages_to_install.append(pip_name)
    
    # Install missing packages
    if packages_to_install:
        print(f"\n{'='*60}")
        print(f"Installing {len(packages_to_install)} required package(s)...")
        print(f"{'='*60}\n")
        for package in packages_to_install:
            install_package(package)
        print(f"\n{'='*60}")
        print("All dependencies installed successfully!")
        print(f"{'='*60}\n")

# Install required packages before importing them
check_and_install_packages()

import os
import json
import argparse
import docker
import tempfile
import shutil
from typing import Dict
from datetime import datetime

from azure.identity import DefaultAzureCredential, InteractiveBrowserCredential
from azure.mgmt.resource import ResourceManagementClient
from azure.mgmt.containerregistry import ContainerRegistryManagementClient
from azure.mgmt.containerregistry.models import Registry, Sku as AcrSku, SkuName as AcrSkuName
from azure.core.exceptions import ResourceNotFoundError


class AzureResourcesTrackerDeployer:

    def __init__(self, config: Dict):
        self.config = config
        self.resource_group = config.get("resource_group")
        self.location = config.get("location", "eastus")
        self.acr_name = config.get("acr_name")
        self.environment_name = config.get("environment_name")
        self.backend_app_name = config.get("backend_app_name")
        self.frontend_app_name = config.get("frontend_app_name")

        timestamp = datetime.now().strftime("%Y%m%d-%H%M%S")
        self.backend_image_tag = f"{self.acr_name}.azurecr.io/azure-tracker-backend:{timestamp}"
        self.frontend_image_tag = f"{self.acr_name}.azurecr.io/azure-tracker-frontend:{timestamp}"

        self.credential = None
        self.subscription_id = None
        self.resource_client = None
        self.acr_client = None
        self.docker_client = None
        self._temp_docker_config_dir = None
        self._original_docker_config = None

    def __del__(self):
        """Cleanup temporary Docker config directory"""
        self._cleanup_docker_config()

    def _validate_config(self):
        """Validate required configuration fields"""
        # subscription_id is now optional - will be selected interactively if not provided
        required_fields = [
            "resource_group", "acr_name", "environment_name",
            "backend_app_name", "frontend_app_name"
        ]
        
        missing_fields = [field for field in required_fields if not self.config.get(field)]
        
        if missing_fields:
            print(f"\n✗ Error: Missing required configuration fields:")
            for field in missing_fields:
                print(f"  - {field}")
            sys.exit(1)
        
        print("✓ Configuration validated")

    def _check_prerequisites(self):
        """Check if required tools are installed and available"""
        print("\nChecking prerequisites...")
        
        # Check Azure CLI
        try:
            result = subprocess.run(
                "az --version",
                shell=True,
                capture_output=True,
                text=True,
                timeout=10
            )
            if result.returncode == 0:
                print("✓ Azure CLI is installed")
            else:
                print("✗ Azure CLI not found")
                print("  Please install Azure CLI: https://docs.microsoft.com/en-us/cli/azure/install-azure-cli")
                sys.exit(1)
        except Exception as e:
            print(f"✗ Error checking Azure CLI: {e}")
            print("  Please install Azure CLI: https://docs.microsoft.com/en-us/cli/azure/install-azure-cli")
            sys.exit(1)
        
        # Check Azure login
        try:
            result = subprocess.run(
                "az account show",
                shell=True,
                capture_output=True,
                text=True,
                timeout=10
            )
            if result.returncode == 0:
                print("✓ Azure CLI is logged in")
            else:
                print("✗ Not logged into Azure CLI")
                print("  Please run: az login")
                sys.exit(1)
        except Exception as e:
            print(f"✗ Error checking Azure login: {e}")
            print("  Please run: az login")
            sys.exit(1)
        
        # Check Docker
        try:
            client = docker.from_env()
            client.ping()
            print("✓ Docker is running")
        except Exception as e:
            print(f"✗ Docker is not running or not installed")
            print(f"  Error: {e}")
            print("  Please ensure Docker Desktop is installed and running")
            sys.exit(1)
        
        print("\n✓ All prerequisites met\n")

    def _cleanup_docker_config(self):
        """Remove temporary Docker config directory and restore original settings"""
        # Restore original DOCKER_CONFIG environment variable
        if self._original_docker_config is not None:
            if self._original_docker_config == '':
                # It was not set originally, so remove it
                os.environ.pop('DOCKER_CONFIG', None)
            else:
                os.environ['DOCKER_CONFIG'] = self._original_docker_config
        
        # Remove temporary directory
        if self._temp_docker_config_dir and os.path.exists(self._temp_docker_config_dir):
            try:
                shutil.rmtree(self._temp_docker_config_dir)
                print(" Cleaned up temporary Docker config")
            except Exception as e:
                print(f" Warning: Could not cleanup temp Docker config: {e}")

    # ───────── Helper Methods ─────────

    def _run_command(self, command: str) -> str:
        """Run Azure CLI command and return output"""
        try:
            result = subprocess.run(
                command,
                shell=True,
                check=True,
                capture_output=True,
                text=True
            )
            return result.stdout.strip()
        except subprocess.CalledProcessError as e:
            print(f" Command failed: {e}")
            if e.stderr:
                print(f"Error: {e.stderr}")
            raise

    # ───────── Subscription Selection ─────────

    def _get_available_subscriptions(self):
        """Get list of available Azure subscriptions"""
        try:
            result = subprocess.run(
                "az account list --query '[].{Name:name, SubscriptionId:id, State:state}' -o json",
                shell=True,
                capture_output=True,
                text=True,
                timeout=15
            )
            if result.returncode == 0:
                return json.loads(result.stdout)
            return []
        except Exception as e:
            print(f" Warning: Could not fetch subscriptions: {e}")
            return []

    def _select_subscription(self):
        """Allow user to select subscription if not specified or invalid"""
        config_sub_id = self.config.get("subscription_id", "")
        
        # Check if subscription_id is placeholder or empty
        is_placeholder = (
            not config_sub_id or 
            config_sub_id == "00000000-0000-0000-0000-000000000000" or
            config_sub_id.strip() == ""
        )
        
        if is_placeholder:
            print("\n No valid subscription ID found in config.json")
            print(" Fetching available subscriptions...")
            
            subscriptions = self._get_available_subscriptions()
            
            if not subscriptions:
                print("\n✗ Error: No Azure subscriptions found")
                print("  Please ensure you are logged into Azure (az login)")
                sys.exit(1)
            
            # Filter only enabled subscriptions
            active_subs = [s for s in subscriptions if s.get('State') == 'Enabled']
            
            if not active_subs:
                print("\n✗ Error: No enabled subscriptions found")
                sys.exit(1)
            
            if len(active_subs) == 1:
                # Only one subscription, use it automatically
                selected_sub = active_subs[0]
                print(f"\n✓ Using subscription: {selected_sub['Name']}")
                print(f"  ID: {selected_sub['SubscriptionId']}")
                return selected_sub['SubscriptionId']
            
            # Multiple subscriptions - let user choose
            print("\n Available Azure Subscriptions:")
            print("="*80)
            for idx, sub in enumerate(active_subs, 1):
                print(f"{idx}. {sub['Name']}")
                print(f"   ID: {sub['SubscriptionId']}")
                print()
            
            while True:
                try:
                    choice = input("Select subscription number (or 'q' to quit): ").strip()
                    
                    if choice.lower() == 'q':
                        print("\nDeployment cancelled by user")
                        sys.exit(0)
                    
                    choice_num = int(choice)
                    if 1 <= choice_num <= len(active_subs):
                        selected_sub = active_subs[choice_num - 1]
                        print(f"\n✓ Selected: {selected_sub['Name']}")
                        return selected_sub['SubscriptionId']
                    else:
                        print(f"Please enter a number between 1 and {len(active_subs)}")
                except ValueError:
                    print("Invalid input. Please enter a number.")
                except KeyboardInterrupt:
                    print("\n\nDeployment cancelled by user")
                    sys.exit(0)
        else:
            # Subscription ID provided in config - validate it exists
            subscriptions = self._get_available_subscriptions()
            
            if subscriptions:
                sub_ids = [s['SubscriptionId'] for s in subscriptions]
                if config_sub_id not in sub_ids:
                    print(f"\n⚠ Warning: Subscription ID '{config_sub_id}' not found in your account")
                    print("\n Available subscriptions:")
                    for sub in subscriptions:
                        print(f"  - {sub['Name']}: {sub['SubscriptionId']}")
                    print("\n✗ Error: Please update subscription_id in config.json")
                    sys.exit(1)
            
            return config_sub_id

    # ───────── Authentication ─────────

    def authenticate(self):
        print("\n Authenticating with Azure...")

        # Select or validate subscription
        self.subscription_id = self._select_subscription()

        try:
            self.credential = DefaultAzureCredential()
            self._init_clients()
            print(" Authenticated via DefaultAzureCredential")
        except Exception:
            print(" Falling back to interactive login...")
            self.credential = InteractiveBrowserCredential()
            self._init_clients()
            print(" Authenticated via interactive browser login")
        
        # Set the default subscription for Azure CLI commands
        print(f" Setting subscription to: {self.subscription_id}")
        set_sub_cmd = f"az account set --subscription {self.subscription_id}"
        try:
            subprocess.run(set_sub_cmd, shell=True, check=True, capture_output=True, text=True)
            print(" Subscription set successfully")
        except subprocess.CalledProcessError as e:
            print(f" Warning: Could not set default subscription: {e.stderr}")
            print("Will use explicit --subscription flag in all commands")

    def _init_clients(self):
        self.resource_client = ResourceManagementClient(self.credential, self.subscription_id)
        self.acr_client = ContainerRegistryManagementClient(self.credential, self.subscription_id)

    def _init_docker_client(self):
        if not self.docker_client:
            try:
                # Temporarily create a minimal Docker config to avoid gcloud credential store conflicts
                # This is necessary when Docker is configured for GCP but deploying to Azure
                
                # Save original DOCKER_CONFIG environment variable
                self._original_docker_config = os.environ.get('DOCKER_CONFIG', '')
                
                # Create a temporary Docker config directory
                temp_docker_dir = tempfile.mkdtemp(prefix="docker_config_")
                temp_config_path = os.path.join(temp_docker_dir, "config.json")
                
                # Write minimal config without credential store
                with open(temp_config_path, 'w') as f:
                    json.dump({"auths": {}}, f)
                
                # Store the temp directory for cleanup
                self._temp_docker_config_dir = temp_docker_dir
                
                # Set environment variable to use temporary config
                os.environ['DOCKER_CONFIG'] = temp_docker_dir
                
                # Now initialize Docker client
                self.docker_client = docker.from_env()
                self.docker_client.ping()
                print(" Docker daemon running (using temporary config)")
            except Exception as e:
                print(" Docker error detected:", e)
                print(" Note: Please ensure Docker Desktop is open and running on your system.")
                raise

    # ───────── Resource Group ─────────

    def create_resource_group(self):
        print(f"\n Creating resource group {self.resource_group}")
        
        # Check if exists first
        check_cmd = f"az group exists --name {self.resource_group} --subscription {self.subscription_id}"
        try:
            result = subprocess.run(check_cmd, shell=True, capture_output=True, text=True)
            if result.stdout.strip().lower() == "true":
                print(f" Resource group '{self.resource_group}' already exists")
                return
        except Exception:
            pass
        
        # Create using Azure CLI
        create_cmd = f"az group create --name {self.resource_group} --location {self.location} --subscription {self.subscription_id}"
        try:
            result = subprocess.run(
                create_cmd,
                shell=True,
                check=True,
                capture_output=True,
                text=True
            )
            print(f" Resource group '{self.resource_group}' created")
        except subprocess.CalledProcessError as e:
            print(f" Failed to create resource group")
            print(f"Error: {e.stderr}")
            raise

    # ───────── ACR ─────────

    def create_container_registry(self):
        print(f"\n Creating ACR {self.acr_name}")
        try:
            self.acr_client.registries.get(self.resource_group, self.acr_name)
            print(" ACR already exists")
            return
        except ResourceNotFoundError:
            pass

        registry = Registry(
            location=self.location,
            sku=AcrSku(name=AcrSkuName.BASIC),
            admin_user_enabled=True,
        )

        self.acr_client.registries.begin_create(
            self.resource_group, self.acr_name, registry
        ).result()

        print(" ACR created")

    def _get_acr_credentials(self):
        creds = self.acr_client.registries.list_credentials(self.resource_group, self.acr_name)
        return creds.username, creds.passwords[0].value

    # ───────── Docker Build ─────────

    def _build_and_push(self, path, tag, label, build_args=None):
        self._init_docker_client()

        username, password = self._get_acr_credentials()
        registry_url = f"{self.acr_name}.azurecr.io"

        self.docker_client.login(registry=registry_url, username=username, password=password)

        print(f"\n Building {label}")
        print(f"Build context: {path}")
        if build_args:
            print(f"Build args: {build_args}")
        
        # Build with streaming logs
        try:
            for line in self.docker_client.api.build(
                path=path,
                tag=tag,
                rm=True,
                decode=True,
                buildargs=build_args or {}
            ):
                if 'stream' in line:
                    print(line['stream'], end='')
                elif 'error' in line:
                    print(f"Error: {line['error']}")
                    raise Exception(line['error'])
                elif 'status' in line:
                    print(line['status'])
        except Exception as e:
            print(f" Build failed: {e}")
            raise

        print(f"\n Building complete for {label}")
        print(f" Pushing {label} to {registry_url}")
        
        for line in self.docker_client.images.push(tag, stream=True, decode=True):
            if line.get("status"):
                status = line["status"]
                if line.get("progress"):
                    status += f" {line['progress']}"
                print(status, end="\r")

        print(f"\n {label} pushed successfully")

    def build_images(self):
        """Build and push backend image only"""
        # Get parent directory (project root) since script is in deployment/
        base_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
        backend_path = os.path.join(base_dir, "backend")

        self._build_and_push(backend_path, self.backend_image_tag, "backend")

    def build_frontend_image(self, backend_url: str):
        """Build and push frontend image with backend URL"""
        # Get parent directory (project root) since script is in deployment/
        base_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
        frontend_path = os.path.join(base_dir, "frontend")
        
        # Pass backend URL as build argument
        build_args = {
            'VITE_API_URL': backend_url
        }
        
        self._build_and_push(frontend_path, self.frontend_image_tag, "frontend", build_args=build_args)

    # ───────── Container Apps Environment ─────────

    def create_container_apps_environment(self):
        print("\n Creating Container Apps environment")

        # Check if environment exists
        check_cmd = f"az containerapp env show --name {self.environment_name} --resource-group {self.resource_group} --subscription {self.subscription_id} --query name -o tsv"
        try:
            result = subprocess.run(check_cmd, shell=True, capture_output=True, text=True)
            if result.returncode == 0 and result.stdout.strip():
                print(" Environment already exists")
                return
        except Exception:
            pass

        print("Creating Container Apps environment (this may take a few minutes)...")
        
        create_cmd = f"az containerapp env create --name {self.environment_name} --resource-group {self.resource_group} --location {self.location} --subscription {self.subscription_id} --enable-workload-profiles false"
        
        try:
            result = subprocess.run(
                create_cmd,
                shell=True,
                check=True,
                capture_output=True,
                text=True
            )
            print(result.stdout)
            print(" Environment created")
        except subprocess.CalledProcessError as e:
            print(f" Failed to create environment")
            print(f"Error output: {e.stderr}")
            raise

    # ───────── Deploy Container Apps ─────────

    def deploy_backend_app(self) -> str:
        """Deploy backend container app and return its URL"""
        print(f"\n Deploying backend app: {self.backend_app_name}")

        # Get ACR credentials
        username, password = self._get_acr_credentials()
        registry_server = f"{self.acr_name}.azurecr.io"

        # Get environment variables from config
        env_vars = self.config.get("backend_env_vars", {})
        env_str = " ".join([f'"{k}={v}"' for k, v in env_vars.items()])

        # Check if app exists
        check_cmd = f"az containerapp show --name {self.backend_app_name} --resource-group {self.resource_group} --subscription {self.subscription_id} --query name -o tsv"
        result = subprocess.run(check_cmd, shell=True, capture_output=True, text=True)
        
        if result.returncode == 0 and result.stdout.strip():
            # Update existing app
            print("Updating existing backend app...")
            update_cmd = f"""az containerapp update --name {self.backend_app_name} --resource-group {self.resource_group} --subscription {self.subscription_id} --image {self.backend_image_tag}"""
            
            if env_str:
                update_cmd += f" --set-env-vars {env_str}"
            
            try:
                subprocess.run(update_cmd, shell=True, check=True, capture_output=True, text=True)
                print(" Backend app updated")
            except subprocess.CalledProcessError as e:
                print(f" Failed to update backend: {e.stderr}")
                raise
        else:
            # Create new app
            print("Creating new backend app...")
            create_cmd = f"""az containerapp create --name {self.backend_app_name} --resource-group {self.resource_group} --environment {self.environment_name} --subscription {self.subscription_id} --image {self.backend_image_tag} --target-port 8000 --ingress external --registry-server {registry_server} --registry-username {username} --registry-password "{password}" --cpu 0.5 --memory 1.0Gi --min-replicas 1 --max-replicas 3"""
            
            if env_str:
                create_cmd += f" --env-vars {env_str}"
            
            try:
                result = subprocess.run(
                    create_cmd,
                    shell=True,
                    check=True,
                    capture_output=True,
                    text=True
                )
                print(" Backend app created")
            except subprocess.CalledProcessError as e:
                print(f" Failed to create backend: {e.stderr}")
                raise

        # Get backend URL
        url_cmd = f"az containerapp show --name {self.backend_app_name} --resource-group {self.resource_group} --subscription {self.subscription_id} --query properties.configuration.ingress.fqdn -o tsv"
        result = subprocess.run(url_cmd, shell=True, capture_output=True, text=True)
        backend_fqdn = result.stdout.strip()
        backend_url = f"https://{backend_fqdn}"
        
        print(f" Backend URL: {backend_url}")
        return backend_url

    def deploy_frontend_app(self, backend_url: str) -> str:
        """Deploy frontend container app and return its URL"""
        print(f"\n Deploying frontend app: {self.frontend_app_name}")

        # Get ACR credentials
        username, password = self._get_acr_credentials()
        registry_server = f"{self.acr_name}.azurecr.io"

        # Check if app exists
        check_cmd = f"az containerapp show --name {self.frontend_app_name} --resource-group {self.resource_group} --subscription {self.subscription_id} --query name -o tsv"
        result = subprocess.run(check_cmd, shell=True, capture_output=True, text=True)
        
        if result.returncode == 0 and result.stdout.strip():
            # Update existing app
            print("Updating existing frontend app...")
            update_cmd = f"""az containerapp update --name {self.frontend_app_name} --resource-group {self.resource_group} --subscription {self.subscription_id} --image {self.frontend_image_tag}"""
            
            try:
                subprocess.run(update_cmd, shell=True, check=True, capture_output=True, text=True)
                print(" Frontend app updated")
            except subprocess.CalledProcessError as e:
                print(f" Failed to update frontend: {e.stderr}")
                raise
        else:
            # Create new app (backend URL is baked into image at build time)
            print("Creating new frontend app...")
            create_cmd = f"""az containerapp create --name {self.frontend_app_name} --resource-group {self.resource_group} --environment {self.environment_name} --subscription {self.subscription_id} --image {self.frontend_image_tag} --target-port 80 --ingress external --registry-server {registry_server} --registry-username {username} --registry-password "{password}" --cpu 0.5 --memory 1.0Gi --min-replicas 1 --max-replicas 3"""
            
            try:
                result = subprocess.run(
                    create_cmd,
                    shell=True,
                    check=True,
                    capture_output=True,
                    text=True
                )
                print(" Frontend app created")
            except subprocess.CalledProcessError as e:
                print(f" Failed to create frontend: {e.stderr}")
                raise

        # Get frontend URL
        url_cmd = f"az containerapp show --name {self.frontend_app_name} --resource-group {self.resource_group} --subscription {self.subscription_id} --query properties.configuration.ingress.fqdn -o tsv"
        result = subprocess.run(url_cmd, shell=True, capture_output=True, text=True)
        frontend_fqdn = result.stdout.strip()
        frontend_url = f"https://{frontend_fqdn}"
        
        print(f" Frontend URL: {frontend_url}")
        return frontend_url

    # ───────── Main Deploy ─────────

    def deploy(self):
        print("\n Starting Azure Resources Tracker Deployment\n")

        try:
            self._validate_config()
            self._check_prerequisites()
            self.authenticate()
            self.create_resource_group()
            self.create_container_registry()
            
            # Build and deploy backend first
            self.build_images()  # Builds backend only
            self.create_container_apps_environment()
            backend_url = self.deploy_backend_app()
            
            # Build frontend with backend URL, then deploy
            print(f"\n Building frontend with backend URL: {backend_url}")
            self.build_frontend_image(backend_url)
            frontend_url = self.deploy_frontend_app(backend_url)

            print("\n" + "=" * 80)
            print(" Deployment completed successfully!")
            print("=" * 80)
            print(f"\n Backend URL:  {backend_url}")
            print(f" Frontend URL: {frontend_url}")
            print(f"\n API Documentation: {backend_url}/docs")
            print("\n Your Azure Resources Tracker is now live on Azure Container Apps!")
            print("=" * 80)
        finally:
            # Cleanup temporary Docker config
            self._cleanup_docker_config()


# ───────── Entry ─────────

def main():
    parser = argparse.ArgumentParser(
        description="Deploy Azure Resources Tracker to Azure Container Apps",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Example usage:
  python deploy.py --config config.json

Prerequisites:
  - Azure CLI installed and logged in (az login)
  - Docker Desktop running
  - Python 3.9+
        """
    )
    parser.add_argument(
        "--config",
        required=True,
        help="Path to configuration JSON file"
    )
    args = parser.parse_args()

    # Validate config file exists
    if not os.path.exists(args.config):
        print(f"✗ Error: Configuration file not found: {args.config}")
        sys.exit(1)

    # Load and validate JSON
    try:
        with open(args.config) as f:
            config = json.load(f)
    except json.JSONDecodeError as e:
        print(f"✗ Error: Invalid JSON in configuration file: {e}")
        sys.exit(1)
    except Exception as e:
        print(f"✗ Error reading configuration file: {e}")
        sys.exit(1)

    # Run deployment
    try:
        AzureResourcesTrackerDeployer(config).deploy()
    except KeyboardInterrupt:
        print("\n\n⚠ Deployment interrupted by user")
        sys.exit(1)
    except Exception as e:
        print(f"\n\n✗ Deployment failed with error: {e}")
        print("\nFor support, please check:")
        print("  - Azure portal for resource status")
        print("  - Docker Desktop is running")
        print("  - Azure CLI is logged in (az login)")
        sys.exit(1)


if __name__ == "__main__":
    main()
