# Azure Resources Tracker - Deployment Guide

## 📋 Prerequisites

### Required Accounts & Access
- **Azure Subscription** with Owner/Contributor role
- **GitHub Account** with organization access
- **SharePoint Online** site and list
- **Azure AD** application registration

### Required Tools
- Azure CLI (`az`)
- Python 3.9+
- Node.js 20+
- Docker (optional, for containerized deployment)

---

## 🔧 Setup Instructions

### 1. Azure Service Principal Setup

Create a service principal for the application:

```bash
# Login to Azure
az login

# Set subscription
az account set --subscription <subscription-id>

# Create service principal
az ad sp create-for-rbac \
  --name "azure-resources-tracker" \
  --role Contributor \
  --scopes /subscriptions/<subscription-id> \
  --sdk-auth

# Save the output JSON - you'll need it for GitHub Secrets
```

### 2. SharePoint List Configuration

Create a SharePoint list with the following columns:

| Column Name | Type | Required |
|-------------|------|----------|
| Title | Single line of text | Yes |
| UserName | Single line of text | Yes |
| ResourceGroupName | Single line of text | Yes |
| ProjectName | Single line of text | Yes |
| DateOfCreation | Date and Time | Yes |
| Status | Choice (Pending, In Progress, Completed, Failed) | Yes |
| AzureResourceGroupId | Single line of text | No |
| GitHubRepoUrl | Hyperlink | No |
| ErrorMessage | Multiple lines of text | No |

### 3. SharePoint App Registration

```bash
# Register app in SharePoint
# Navigate to: https://yoursite.sharepoint.com/_layouts/15/appregnew.aspx

# Generate Client ID and Secret
# Set App Domain: localhost (for dev)
# Set Redirect URI: https://localhost

# Grant permissions
# Navigate to: https://yoursite.sharepoint.com/_layouts/15/appinv.aspx
# Use this permission XML:
```

```xml
<AppPermissionRequests AllowAppOnlyPolicy="true">
  <AppPermissionRequest Scope="http://sharepoint/content/sitecollection/web/list" Right="Manage" />
</AppPermissionRequests>
```

### 4. GitHub Personal Access Token

```bash
# Create a PAT at: https://github.com/settings/tokens

# Required scopes:
# - repo (all)
# - admin:org (read:org, write:org)
# - delete_repo (optional, for cleanup)
```

### 5. Configure Environment Variables

#### Backend (.env file)

```bash
cd backend
cp .env.example .env

# Edit .env with your values:
# - AZURE_* variables from service principal
# - GITHUB_TOKEN from PAT
# - SHAREPOINT_* variables from app registration
```

#### Frontend (.env file)

```bash
cd frontend
cp .env.example .env

# Edit .env:
VITE_API_URL=http://localhost:8000
```

---

## 🚀 Local Development

### Backend

```bash
cd backend

# Create virtual environment
python -m venv venv
source venv/bin/activate  # Windows: venv\Scripts\activate

# Install dependencies
pip install -r requirements.txt

# Run development server
python -m app.main
```

Backend will be available at: `http://localhost:8000`
API docs at: `http://localhost:8000/docs`

### Frontend

```bash
cd frontend

# Install dependencies
npm install

# Run development server
npm run dev
```

Frontend will be available at: `http://localhost:5173`

### Docker Compose (Recommended)

```bash
# Build and start all services
docker-compose up -d

# View logs
docker-compose logs -f

# Stop services
docker-compose down
```

---

## 🌐 Production Deployment

### Option 1: Azure App Service

#### Deploy Backend

```bash
# Create resource group
az group create \
  --name rg-azure-tracker-prod \
  --location eastus

# Create App Service plan
az appservice plan create \
  --name plan-azure-tracker \
  --resource-group rg-azure-tracker-prod \
  --is-linux \
  --sku B1

# Create Web App
az webapp create \
  --name azure-tracker-api-prod \
  --resource-group rg-azure-tracker-prod \
  --plan plan-azure-tracker \
  --runtime "PYTHON:3.11"

# Configure app settings
az webapp config appsettings set \
  --name azure-tracker-api-prod \
  --resource-group rg-azure-tracker-prod \
  --settings \
    AZURE_SUBSCRIPTION_ID="<value>" \
    AZURE_TENANT_ID="<value>" \
    AZURE_CLIENT_ID="<value>" \
    AZURE_CLIENT_SECRET="@Microsoft.KeyVault(SecretUri=...)"

# Deploy code
cd backend
zip -r backend.zip .
az webapp deployment source config-zip \
  --name azure-tracker-api-prod \
  --resource-group rg-azure-tracker-prod \
  --src backend.zip
```

#### Deploy Frontend

```bash
# Build frontend
cd frontend
npm run build

# Create Static Web App
az staticwebapp create \
  --name azure-tracker-ui-prod \
  --resource-group rg-azure-tracker-prod \
  --source ./dist \
  --location eastus2 \
  --branch main

# Or deploy to Azure Storage + CDN
az storage account create \
  --name azuretrackerui \
  --resource-group rg-azure-tracker-prod \
  --location eastus \
  --sku Standard_LRS

az storage blob service-properties update \
  --account-name azuretrackerui \
  --static-website \
  --index-document index.html

az storage blob upload-batch \
  --account-name azuretrackerui \
  --source ./dist \
  --destination '$web'
```

### Option 2: Google Cloud Run

#### Deploy Backend

```bash
# Enable APIs
gcloud services enable run.googleapis.com artifactregistry.googleapis.com

# Create Artifact Registry
gcloud artifacts repositories create azure-tracker \
  --repository-format=docker \
  --location=us-central1

# Build and push image
cd backend
gcloud builds submit \
  --tag us-central1-docker.pkg.dev/<project-id>/azure-tracker/backend

# Deploy to Cloud Run
gcloud run deploy azure-tracker-api \
  --image us-central1-docker.pkg.dev/<project-id>/azure-tracker/backend \
  --region us-central1 \
  --platform managed \
  --allow-unauthenticated \
  --set-env-vars="USE_SECRET_MANAGER=true"
```

#### Deploy Frontend

```bash
cd frontend
gcloud builds submit \
  --tag us-central1-docker.pkg.dev/<project-id>/azure-tracker/frontend

gcloud run deploy azure-tracker-ui \
  --image us-central1-docker.pkg.dev/<project-id>/azure-tracker/frontend \
  --region us-central1 \
  --platform managed \
  --allow-unauthenticated
```

### Option 3: GitHub Actions (Automated)

#### Configure Secrets

Go to repository Settings > Secrets and add:

- `AZURE_CREDENTIALS` - Service principal JSON
- `AZURE_SUBSCRIPTION_ID`
- `GITHUB_TOKEN` - PAT for repo creation
- `SHAREPOINT_CLIENT_ID`
- `SHAREPOINT_CLIENT_SECRET`
- `SHAREPOINT_SITE_URL`

#### Trigger Deployment

```bash
# Push to main branch
git push origin main

# Or manually trigger workflow
# Go to: Actions > Deploy to Azure > Run workflow
```

---

## 🔒 Security Best Practices

### 1. Use Azure Key Vault

```bash
# Create Key Vault
az keyvault create \
  --name kv-azure-tracker \
  --resource-group rg-azure-tracker-prod \
  --location eastus

# Store secrets
az keyvault secret set \
  --vault-name kv-azure-tracker \
  --name azure-client-secret \
  --value "<secret-value>"

# Grant access to App Service
az webapp identity assign \
  --name azure-tracker-api-prod \
  --resource-group rg-azure-tracker-prod

# Reference in app settings
az webapp config appsettings set \
  --name azure-tracker-api-prod \
  --resource-group rg-azure-tracker-prod \
  --settings \
    AZURE_CLIENT_SECRET="@Microsoft.KeyVault(VaultName=kv-azure-tracker;SecretName=azure-client-secret)"
```

### 2. Enable Application Insights

```bash
az monitor app-insights component create \
  --app azure-tracker-insights \
  --location eastus \
  --resource-group rg-azure-tracker-prod

# Connect to App Service
az webapp config appsettings set \
  --name azure-tracker-api-prod \
  --resource-group rg-azure-tracker-prod \
  --settings \
    APPLICATIONINSIGHTS_CONNECTION_STRING="<connection-string>"
```

### 3. Configure CORS

Update backend app settings or code to allow only your frontend domain.

### 4. Enable Authentication

Configure Azure AD authentication for both frontend and backend.

---

## 📊 Monitoring & Logs

### View Logs

```bash
# Azure App Service logs
az webapp log tail \
  --name azure-tracker-api-prod \
  --resource-group rg-azure-tracker-prod

# Cloud Run logs
gcloud run services logs read azure-tracker-api --region us-central1
```

### Health Checks

- Backend: `https://<your-api-url>/api/health`
- Frontend: `https://<your-ui-url>/health`

---

## 🧪 Testing

### Backend Tests

```bash
cd backend
pytest tests/ -v --cov=app
```

### Frontend Tests

```bash
cd frontend
npm test
```

---

## 🔄 Updates & Maintenance

### Update Dependencies

```bash
# Backend
cd backend
pip install --upgrade -r requirements.txt

# Frontend
cd frontend
npm update
```

### Database Migrations

If using a database, create and run migrations:

```bash
cd backend
alembic revision --autogenerate -m "description"
alembic upgrade head
```

---

## 📞 Troubleshooting

### Common Issues

1. **SharePoint webhook not working**
   - Verify client ID and secret
   - Check permissions
   - Ensure webhook URL is accessible

2. **Azure resource creation fails**
   - Verify service principal has Contributor role
   - Check subscription limits
   - Validate resource group name

3. **GitHub repo creation fails**
   - Verify PAT has correct scopes
   - Check organization permissions
   - Ensure repo name is unique

---

## 📝 License

MIT License - see LICENSE file for details
