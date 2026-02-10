# Azure Resources Tracker

> **Automated Azure Resource Group and GitHub Repository Creation via SharePoint Integration**

## 📋 Overview

This application automatically creates Azure Resource Groups and GitHub repositories when SharePoint entries are updated. It provides a seamless workflow for resource provisioning with tracking capabilities.

## 🎯 Features

- **SharePoint Integration**: Monitor SharePoint list for new/updated entries
- **Azure Resource Group Creation**: Automatically provision Azure resource groups
- **GitHub Repository Creation**: Create repositories with standardized templates
- **Tracking Dashboard**: View all created resources with metadata
- **Webhook Support**: Real-time updates from SharePoint
- **Audit Trail**: Track creation date, user, project name

## 📊 SharePoint Schema

The SharePoint list should contain the following columns:

| Column Name | Type | Description |
|------------|------|-------------|
| `UserName` | Text | Name of the requesting user |
| `ResourceGroupName` | Text | Name for the Azure resource group |
| `DateOfCreation` | DateTime | Timestamp of entry creation |
| `ProjectName` | Text | Associated project name |
| `Status` | Choice | Processing status (Pending/In Progress/Completed/Failed) |
| `AzureResourceGroupId` | Text | Azure RG ID (auto-populated) |
| `GitHubRepoUrl` | Text | GitHub repo URL (auto-populated) |

## 🏗️ Architecture

```
SharePoint List Update
       ↓
   Webhook Event
       ↓
   Backend API (FastAPI)
       ↓
   ┌─────────────────┐
   ↓                 ↓
Azure SDK      GitHub API
   ↓                 ↓
Create RG      Create Repo
   ↓                 ↓
Update SharePoint Entry
```

## 🚀 Quick Start

### Prerequisites

- Python 3.9+
- Node.js 20+
- Azure Subscription
- GitHub Account with Personal Access Token
- SharePoint Online access
- Azure Service Principal

### Environment Variables

Create a `.env` file in the backend directory:

```env
# Azure Configuration
AZURE_SUBSCRIPTION_ID=your-subscription-id
AZURE_TENANT_ID=your-tenant-id
AZURE_CLIENT_ID=your-client-id
AZURE_CLIENT_SECRET=your-client-secret
AZURE_DEFAULT_LOCATION=eastus

# GitHub Configuration
GITHUB_TOKEN=your-github-token
GITHUB_ORG=your-github-org

# SharePoint Configuration
SHAREPOINT_SITE_URL=https://yourorg.sharepoint.com/sites/yoursite
SHAREPOINT_LIST_NAME=ResourceRequests
SHAREPOINT_CLIENT_ID=your-sharepoint-client-id
SHAREPOINT_CLIENT_SECRET=your-sharepoint-client-secret

# Application Configuration
WEBHOOK_SECRET=your-webhook-secret
API_HOST=0.0.0.0
API_PORT=8000
```

### Backend Setup

```bash
cd backend
python -m venv venv
source venv/bin/activate  # Windows: venv\Scripts\activate
pip install -r requirements.txt
python main.py
```

### Frontend Setup

```bash
cd frontend
npm install
npm run dev
```

### Docker Deployment

```bash
# Build and run with Docker Compose
docker-compose up -d

# View logs
docker-compose logs -f
```

## 📁 Project Structure

```
azure-resources-tracker/
├── backend/
│   ├── app/
│   │   ├── __init__.py
│   │   ├── main.py
│   │   ├── models.py
│   │   ├── config.py
│   │   ├── routers/
│   │   │   ├── __init__.py
│   │   │   ├── webhook.py
│   │   │   ├── resources.py
│   │   │   └── health.py
│   │   ├── services/
│   │   │   ├── __init__.py
│   │   │   ├── azure_service.py
│   │   │   ├── github_service.py
│   │   │   └── sharepoint_service.py
│   │   └── utils/
│   │       ├── __init__.py
│   │       ├── logger.py
│   │       └── validators.py
│   ├── tests/
│   ├── requirements.txt
│   ├── Dockerfile
│   └── .env.example
├── frontend/
│   ├── src/
│   │   ├── components/
│   │   ├── pages/
│   │   ├── services/
│   │   ├── App.tsx
│   │   └── main.tsx
│   ├── public/
│   ├── package.json
│   ├── vite.config.ts
│   └── Dockerfile
├── .github/
│   └── workflows/
│       ├── backend-ci.yml
│       ├── frontend-ci.yml
│       └── deploy.yml
├── docker-compose.yml
├── README.md
└── DEPLOYMENT.md
```

## 🔧 API Endpoints

### Webhook Endpoint
```
POST /api/webhook/sharepoint
```
Receives SharePoint webhook notifications

### Resources Endpoints
```
GET  /api/resources              # List all tracked resources
GET  /api/resources/{id}         # Get specific resource
POST /api/resources/create       # Manually trigger resource creation
GET  /api/resources/status/{id}  # Check creation status
```

### Health Check
```
GET /api/health
```

## 🔐 Security

- **Authentication**: Azure AD integration
- **Authorization**: Role-based access control (RBAC)
- **Secrets Management**: Azure Key Vault integration
- **API Security**: Rate limiting and input validation
- **Webhook Validation**: HMAC signature verification

## 🚢 Deployment

### Azure App Service

```bash
# Deploy backend
az webapp up --name azure-tracker-api --runtime "PYTHON:3.9"

# Deploy frontend
az webapp up --name azure-tracker-ui --runtime "NODE:20-lts"
```

### Cloud Run (GCP)

```bash
# Deploy backend
gcloud run deploy azure-tracker-api --source ./backend

# Deploy frontend
gcloud run deploy azure-tracker-ui --source ./frontend
```

## 📈 Monitoring

- Application Insights for Azure deployments
- Custom logging with structured logs
- Health check endpoints
- Status dashboard in frontend

## 🤝 Contributing

1. Fork the repository
2. Create a feature branch
3. Commit your changes
4. Push to the branch
5. Create a Pull Request

## 📝 License

MIT License - see LICENSE file for details

## 📞 Support

For issues or questions, please create an issue in the GitHub repository.
