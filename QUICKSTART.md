# Azure Resources Tracker - Quick Start Guide

Get the Azure Resources Tracker up and running in 5 minutes!

## ⚡ Quick Setup

### 1. Clone the Repository

```bash
git clone https://github.com/yourusername/azure-resources-tracker.git
cd azure-resources-tracker
```

### 2. Backend Setup

```bash
cd backend

# Create virtual environment
python -m venv venv

# Activate (Windows)
venv\Scripts\activate

# Activate (Mac/Linux)
source venv/bin/activate

# Install dependencies
pip install -r requirements.txt

# Copy environment template
copy .env.example .env  # Windows
cp .env.example .env    # Mac/Linux
```

**Edit `.env` file with your credentials:**

```env
# Minimum required configuration
AZURE_SUBSCRIPTION_ID=your-azure-subscription-id
AZURE_TENANT_ID=your-tenant-id
AZURE_CLIENT_ID=your-client-id
AZURE_CLIENT_SECRET=your-client-secret

GITHUB_TOKEN=your-github-personal-access-token
GITHUB_ORG=your-github-organization

SHAREPOINT_SITE_URL=https://yourorg.sharepoint.com/sites/yoursite
SHAREPOINT_CLIENT_ID=your-sharepoint-client-id
SHAREPOINT_CLIENT_SECRET=your-sharepoint-client-secret
```

**Start the backend:**

```bash
python -m app.main
```

Backend running at: http://localhost:8000

### 3. Frontend Setup (New Terminal)

```bash
cd frontend

# Install dependencies
npm install

# Copy environment template
copy .env.example .env  # Windows
cp .env.example .env    # Mac/Linux

# Start development server
npm run dev
```

Frontend running at: http://localhost:5173

### 4. Verify Installation

Open your browser:
- Frontend: http://localhost:5173
- Backend API Docs: http://localhost:8000/docs
- Health Check: http://localhost:8000/api/health

## 🐳 Docker Quick Start (Alternative)

If you have Docker installed:

```bash
# Copy environment files
cd backend && cp .env.example .env && cd ..
cd frontend && cp .env.example .env && cd ..

# Edit .env files with your credentials

# Start all services
docker-compose up -d

# View logs
docker-compose logs -f
```

Access:
- Frontend: http://localhost:5173
- Backend: http://localhost:8000

## 🎯 Create Your First Resource

### Via Web UI

1. Open http://localhost:5173
2. Click **"Create"** in navigation
3. Fill in the form:
   - User Name: Your name
   - Resource Group Name: `rg-test-project`
   - Project Name: `Test Project`
   - Location: `East US`
4. Click **"Create Resources"**

### Via API

```bash
curl -X POST http://localhost:8000/api/resources/create \
  -H "Content-Type: application/json" \
  -d '{
    "user_name": "John Doe",
    "resource_group_name": "rg-test-project",
    "project_name": "Test Project",
    "location": "eastus",
    "create_github_repo": true
  }'
```

### Via SharePoint

1. Open your SharePoint list
2. Add new item:
   - User Name: `John Doe`
   - Resource Group Name: `rg-test-project`
   - Project Name: `Test Project`
   - Status: `Pending`
3. Webhook will automatically trigger creation

## 🔧 Get Your Credentials

### Azure Service Principal

```bash
az login
az account set --subscription <subscription-id>

az ad sp create-for-rbac \
  --name "azure-resources-tracker" \
  --role Contributor \
  --scopes /subscriptions/<subscription-id> \
  --sdk-auth
```

Copy the JSON output values to your `.env` file.

### GitHub Personal Access Token

1. Go to https://github.com/settings/tokens
2. Click **"Generate new token (classic)"**
3. Select scopes:
   - `repo` (all)
   - `admin:org` → `write:org`
4. Copy token to `.env` file

### SharePoint App Registration

1. Go to: `https://yoursite.sharepoint.com/_layouts/15/appregnew.aspx`
2. Click **Generate** for Client ID and Secret
3. Fill:
   - App Domain: `localhost`
   - Redirect URI: `https://localhost`
4. Copy credentials to `.env` file

## 📚 Next Steps

- Read the [README.md](README.md) for full documentation
- Check [DEPLOYMENT.md](DEPLOYMENT.md) for production deployment
- Review API documentation at http://localhost:8000/docs

## 🆘 Common Issues

**Backend fails to start:**
- Check Python version (3.9+)
- Verify all environment variables are set
- Check Azure credentials are valid

**Frontend fails to build:**
- Check Node version (20+)
- Run `npm install` again
- Clear `node_modules` and reinstall

**Docker issues:**
- Ensure Docker Desktop is running
- Check ports 8000 and 5173 are available
- Run `docker-compose down -v` and retry

## 📞 Need Help?

- Check the [README.md](README.md) troubleshooting section
- Review logs: Backend logs in console, frontend in browser DevTools
- Create an issue on GitHub

---

**You're all set!** 🎉 Start creating Azure resources automatically!
