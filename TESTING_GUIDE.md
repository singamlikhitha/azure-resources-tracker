# Testing Azure Resources Tracker After Deployment

This guide explains how to test your deployed Azure Resources Tracker application, including SharePoint integration.

---

## 🌐 Access Your Deployed Application

After successful deployment, you'll receive these URLs:

```
================================================================================
 Deployment completed successfully!
================================================================================

 Backend URL:  https://azure-tracker-backend.azurecontainerapps.io
 Frontend URL: https://azure-tracker-frontend.azurecontainerapps.io

 API Documentation: https://azure-tracker-backend.azurecontainerapps.io/docs
================================================================================
```

---

## 📋 Step 1: Set Up SharePoint List

### Create the List

1. **Navigate to your SharePoint site**
   - Go to: `https://yourcompany.sharepoint.com/sites/yoursite`

2. **Create new list**
   - Click **"New"** → **"List"**
   - Name: `ResourceRequests` or `Azure Resources`
   - Click **"Create"**

3. **Add required columns** (see table below)

### SharePoint List Structure

| Column Name | Type | Required | Choices/Default |
|-------------|------|----------|-----------------|
| Title (built-in) | Single line text | Yes | - |
| UserName | Single line text | Yes | - |
| ResourceGroupName | Single line text | Yes | - |
| ProjectName | Single line text | Yes | - |
| DateOfCreation | Date and Time | Yes | Default: Today |
| Status | Choice | Yes | Pending, In Progress, Completed, Failed (Default: Pending) |
| AzureResourceGroupId | Single line text | No | Auto-filled by app |
| GitHubRepoUrl | Hyperlink | No | Auto-filled by app |
| ErrorMessage | Multiple lines text | No | Auto-filled if error |

### Quick Setup

1. **Title** - Already exists
2. **+ Add column** → **"Single line of text"** → Name: `UserName` → Required: Yes
3. **+ Add column** → **"Single line of text"** → Name: `ResourceGroupName` → Required: Yes
4. **+ Add column** → **"Single line of text"** → Name: `ProjectName` → Required: Yes
5. **+ Add column** → **"Date and time"** → Name: `DateOfCreation` → Default: Today
6. **+ Add column** → **"Choice"** → Name: `Status` → Choices: `Pending, In Progress, Completed, Failed`
7. **+ Add column** → **"Single line of text"** → Name: `AzureResourceGroupId`
8. **+ Add column** → **"Hyperlink"** → Name: `GitHubRepoUrl`
9. **+ Add column** → **"Multiple lines of text"** → Name: `ErrorMessage`

---

## 🧪 Step 2: Test the API

### Test Health Endpoint

Open in browser or use curl:

```bash
# Check if API is running
curl https://azure-tracker-backend.azurecontainerapps.io/api/health

# Expected response:
{
  "status": "healthy",
  "timestamp": "2026-02-23T10:30:00Z",
  "version": "1.0.0"
}
```

### Test API Documentation

1. Open: `https://azure-tracker-backend.azurecontainerapps.io/docs`
2. You'll see interactive API documentation (Swagger UI)
3. Explore available endpoints:
   - `GET /api/health` - Health check
   - `POST /api/webhook/sharepoint` - SharePoint webhook endpoint
   - `POST /api/resources/create` - Manual resource creation
   - `GET /api/resources` - List resources

### Test Frontend

1. Open: `https://azure-tracker-frontend.azurecontainerapps.io`
2. You should see the application UI
3. Check browser console for any errors (F12)

---

## 🔗 Step 3: Test SharePoint Integration (Manual Polling)

### Option A: Manual Testing via SharePoint List

1. **Add a test item to SharePoint list:**
   - **Title:** Test Request 1
   - **UserName:** Your Name
   - **ResourceGroupName:** `rg-test-project-001`
   - **ProjectName:** Test Project 001
   - **Status:** Pending
   - **DateOfCreation:** (auto-filled)
   - Click **Save**

2. **Trigger the backend to check SharePoint:**
   ```bash
   # Call the polling endpoint (if your backend has one)
   curl -X POST https://azure-tracker-backend.azurecontainerapps.io/api/webhook/poll
   ```

3. **Check the SharePoint list item:**
   - Status should change: `Pending` → `In Progress` → `Completed` or `Failed`
   - If completed:
     - `AzureResourceGroupId` will show the Azure RG ID
     - `GitHubRepoUrl` will show the GitHub repo URL
   - If failed:
     - `ErrorMessage` will show what went wrong

### Option B: Test via API Directly

Use the Swagger UI (`/docs`) or curl:

```bash
# Create resource directly via API
curl -X POST https://azure-tracker-backend.azurecontainerapps.io/api/resources/create \
  -H "Content-Type: application/json" \
  -d '{
    "userName": "Test User",
    "resourceGroupName": "rg-test-api-001",
    "projectName": "API Test Project",
    "subscriptionId": "your-subscription-id"
  }'

# Expected response:
{
  "status": "success",
  "resourceGroupId": "/subscriptions/.../resourceGroups/rg-test-api-001",
  "githubRepoUrl": "https://github.com/yourorg/rg-test-api-001"
}
```

---

## 🔄 Step 4: Test Full Workflow

### End-to-End Test

1. **User submits request in SharePoint:**
   - Go to SharePoint list
   - Click **"New"**
   - Fill in details:
     - Title: "Production Database Setup"
     - UserName: "John Doe"
     - ResourceGroupName: "rg-prod-database-001"
     - ProjectName: "Customer Database Project"
   - Click **Save**

2. **Backend processes the request:**
   - Status changes to "In Progress"
   - Backend API:
     - Creates Azure Resource Group
     - Creates GitHub Repository
     - Updates SharePoint item

3. **Check results in SharePoint:**
   - Status: "Completed"
   - AzureResourceGroupId: `/subscriptions/.../resourceGroups/rg-prod-database-001`
   - GitHubRepoUrl: `https://github.com/yourorg/rg-prod-database-001`

4. **Verify in Azure Portal:**
   - Login to [Azure Portal](https://portal.azure.com)
   - Go to "Resource Groups"
   - Find `rg-prod-database-001`
   - Verify it was created with correct tags

5. **Verify in GitHub:**
   - Go to your GitHub organization
   - Find the new repository: `rg-prod-database-001`
   - Check it has README, .gitignore, etc.

---

## 🔍 Step 5: Monitor and Debug

### View Backend Logs

```bash
# View recent logs
az containerapp logs show \
  --name azure-tracker-backend \
  --resource-group rg-azure-resources-tracker \
  --tail 50

# Follow logs in real-time
az containerapp logs show \
  --name azure-tracker-backend \
  --resource-group rg-azure-resources-tracker \
  --follow
```

### View Frontend Logs

```bash
az containerapp logs show \
  --name azure-tracker-frontend \
  --resource-group rg-azure-resources-tracker \
  --tail 50
```

### Check Azure Portal

1. Go to [Azure Portal](https://portal.azure.com)
2. Navigate to your resource group: `rg-azure-resources-tracker`
3. Check:
   - Container Apps are running (green status)
   - CPU/Memory usage
   - Request count
   - Error rates

### Check Application Insights (if configured)

1. In Azure Portal → Application Insights
2. View:
   - Request telemetry
   - Exceptions
   - Dependencies
   - Performance metrics

---

## 🧩 Testing Scenarios

### Scenario 1: Successful Creation

**Input:**
- ResourceGroupName: `rg-test-success-001`
- ProjectName: Valid project name
- All required fields filled

**Expected:**
- ✅ Status: Completed
- ✅ Azure RG created
- ✅ GitHub repo created
- ✅ URLs populated

### Scenario 2: Duplicate Resource Group

**Input:**
- ResourceGroupName: `rg-test-success-001` (already exists)

**Expected:**
- ❌ Status: Failed
- ❌ ErrorMessage: "Resource group already exists"

### Scenario 3: Invalid Permissions

**Input:**
- ResourceGroupName: `rg-test-noperm-001`
- User lacks Azure permissions

**Expected:**
- ❌ Status: Failed
- ❌ ErrorMessage: "Authorization failed" or similar

### Scenario 4: GitHub API Rate Limit

**Input:**
- Multiple rapid requests

**Expected:**
- ❌ Status: Failed
- ❌ ErrorMessage: "GitHub API rate limit exceeded"

---

## 📊 What to Check in SharePoint

### View All Requests

1. Go to SharePoint list
2. All items view shows:
   - All requests with their status
   - Color coding by status (if configured)
   - Last modified date

### View Pending Requests

1. Create a view filtered by `Status = Pending`
2. Shows requests waiting to be processed

### View Failed Requests

1. Create a view filtered by `Status = Failed`
2. Check ErrorMessage column for details
3. Fix issues and retry

### View Completed Requests

1. Create a view filtered by `Status = Completed`
2. Click on GitHubRepoUrl to open repositories
3. Verify AzureResourceGroupId matches Azure Portal

---

## 🎯 Success Checklist

After testing, verify:

- [ ] Backend API responds to health checks
- [ ] API documentation accessible at `/docs`
- [ ] Frontend loads without errors
- [ ] SharePoint list created with all columns
- [ ] Can add items to SharePoint list
- [ ] Backend processes SharePoint items
- [ ] Azure resource groups created successfully
- [ ] GitHub repositories created successfully
- [ ] SharePoint items updated with results
- [ ] Error handling works (try invalid inputs)
- [ ] Logs are accessible and informative

---

## 🐛 Common Issues

### Backend Not Responding

**Symptoms:** 502/503 errors when accessing backend URL

**Fix:**
```bash
# Check if app is running
az containerapp show \
  --name azure-tracker-backend \
  --resource-group rg-azure-resources-tracker \
  --query "properties.runningStatus"

# Restart if needed
az containerapp revision restart \
  --name azure-tracker-backend \
  --resource-group rg-azure-resources-tracker
```

### SharePoint Not Updating

**Symptoms:** Items stay in "Pending" status

**Possible causes:**
1. SharePoint credentials not configured in backend env vars
2. SharePoint list name mismatch
3. Backend not polling or webhook not configured

**Fix:**
- Check backend logs for SharePoint errors
- Verify `SHAREPOINT_*` environment variables
- Test SharePoint connection via API

### Azure Resources Not Created

**Symptoms:** Status shows "Completed" but no Azure RG

**Possible causes:**
1. Azure credentials invalid
2. Insufficient permissions
3. Subscription ID wrong

**Fix:**
- Check `AZURE_*` environment variables
- Verify service principal has Contributor role
- Test Azure connection via API

### GitHub Repos Not Created

**Symptoms:** Status shows "Completed" but no GitHub repo

**Possible causes:**
1. GitHub token invalid or expired
2. Token lacks `repo` scope
3. Organization name wrong

**Fix:**
- Generate new GitHub token
- Verify token has correct scopes
- Test GitHub connection via API

---

## 📚 Additional Resources

- **API Documentation:** `https://your-backend-url/docs`
- **SharePoint Setup:** See [SHAREPOINT_SETUP.md](SHAREPOINT_SETUP.md)
- **Deployment Guide:** See [AUTOMATED_DEPLOYMENT.md](AUTOMATED_DEPLOYMENT.md)
- **Azure Portal:** https://portal.azure.com
- **Azure Container Apps Docs:** https://docs.microsoft.com/azure/container-apps

---

## 🎉 Next Steps

Once testing is complete:

1. **Configure Production Settings**
   - Use Azure Key Vault for secrets
   - Set up proper CORS origins
   - Enable authentication/authorization

2. **Set Up Monitoring**
   - Configure Application Insights
   - Set up alerts for failures
   - Create dashboard for metrics

3. **Train Users**
   - Create user guide for SharePoint
   - Document naming conventions
   - Explain approval processes

4. **Implement Governance**
   - Resource tagging policies
   - Budget alerts
   - Access controls

5. **Automate Further**
   - Set up CI/CD pipeline
   - Implement automatic testing
   - Configure backup/disaster recovery

---

**Your Azure Resources Tracker is ready for use!** 🚀
