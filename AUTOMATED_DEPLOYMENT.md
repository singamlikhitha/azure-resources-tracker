# Azure Resources Tracker - Automated Deployment

This deployment script automates the deployment of Azure Resources Tracker to Azure Container Apps with **subscription selection** support.

## Features

✅ **Automatic Subscription Selection** - Choose which Azure subscription to use during deployment  
✅ **One-Command Deployment** - Deploy backend and frontend with a single command  
✅ **Docker Credential Handling** - Automatically handles Docker credential conflicts  
✅ **Environment Validation** - Checks all prerequisites before starting  
✅ **Progress Tracking** - Clear status updates during deployment  

---

## Prerequisites

Before deployment, ensure you have:

### Required Tools
- **Azure CLI** - [Install](https://docs.microsoft.com/en-us/cli/azure/install-azure-cli)
- **Docker Desktop** - [Install](https://www.docker.com/products/docker-desktop/)
- **Python 3.9+** - [Install](https://www.python.org/downloads/)

### Azure Requirements
- Azure subscription with Contributor role or higher
- Logged into Azure CLI: `az login`

### Application Setup
- Azure AD Service Principal (for backend to manage resources)
- GitHub Personal Access Token (for repo creation)
- SharePoint app registration (for list integration)

---

## Quick Start

### 1. Configure Deployment

Edit `config.json` with your settings:

```json
{
  "subscription_id": "",
  "resource_group": "rg-azure-resources-tracker",
  "location": "eastus",
  "acr_name": "acrazuretracker",
  "environment_name": "env-azure-tracker",
  "backend_app_name": "azure-tracker-backend",
  "frontend_app_name": "azure-tracker-frontend",
  "backend_env_vars": {
    "AZURE_TENANT_ID": "your-tenant-id",
    "AZURE_CLIENT_ID": "your-service-principal-client-id",
    "AZURE_CLIENT_SECRET": "your-service-principal-secret",
    "GITHUB_TOKEN": "your-github-pat",
    "SHAREPOINT_SITE_URL": "https://yoursite.sharepoint.com",
    "SHAREPOINT_LIST_NAME": "Azure Resources",
    "SHAREPOINT_CLIENT_ID": "your-sharepoint-app-client-id",
    "SHAREPOINT_CLIENT_SECRET": "your-sharepoint-app-secret"
  }
}
```

**Note:** Leave `subscription_id` empty or use `""` to select from available subscriptions during deployment.

### 2. Run Deployment

```powershell
python deploy.py --config config.json
```

### 3. Select Subscription (if not specified)

If multiple subscriptions are available:

```
Available Azure Subscriptions:
================================================================================
1. Production Subscription
   ID: 12345678-1234-1234-1234-123456789012

2. Development Subscription
   ID: 87654321-4321-4321-4321-210987654321

Select subscription number (or 'q' to quit): 2

✓ Selected: Development Subscription
```

### 4. Wait for Deployment

The script will:
- ✓ Validate configuration
- ✓ Check prerequisites
- ✓ Authenticate with Azure
- ✓ Create resource group
- ✓ Create Azure Container Registry
- ✓ Build Docker images
- ✓ Push images to ACR
- ✓ Create Container Apps environment
- ✓ Deploy backend application
- ✓ Deploy frontend application

### 5. Access Your Application

```
================================================================================
 Deployment completed successfully!
================================================================================

 Backend URL:  https://azure-tracker-backend.azurecontainerapps.io
 Frontend URL: https://azure-tracker-frontend.azurecontainerapps.io

 API Documentation: https://azure-tracker-backend.azurecontainerapps.io/docs

 Your Azure Resources Tracker is now live on Azure Container Apps!
================================================================================
```

---

## Configuration Fields

### Required Fields

| Field | Description | Example |
|-------|-------------|---------|
| `resource_group` | Azure resource group name | `rg-azure-resources-tracker` |
| `acr_name` | Azure Container Registry name (globally unique) | `acrazuretracker` |
| `environment_name` | Container Apps environment name | `env-azure-tracker` |
| `backend_app_name` | Backend container app name | `azure-tracker-backend` |
| `frontend_app_name` | Frontend container app name | `azure-tracker-frontend` |

### Optional Fields

| Field | Description | Default |
|-------|-------------|---------|
| `subscription_id` | Azure subscription ID (leave empty to select) | Interactive selection |
| `location` | Azure region | `eastus` |
| `backend_env_vars` | Environment variables for backend | `{}` |

### Backend Environment Variables

Required for application functionality:

| Variable | Description | How to Get |
|----------|-------------|------------|
| `AZURE_TENANT_ID` | Azure AD tenant ID | `az account show --query tenantId -o tsv` |
| `AZURE_CLIENT_ID` | Service principal client ID | Create via `az ad sp create-for-rbac` |
| `AZURE_CLIENT_SECRET` | Service principal secret | From service principal creation |
| `GITHUB_TOKEN` | GitHub PAT with repo scope | [GitHub Settings](https://github.com/settings/tokens) |
| `SHAREPOINT_SITE_URL` | SharePoint site URL | From SharePoint |
| `SHAREPOINT_LIST_NAME` | SharePoint list name | Name of your list |
| `SHAREPOINT_CLIENT_ID` | SharePoint app client ID | From app registration |
| `SHAREPOINT_CLIENT_SECRET` | SharePoint app secret | From app registration |

---

## Subscription Selection

### Interactive Selection

Leave `subscription_id` empty or set to `""`:

```json
{
  "subscription_id": ""
}
```

The script will:
1. Fetch available subscriptions
2. Display them with names and IDs
3. Let you choose which one to use
4. Create all resources in selected subscription

### Pre-Specified Subscription

Set specific subscription ID:

```json
{
  "subscription_id": "12345678-1234-1234-1234-123456789012"
}
```

The script will:
1. Validate the subscription exists
2. Use that subscription
3. Skip interactive selection

### Single Subscription

If you only have one subscription, it's automatically selected:

```
✓ Using subscription: My Azure Subscription
  ID: 12345678-1234-1234-1234-123456789012
```

---

## Updating Deployment

To update the application after code changes:

```powershell
# Update config.json if needed
# Run deployment again
python deploy.py --config config.json
```

The script will:
- Use existing resources (resource group, ACR, environment)
- Build new Docker images with new timestamp
- Update container apps with new images
- Preserve existing data and configuration

---

## Cleanup

To remove all deployed resources:

```powershell
# Delete resource group and all contained resources
az group delete --name rg-azure-resources-tracker --yes

# This removes:
# - Container apps
# - Container Apps environment
# - Azure Container Registry
# - All Docker images
```

---

## Troubleshooting

### "No Azure subscriptions found"
**Fix:** Run `az login`

### "Docker is not running"
**Fix:** Start Docker Desktop

### "ACR name already taken"
**Fix:** Change `acr_name` in config.json to a unique value

### "Subscription ID not found"
**Fix:** Remove or update `subscription_id` in config.json

### Build fails
**Fix:** Ensure Dockerfiles exist in backend/ and frontend/ directories

For more issues, see the [DEPLOYMENT.md](DEPLOYMENT.md) guide.

---

## SharePoint Integration

For SharePoint-based deployment with dropdown subscription selection, see:
- Backend integration: Check `backend/app` for SharePoint handlers
- API endpoints: `GET /subscriptions` and `POST /deploy`
- Power Automate: Set up flow to call deployment API

---

## Security Notes

1. **Never commit credentials** - Use Azure Key Vault for production
2. **Service Principal** - Use least-privilege access
3. **GitHub Token** - Use fine-grained PAT with minimal scopes
4. **SharePoint Secrets** - Rotate regularly

---

## Cost Estimation

### Azure Container Apps
- **Backend**: ~$10-30/month (0.5 vCPU, 1GB RAM)
- **Frontend**: ~$10-30/month (0.5 vCPU, 1GB RAM)
- **Environment**: ~$5/month

### Azure Container Registry
- **Basic tier**: ~$5/month
- **Storage**: ~$0.10/GB/month

**Total Estimated Cost**: ~$30-70/month

Free tier available for development/testing.

---

## Support

For issues or questions:
1. Check DEPLOYMENT.md for detailed setup
2. Review Azure portal for resource status
3. Check container logs: `az containerapp logs show --name <app-name> --resource-group <rg-name>`

---

## What's Deployed

### Infrastructure
- ✅ Azure Container Registry (for Docker images)
- ✅ Azure Container Apps Environment (managed Kubernetes)
- ✅ Backend Container App (Python FastAPI)
- ✅ Frontend Container App (React/Vite)

### Features
- ✅ HTTPS endpoints (auto-provisioned)
- ✅ Auto-scaling (1-3 replicas)
- ✅ Health monitoring
- ✅ Log aggregation
- ✅ Zero-downtime deployments

### Integrations
- ✅ Azure AD authentication
- ✅ SharePoint list integration
- ✅ GitHub API integration
- ✅ Azure Resource Manager API
