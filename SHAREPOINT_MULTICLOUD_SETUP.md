# SharePoint Multi-Cloud Resource Tracker Setup Guide

This guide will help you set up a SharePoint list where users can request cloud resources across Azure, GCP, and AWS without needing access to the web UI.

## Overview

Users will:
1. Add items to a SharePoint list
2. Select cloud platform (Azure/GCP/AWS)
3. Select resource type (Resource Group/Project/Account)
4. Fill in resource details
5. Optionally request GitHub repo creation
6. Backend automatically creates resources and updates status

---

## Part 1: Create SharePoint List

### Step 1: Create the List

1. Navigate to your SharePoint site
2. Click **"New"** → **"List"**
3. Name it: `Multi-Cloud Resources` (or any name you prefer)
4. Description: "Multi-cloud resource provisioning requests"
5. Click **"Create"**

### Step 2: Add Custom Columns

Add these columns in order (click **"+ Add column"** each time):

#### 1. **UserName**
- **Type:** Single line of text
- **Name:** `UserName`
- **Description:** Name of the user requesting resources
- **Required:** Yes

#### 2. **CloudPlatform**
- **Type:** Choice
- **Name:** `CloudPlatform`
- **Description:** Cloud platform to create resources in
- **Required:** Yes
- **Choices:**
  - Azure
  - GCP
  - AWS
- **Default:** Azure

#### 3. **ResourceType**
- **Type:** Choice
- **Name:** `ResourceType`
- **Description:** Type of resource to create
- **Required:** Yes
- **Choices:**
  - Resource Group
  - Project
  - Account
- **Default:** Resource Group

#### 4. **ResourceGroupName**
- **Type:** Single line of text
- **Name:** `ResourceGroupName`
- **Description:** Resource name (Azure RG / GCP Project ID / AWS Account Name)
- **Required:** Yes

#### 5. **ProjectName**
- **Type:** Single line of text
- **Name:** `ProjectName`
- **Description:** Human-readable project name
- **Required:** Yes

#### 6. **SubscriptionId**
- **Type:** Single line of text
- **Name:** `SubscriptionId`
- **Description:** Azure Subscription ID (optional for Azure)
- **Required:** No

#### 7. **Location**
- **Type:** Choice
- **Name:** `Location`
- **Description:** Azure region (only for Azure)
- **Required:** No
- **Choices:**
  - eastus
  - westus
  - centralus
  - northeurope
  - westeurope
  - southeastasia

#### 8. **CreateGitHubRepo**
- **Type:** Yes/No
- **Name:** `CreateGitHubRepo`
- **Description:** Also create a GitHub repository?
- **Default:** No

#### 9. **Tags**
- **Type:** Multiple lines of text
- **Name:** `Tags`
- **Description:** Additional tags (format: key:value, key:value)
- **Required:** No

#### 10. **DateOfCreation**
- **Type:** Date and Time
- **Name:** `DateOfCreation`
- **Description:** Request submission date
- **Format:** Date & Time
- **Default:** Today's date
- **Required:** Yes

#### 11. **Status**
- **Type:** Choice
- **Name:** `Status`
- **Description:** Request processing status
- **Required:** Yes
- **Choices:**
  - Pending
  - In Progress
  - Completed
  - Failed
- **Default:** Pending

#### 12. **ResourceId**
- **Type:** Single line of text
- **Name:** `ResourceId`
- **Description:** Cloud resource ID (auto-filled by backend)
- **Required:** No

#### 13. **AzureResourceGroupId**
- **Type:** Single line of text
- **Name:** `AzureResourceGroupId`
- **Description:** Legacy Azure RG ID (auto-filled)
- **Required:** No

#### 14. **GitHubRepoUrl**
- **Type:** Hyperlink
- **Name:** `GitHubRepoUrl`
- **Description:** GitHub repository URL (auto-filled)
- **Required:** No

#### 15. **ErrorMessage**
- **Type:** Multiple lines of text
- **Name:** `ErrorMessage`
- **Description:** Error details if creation failed
- **Required:** No
- **Number of lines:** 6

---

## Part 2: Configure List Views

### Default View (All Items)
Show these columns:
- Title (or ProjectName)
- CloudPlatform
- ResourceType
- UserName
- ResourceGroupName
- Status
- DateOfCreation
- GitHubRepoUrl

### Pending View
- **Filter:** Status equals "Pending"
- **Sort:** DateOfCreation (oldest first)

### Completed View
- **Filter:** Status equals "Completed"
- **Sort:** DateOfCreation (newest first)

### Failed View
- **Filter:** Status equals "Failed"
- Show: ErrorMessage column

### My Requests View
- **Filter:** Created By equals "[Me]"
- **Sort:** DateOfCreation (newest first)

---

## Part 3: Register SharePoint App

### Step 1: Create App Registration

1. Go to: `https://[yourtenant].sharepoint.com/_layouts/15/appregnew.aspx`
2. Click **"Generate"** next to Client Id
3. Click **"Generate"** next to Client Secret
4. Fill in:
   - **Title:** Multi-Cloud Resource Tracker
   - **App Domain:** `azurecontainerapps.io` (or your backend domain)
   - **Redirect URI:** `https://azure-tracker-backend.victoriousbeach-6b7a8fbc.eastus.azurecontainerapps.io/callback`
5. Click **"Create"**
6. **IMPORTANT:** Copy and save the **Client ID** and **Client Secret**

### Step 2: Grant Permissions

1. Go to: `https://[yourtenant].sharepoint.com/_layouts/15/appinv.aspx`
2. Paste the **Client ID** you just saved
3. Click **"Lookup"** - app details will populate
4. In **Permission Request XML**, paste:

```xml
<AppPermissionRequests AllowAppOnlyPolicy="true">
  <AppPermissionRequest Scope="http://sharepoint/content/sitecollection/web/list" Right="Manage" />
</AppPermissionRequests>
```

5. Click **"Create"**
6. Review the permissions and click **"Trust It"**

---

## Part 4: Update Backend Configuration

### Step 1: Update Environment Variables

Update your Azure Container App backend with SharePoint credentials:

```powershell
az containerapp update `
  --name azure-tracker-backend `
  --resource-group rg-azure-resources-tracker `
  --set-env-vars `
    "SHAREPOINT_ENABLED=true" `
    "SHAREPOINT_SITE_URL=https://[yourtenant].sharepoint.com/sites/[yoursite]" `
    "SHAREPOINT_LIST_NAME=Multi-Cloud Resources" `
    "SHAREPOINT_CLIENT_ID=[your-client-id]" `
    "SHAREPOINT_CLIENT_SECRET=[your-client-secret]"
```

Replace:
- `[yourtenant]` - Your Microsoft 365 tenant name
- `[yoursite]` - Your SharePoint site name
- `[your-client-id]` - Client ID from Step 3.1
- `[your-client-secret]` - Client Secret from Step 3.1

### Step 2: Verify Configuration

Check that the backend is running:
```powershell
az containerapp revision list `
  --name azure-tracker-backend `
  --resource-group rg-azure-resources-tracker `
  --query "[0].{Name:name,Active:properties.active,Status:properties.runningState}"
```

---

## Part 5: Set Up SharePoint Webhook (Automatic Processing)

### Option A: Using PnP PowerShell (Recommended)

1. Install PnP PowerShell:
```powershell
Install-Module -Name PnP.PowerShell -Scope CurrentUser
```

2. Connect to SharePoint:
```powershell
Connect-PnPOnline -Url "https://[yourtenant].sharepoint.com/sites/[yoursite]" -Interactive
```

3. Add webhook subscription:
```powershell
$webhookUrl = "https://azure-tracker-backend.victoriousbeach-6b7a8fbc.eastus.azurecontainerapps.io/api/webhook/sharepoint"
$clientState = "secure-random-string-123456"  # Match WEBHOOK_SECRET in backend

Add-PnPWebhookSubscription `
  -List "Multi-Cloud Resources" `
  -NotificationUrl $webhookUrl `
  -ExpirationDate (Get-Date).AddMonths(6) `
  -ClientState $clientState
```

4. Verify webhook:
```powershell
Get-PnPWebhookSubscriptions -List "Multi-Cloud Resources"
```

### Option B: Using REST API

```bash
# Get access token first (use appropriate method for your auth)
# Then create webhook:

POST https://[yourtenant].sharepoint.com/sites/[yoursite]/_api/web/lists/getbytitle('Multi-Cloud Resources')/subscriptions
Content-Type: application/json
Authorization: Bearer [access_token]

{
  "resource": "https://[yourtenant].sharepoint.com/sites/[yoursite]/_api/web/lists/getbytitle('Multi-Cloud Resources')",
  "notificationUrl": "https://azure-tracker-backend.victoriousbeach-6b7a8fbc.eastus.azurecontainerapps.io/api/webhook/sharepoint",
  "expirationDateTime": "2026-08-24T00:00:00Z",
  "clientState": "secure-random-string-123456"
}
```

### Webhook Renewal

SharePoint webhooks expire after 6 months. Set up automatic renewal:

1. The backend has a renewal endpoint: `/api/webhook/sharepoint/renew`
2. Set up a monthly Azure Logic App or scheduled task to call this endpoint
3. Or manually renew every 5 months using the PowerShell command above

---

## Part 6: Testing the Setup

### Test 1: Create Azure Resource Group

1. Go to your SharePoint list
2. Click **"+ New"**
3. Fill in:
   - **Title:** My Test Project
   - **UserName:** Your Name
   - **CloudPlatform:** Azure
   - **ResourceType:** Resource Group
   - **ResourceGroupName:** `rg-test-sharepoint-demo`
   - **ProjectName:** Test Project
   - **SubscriptionId:** (select from dropdown or leave default)
   - **Location:** eastus
   - **CreateGitHubRepo:** No (or Yes if you want a repo)
   - **Status:** Pending
4. Click **"Save"**

Expected behavior:
- Within 30 seconds, Status should change to "In Progress"
- Within 2-3 minutes, Status should change to "Completed"
- ResourceId and AzureResourceGroupId will be populated
- If GitHub repo was requested, GitHubRepoUrl will be populated

### Test 2: Create GCP Project

1. Click **"+ New"**
2. Fill in:
   - **CloudPlatform:** GCP
   - **ResourceType:** Project
   - **ResourceGroupName:** `my-gcp-project-123` (must be unique, lowercase, 6-30 chars)
   - **ProjectName:** My GCP Test Project
   - **CreateGitHubRepo:** Yes
3. Click **"Save"**

**Note:** GCP project creation requires GCP credentials configured in backend. If not configured, Status will change to "Failed" with error message.

### Test 3: Create AWS Account

1. Click **"+ New"**
2. Fill in:
   - **CloudPlatform:** AWS
   - **ResourceType:** Account
   - **ResourceGroupName:** `my-aws-account`
   - **ProjectName:** My AWS Test
   - **Tags:** `email:myemail@example.com` (required for AWS)
3. Click **"Save"**

**Note:** AWS account creation requires AWS Organizations API access. If not configured, will fail with error message.

---

## Part 7: User Instructions

### For End Users Creating Resources:

#### Creating an Azure Resource Group

1. Go to the SharePoint list
2. Click **"+ New"**
3. Fill in these **required** fields:
   - **UserName:** Your full name
   - **CloudPlatform:** Select "Azure"
   - **ResourceType:** Select "Resource Group"
   - **ResourceGroupName:** Enter your resource group name (e.g., `rg-myproject-dev`)
     - Use only letters, numbers, hyphens, underscores, periods
     - 1-90 characters
   - **ProjectName:** Human-readable project name
   - **Location:** Select Azure region (e.g., "eastus")
4. Optional fields:
   - **CreateGitHubRepo:** Check "Yes" if you want a GitHub repository
   - **Tags:** Add custom tags (format: `Environment:Dev, Team:Engineering`)
5. Leave **Status** as "Pending"
6. Click **"Save"**
7. Wait 2-3 minutes and refresh - Status will update

#### Creating a GCP Project

1. Click **"+ New"**
2. **CloudPlatform:** Select "GCP"
3. **ResourceType:** Select "Project"
4. **ResourceGroupName:** Enter project ID (6-30 lowercase characters, start with letter)
5. **ProjectName:** Display name for project
6. **CreateGitHubRepo:** Optional
7. Click **"Save"**

#### Creating an AWS Account

1. Click **"+ New"**
2. **CloudPlatform:** Select "AWS"
3. **ResourceType:** Select "Account"
4. **ResourceGroupName:** Account identifier
5. **ProjectName:** Account name
6. **Tags:** **Must include** `email:your.email@company.com`
7. Click **"Save"**

#### Checking Request Status

- **Pending:** Request submitted, waiting for processing
- **In Progress:** Resources are being created
- **Completed:** Success! Check ResourceId and GitHubRepoUrl columns
- **Failed:** Check ErrorMessage column for details

---

## Part 8: Permissions & Security

### List Permissions

Recommended permission setup:

1. **End Users:**
   - **Permission Level:** Contribute
   - **Can:** Create items, edit their own items, view all items
   - **Cannot:** Delete items, change list structure

2. **Team Leads/Managers:**
   - **Permission Level:** Edit
   - **Can:** Edit any item, approve/reject requests
   - **Cannot:** Delete list

3. **Admins:**
   - **Permission Level:** Full Control
   - **Can:** Manage everything

### Enable Item-Level Permissions

1. Go to List Settings → Advanced Settings
2. **Create and edit access:** "Create items and edit items that were created by the user"
3. **Read access:** "Read all items"
4. This ensures users can only edit their own requests

### Enable Versioning

1. Go to List Settings → Versioning settings
2. Check **"Create a version each time you edit an item"**
3. Keep at least 10 versions
4. This provides audit trail

---

## Part 9: Power Automate Enhancement (Optional)

### Add Email Notifications

Create a Power Automate flow:

**Trigger:** When an item is created or modified
**Condition:** Status equals "Completed" OR Status equals "Failed"
**Action:** Send email to Created By

Sample email:
```
Subject: Resource Request [Status] - [ProjectName]

Your resource request has been [Status].

Details:
- Cloud Platform: [CloudPlatform]
- Resource Type: [ResourceType]
- Resource Name: [ResourceGroupName]
- Status: [Status]

[If Completed]
Resource ID: [ResourceId]
GitHub Repo: [GitHubRepoUrl]

[If Failed]
Error: [ErrorMessage]
```

### Add Approval Workflow

1. **Trigger:** When item is created
2. **Action:** Start approval process
3. **If approved:** Leave Status as "Pending" (backend will process)
4. **If rejected:** Update Status to "Failed", add rejection reason

---

## Part 10: Monitoring & Maintenance

### Check Backend Logs

```powershell
az containerapp logs show `
  --name azure-tracker-backend `
  --resource-group rg-azure-resources-tracker `
  --follow
```

### Monitor Webhook Status

SharePoint webhooks need renewal every 6 months. Check expiration:

```powershell
Connect-PnPOnline -Url "https://[yourtenant].sharepoint.com/sites/[yoursite]" -Interactive
Get-PnPWebhookSubscriptions -List "Multi-Cloud Resources"
```

### Common Issues

#### Webhook Not Triggering
- Verify webhook exists: `Get-PnPWebhookSubscriptions`
- Check clientState matches WEBHOOK_SECRET in backend
- Ensure backend URL is accessible from SharePoint (must be HTTPS)
- Check backend logs for incoming webhook calls

#### Items Stuck in "Pending"
- Verify SHAREPOINT_ENABLED=true in backend
- Check SharePoint credentials (CLIENT_ID, CLIENT_SECRET)
- Manually trigger: Call `/api/webhook/sharepoint/manual-trigger/{item_id}`

#### "Unauthorized" Errors
- Re-grant app permissions in appin.aspx
- Verify client secret hasn't expired
- Check list name matches exactly

---

## Summary

You now have a SharePoint-based multi-cloud resource provisioning system where:

✅ Users submit requests via SharePoint list (no web UI access needed)
✅ Backend automatically processes requests via webhook
✅ Supports Azure, GCP, and AWS with appropriate credentials
✅ Optional GitHub repository creation
✅ Status tracking and error reporting
✅ Audit trail with versioning

**Your SharePoint is ready to provision cloud resources!** 🚀

For questions or issues, check the backend logs or SharePoint list ErrorMessage column.
