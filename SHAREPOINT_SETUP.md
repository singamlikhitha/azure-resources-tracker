# SharePoint List Setup Guide

## Creating the SharePoint List

1. Navigate to your SharePoint site
2. Click **"New"** → **"List"**
3. Name it: `ResourceRequests`
4. Click **"Create"**

## Add Custom Columns

After creating the list, add these columns:

### 1. UserName
- **Type:** Single line of text
- **Required:** Yes
- Click **"+ Add column"** → **"Single line of text"**
- Name: `UserName`
- Description: `Name of the user requesting resources`

### 2. ResourceGroupName
- **Type:** Single line of text
- **Required:** Yes
- Name: `ResourceGroupName`
- Description: `Name for the Azure resource group`

### 3. ProjectName
- **Type:** Single line of text
- **Required:** Yes
- Name: `ProjectName`
- Description: `Associated project name`

### 4. DateOfCreation
- **Type:** Date and Time
- **Required:** Yes
- **Format:** Date & Time
- **Default:** Today's date
- Name: `DateOfCreation`

### 5. Status
- **Type:** Choice
- **Required:** Yes
- **Choices:**
  - Pending
  - In Progress
  - Completed
  - Failed
- **Default:** Pending
- Name: `Status`

### 6. AzureResourceGroupId
- **Type:** Single line of text
- **Required:** No
- Name: `AzureResourceGroupId`
- Description: `Azure resource group ID (auto-filled)`

### 7. GitHubRepoUrl
- **Type:** Hyperlink
- **Required:** No
- Name: `GitHubRepoUrl`
- Description: `GitHub repository URL (auto-filled)`

### 8. ErrorMessage
- **Type:** Multiple lines of text
- **Required:** No
- Name: `ErrorMessage`
- Description: `Error message if creation failed`

## Configure List Views

### All Items View
Show columns:
- Title / ProjectName
- UserName
- ResourceGroupName
- Status
- DateOfCreation

### Pending Items View
Filter: `Status` equals `Pending`

### Failed Items View
Filter: `Status` equals `Failed`

## Set Up Webhook (Optional)

### Create SharePoint App

1. Go to: `https://yoursite.sharepoint.com/_layouts/15/appregnew.aspx`
2. Click **"Generate"** for both Client ID and Secret
3. Fill:
   - **Title:** Azure Resources Tracker
   - **App Domain:** Your API domain (e.g., `api.yourdomain.com` or `localhost` for dev)
   - **Redirect URI:** `https://api.yourdomain.com/callback` or `https://localhost`
4. Click **"Create"**
5. Save the **Client ID** and **Client Secret**

### Grant Permissions

1. Go to: `https://yoursite.sharepoint.com/_layouts/15/appinv.aspx`
2. Enter the **Client ID** from previous step
3. Click **"Lookup"**
4. Paste this XML in **Permission Request XML**:

```xml
<AppPermissionRequests AllowAppOnlyPolicy="true">
  <AppPermissionRequest Scope="http://sharepoint/content/sitecollection/web/list" Right="Manage" />
</AppPermissionRequests>
```

5. Click **"Create"**
6. Click **"Trust It"** on the confirmation page

### Register Webhook

Use this PowerShell script or API call:

```powershell
$siteUrl = "https://yoursite.sharepoint.com/sites/yoursite"
$listName = "ResourceRequests"
$webhookUrl = "https://your-api-url/api/webhook/sharepoint"
$clientId = "your-client-id"
$clientSecret = "your-client-secret"

# Add webhook
Add-PnPWebhookSubscription -List $listName -NotificationUrl $webhookUrl -ClientState "your-random-string"
```

Or use the REST API:

```bash
POST https://yoursite.sharepoint.com/sites/yoursite/_api/web/lists/getbytitle('ResourceRequests')/subscriptions
Content-Type: application/json
Authorization: Bearer <access_token>

{
  "resource": "https://yoursite.sharepoint.com/sites/yoursite/_api/web/lists/getbytitle('ResourceRequests')",
  "notificationUrl": "https://your-api-url/api/webhook/sharepoint",
  "expirationDateTime": "2026-12-31T00:00:00Z",
  "clientState": "your-random-string"
}
```

## Test the List

1. Add a new item to the list:
   - **Title/ProjectName:** Test Project
   - **UserName:** John Doe
   - **ResourceGroupName:** rg-test-dev
   - **Status:** Pending

2. If webhook is configured, check your API logs
3. Watch the Status change from "Pending" → "In Progress" → "Completed"
4. Check that AzureResourceGroupId and GitHubRepoUrl are populated

## Permissions

Ensure users who will create items have:
- **Contribute** permission on the list
- Ability to view and edit their own items

For production, consider:
- Item-level permissions
- Approval workflows
- Version history enabled

---

**Your SharePoint list is ready!** 🎉
