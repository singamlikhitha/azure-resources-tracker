# Complete SharePoint Setup Guide
## Multi-Cloud Resource Provisioning via SharePoint

### What This Does:
✅ Users submit forms in SharePoint  
✅ Power Automate automatically creates Azure/GCP/AWS resources  
✅ Results stored back in SharePoint with tracking  
✅ Azure users can select between 2 subscriptions  
✅ Full audit trail: who created what, when, where  

---

## Part 1: Create SharePoint List

### Step 1: Go to your SharePoint site
Navigate to: **https://netorgft1612603.sharepoint.com/sites/devops**

### Step 2: Create the list
1. Click **+ New** → **List**
2. Name: **Multi-Cloud Resource Requests**
3. Description: **Submit requests to create Azure, GCP, and AWS resources**
4. Click **Create**

### Step 3: Add these columns

Click **+ Add column** for each:

| Column Name | Type | Configuration |
|-------------|------|---------------|
| **CloudPlatform** | Choice | Choices: `Azure`, `GCP`, `AWS`<br>Default: Azure<br>**Required** |
| **ResourceType** | Choice | Choices: `Resource Group`, `Project`, `Account`<br>Default: Resource Group<br>**Required** |
| **ResourceName** | Single line of text | **Required** |
| **AzureSubscription** | Choice | Choices: `ZCS Admin`, `ZionAi Projects`<br>Default: ZCS Admin |
| **Location** | Single line of text | Placeholder: e.g., eastus, westus |
| **GithubRepo** | Yes/No | Default: No |
| **Tags** | Multiple lines of text | |
| **Status** | Choice | Choices: `Pending`, `Creating`, `Completed`, `Failed`<br>Default: Pending<br>**Required** |
| **ResourceId** | Single line of text | |
| **GitHubRepoUrl** | Hyperlink | |
| **ErrorMessage** | Multiple lines of text | |
| **CreatedDate** | Date and Time | Default: Today's date |

### Step 4: Configure list settings
1. Click **⚙️ List settings**
2. Under **General Settings** → **Title** → **Change to "Request Description"**
3. Make Title optional (uncheck Required)

---

## Part 2: Set Up Power Automate Flow

### Step 1: Create the flow
1. Go to: **https://make.powerautomate.com**
2. Click **+ Create** → **Automated cloud flow**
3. Flow name: **Multi-Cloud Resource Provisioner**
4. Trigger: **When an item is created** (SharePoint)
5. Click **Create**

### Step 2: Configure the trigger
- **Site Address**: `https://netorgft1612603.sharepoint.com/sites/devops`
- **List Name**: `Multi-Cloud Resource Requests`

### Step 3: Add Condition
Click **+ New step** → **Condition**

**Condition**: Status is equal to `Pending`

### Step 4: In the "If yes" branch

#### Action 1: Update status to "Creating"
1. Click **Add an action** → **Update item** (SharePoint)
2. Configure:
   - **Site Address**: `https://netorgft1612603.sharepoint.com/sites/devops`
   - **List Name**: `Multi-Cloud Resource Requests`
   - **Id**: ID (from dynamic content)
   - **Title**: Title (from dynamic content)
   - **Status**: `Creating`

#### Action 2: Call Backend API
1. Click **Add an action** → **HTTP**
2. Configure:

```
Method: POST
URI: https://azure-tracker-backend.victoriousbeach-6b7a8fbc.eastus.azurecontainerapps.io/api/resources
```

**Headers**:
```
Content-Type: application/json
```

**Body** (copy this exactly):
```json
{
  "name": "@{triggerOutputs()?['body/ResourceName']}",
  "cloud_platform": "@{triggerOutputs()?['body/CloudPlatform']?['Value']}",
  "resource_type": "@{if(equals(triggerOutputs()?['body/ResourceType']?['Value'], 'Resource Group'), 'AZURE_RESOURCE_GROUP', if(equals(triggerOutputs()?['body/ResourceType']?['Value'], 'Project'), 'GCP_PROJECT', 'AWS_ACCOUNT'))}",
  "location": "@{triggerOutputs()?['body/Location']}",
  "subscription_id": "@{if(equals(triggerOutputs()?['body/AzureSubscription']?['Value'], 'ZCS Admin'), 'e21901bf-488a-4ded-b169-b694737e4c86', if(equals(triggerOutputs()?['body/AzureSubscription']?['Value'], 'ZionAi Projects'), '5c5c5028-4a7e-435c-8430-6ece5f592ae2', ''))}",
  "tags": "@{triggerOutputs()?['body/Tags']}",
  "create_github_repo": @{triggerOutputs()?['body/GithubRepo']},
  "project_name": "@{coalesce(triggerOutputs()?['body/Title'], triggerOutputs()?['body/ResourceName'])}"
}
```

> **Your Subscription IDs**:
> - ZCS Admin: `e21901bf-488a-4ded-b169-b694737e4c86`
> - ZionAi Projects: `5c5c5028-4a7e-435c-8430-6ece5f592ae2`

#### Action 3: Update with Success Results
1. Click **Add an action** → **Update item** (SharePoint)
2. Configure:
   - **Site Address**: `https://netorgft1612603.sharepoint.com/sites/devops`
   - **List Name**: `Multi-Cloud Resource Requests`
   - **Id**: ID (from dynamic content)
   - **Title**: Title (from dynamic content)
   - **Status**: `Completed`
   - **ResourceId**: Click **Add dynamic content** → **Expression** → Enter:
     ```
     body('HTTP')?['resource_id']
     ```
   - **GitHubRepoUrl**: Click **Add dynamic content** → **Expression** → Enter:
     ```
     body('HTTP')?['github_repo_url']
     ```

#### Action 4: Add parallel branch for error handling
1. Click the **⋮** on the "Update item" action
2. Select **Configure run after**
3. Check **has failed** and **has timed out**
4. Click **Done**

5. Click **Add a parallel branch** → **Update item** (SharePoint)
6. Configure:
   - **Site Address**: `https://netorgft1612603.sharepoint.com/sites/devops`
   - **List Name**: `Multi-Cloud Resource Requests`
   - **Id**: ID (from dynamic content)
   - **Title**: Title (from dynamic content)
   - **Status**: `Failed`
   - **ErrorMessage**: Click **Add dynamic content** → **Expression** → Enter:
     ```
     if(equals(outputs('HTTP')?['statusCode'], 500), body('HTTP')?['detail'], concat('API Error: ', outputs('HTTP')?['statusCode']))
     ```

### Step 5: Save the flow
Click **Save** at the top

---

## Part 3: Get Your Azure Subscription IDs

If you need to find your actual subscription IDs:

```powershell
az account list --query "[].{Name:name, SubscriptionId:id}" -o table
```

Then update the Power Automate HTTP body with the correct IDs.

---

## Part 4: Test It!

### Test 1: Azure Resource Group
1. Go to: `https://netorgft1612603.sharepoint.com/sites/devops/Lists/Multi-Cloud%20Resource%20Requests`
2. Click **+ New**
3. Fill in:
   - **Title**: My First Test
   - **CloudPlatform**: Azure
   - **ResourceType**: Resource Group
   - **ResourceName**: `rg-test-sharepoint-001`
   - **AzureSubscription**: ZCS Admin
   - **Location**: eastus
   - **GithubRepo**: No
   - **Status**: Pending
4. Click **Save**
5. Wait 2-3 minutes
6. Refresh the page
7. ✅ Status should change to **Completed**
8. Check **ResourceId** column

### Test 2: GCP Project
1. Click **+ New**
2. Fill in:
   - **CloudPlatform**: GCP
   - **ResourceType**: Project
   - **ResourceName**: `my-gcp-test-123`
   - **GithubRepo**: Yes
   - **Status**: Pending
3. Click **Save**
4. Wait 2-3 minutes and check results

### Test 3: AWS Account
1. Click **+ New**
2. Fill in:
   - **CloudPlatform**: AWS
   - **ResourceType**: Account
   - **ResourceName**: `test-aws-account`
   - **Tags**: `email:your.email@example.com`
   - **GithubRepo**: No
   - **Status**: Pending
3. Click **Save**
4. Wait 2-3 minutes and check results

---

## Part 5: Create Custom Views

### View 1: Pending Requests
1. Click **⚙️** (gear icon) → **List settings**
2. Under **Views** → **Create view**
3. Name: **Pending Requests**
4. Filter: `Status is equal to Pending`
5. Sort by: **CreatedDate** (descending)
6. Select columns to show:
   - Title
   - CloudPlatform
   - ResourceType
   - ResourceName
   - AzureSubscription
   - Location
   - Status
   - Created By
   - CreatedDate

### View 2: My Requests
1. Create another view
2. Name: **My Requests**
3. Filter: `Created By is equal to [Me]`
4. Sort by: **CreatedDate** (descending)

### View 3: Completed
1. Create another view
2. Name: **Completed**
3. Filter: `Status is equal to Completed`
4. Sort by: **CreatedDate** (descending)
5. Include columns: ResourceId, GitHubRepoUrl

### View 4: Failed
1. Create another view
2. Name: **Failed**
3. Filter: `Status is equal to Failed`
4. Sort by: **CreatedDate** (descending)
5. Include columns: ErrorMessage

---

## Part 6: User Instructions

Share this with your team:

### How to Request a Cloud Resource

1. **Go to the SharePoint list**:
   https://netorgft1612603.sharepoint.com/sites/devops/Lists/Multi-Cloud%20Resource%20Requests

2. **Click + New**

3. **Fill out the form**:
   - **Title**: Brief description (e.g., "Dev environment for Project X")
   - **CloudPlatform**: Select Azure, GCP, or AWS
   - **ResourceType**: 
     - Azure → Resource Group
     - GCP → Project
     - AWS → Account
   - **ResourceName**: 
     - Azure: `rg-projectname-env` (e.g., `rg-webapp-dev`)
     - GCP: `project-name-123` (lowercase, 6-30 chars)
     - AWS: Any name
   - **AzureSubscription**: (Only for Azure) Select ZCS Admin or ZionAi Projects
   - **Location**: (Only for Azure) e.g., eastus, westus, eastus2
   - **GithubRepo**: Yes if you want a GitHub repo created
   - **Tags**: Optional (e.g., `Team:Engineering, Environment:Dev`)
   - **Status**: Leave as **Pending**

4. **Click Save**

5. **Wait 2-3 minutes** and refresh the page

6. **Check results**:
   - **Status** will change to:
     - `Creating` → Resource is being created right now
     - `Completed` → ✅ Done! Check **ResourceId** and **GitHubRepoUrl**
     - `Failed` → ❌ Error. Check **ErrorMessage**

### Naming Rules

**Azure Resource Groups**:
- Letters, numbers, hyphens, underscores, periods, parentheses
- 1-90 characters
- Examples: `rg-webapp-prod`, `rg-data-dev`

**GCP Projects**:
- Lowercase letters, numbers, hyphens
- 6-30 characters
- Must start with a letter
- Examples: `my-project-123`, `data-platform-dev`

**AWS Accounts**:
- Any characters allowed
- Examples: `Production Account`, `Dev-Team-1`

---

## Part 7: Tracking & Reporting

### View All Resources
Go to: `https://netorgft1612603.sharepoint.com/sites/devops/Lists/Multi-Cloud%20Resource%20Requests`

**Default view shows**:
- Who created (Created By column)
- When created (CreatedDate column)
- What platform (CloudPlatform)
- Resource details (ResourceName, ResourceId)
- Status
- GitHub repo (if created)

### Export to Excel
1. Click **Export to Excel** in the list toolbar
2. Generates report with all tracking data

### Create Dashboard
Use SharePoint web parts to create a dashboard page showing:
- Count by CloudPlatform
- Recent requests
- Failed requests
- Your requests

---

## Part 8: Troubleshooting

### Status stays "Pending"
- Check Power Automate run history: https://make.powerautomate.com
- Click on your flow → **Run history**
- Check if it triggered and where it failed

### Status changed to "Failed"
- Look at **ErrorMessage** column
- Common errors:
  - **Name already exists**: Choose different name
  - **Invalid name format**: Check naming rules above
  - **Subscription not found**: Select correct subscription for Azure
  - **Permission denied**: Backend may need credentials configured

### GCP/AWS returns error
- GCP/AWS may not be fully configured in backend yet
- Check backend logs:
  ```powershell
  az containerapp logs show --name azure-tracker-backend --resource-group rg-azure-resources-tracker --follow
  ```

### GitHub repo not created
- Check **GithubRepo** was set to Yes
- Check **GitHubRepoUrl** column for the link
- GitHub org may be full or repo name exists

---

## Part 9: Permissions

### Give users access to the list
1. Go to the SharePoint list
2. Click **⚙️** → **List settings**
3. Click **Permissions for this list**
4. Click **Grant Permissions**
5. Add users/groups with **Contribute** permission

---

## Part 10: Monitor Backend

### View backend logs
```powershell
az containerapp logs show --name azure-tracker-backend --resource-group rg-azure-resources-tracker --follow
```

### Check backend health
Open in browser: https://azure-tracker-backend.victoriousbeach-6b7a8fbc.eastus.azurecontainerapps.io/api/health

### View API documentation
Open in browser: https://azure-tracker-backend.victoriousbeach-6b7a8fbc.eastus.azurecontainerapps.io/docs

---

## Summary

✅ **SharePoint** = User interface for submitting requests  
✅ **Power Automate** = Automation engine connecting SharePoint to backend  
✅ **Backend API** = Creates actual cloud resources  
✅ **Results** = Automatically updated in SharePoint  
✅ **Tracking** = Full audit trail in SharePoint list  

**Your users never leave SharePoint!**

---

**Ready to start? Begin with Part 1: Create the SharePoint list!** 🚀
