# SharePoint Setup - Simplified Approach (No Admin Needed!)

## ✅ This Method Uses:
- SharePoint List (input form)
- Power Automate (connects to backend)
- Backend API (creates resources)
- Web Dashboard (shows results)

**No app registration or admin approval required!**

---

## Step 1: Create SharePoint List

1. Go to: **https://netorgft1612603.sharepoint.com/sites/devops**

2. Click **+ New** → **List**

3. Name: **Multi-Cloud Resources**

4. Click **Create**

5. Add these columns (click **+ Add column** after each):

### Required Columns (must create):

| # | Column Name | Type | Settings |
|---|-------------|------|----------|
| 1 | **UserName** | Single line of text | Required: Yes |
| 2 | **CloudPlatform** | Choice | Choices: `Azure`, `GCP`, `AWS`<br>Default: `Azure`<br>Required: Yes |
| 3 | **ResourceType** | Choice | Choices: `Resource Group`, `Project`, `Account`<br>Default: `Resource Group`<br>Required: Yes |
| 4 | **ResourceGroupName** | Single line of text | Required: Yes |
| 5 | **ProjectName** | Single line of text | Required: Yes |
| 6 | **SubscriptionId** | Single line of text | Required: No |
| 7 | **Location** | Single line of text | Required: No |
| 8 | **CreateGitHubRepo** | Yes/No | Default: No |
| 9 | **Tags** | Multiple lines of text | Required: No |
| 10 | **Status** | Choice | Choices: `Pending`, `In Progress`, `Completed`, `Failed`<br>Default: `Pending`<br>Required: Yes |
| 11 | **ResourceId** | Single line of text | Required: No |
| 12 | **GitHubRepoUrl** | Hyperlink | Required: No |
| 13 | **ErrorMessage** | Multiple lines of text | Required: No |

---

## Step 2: Create Power Automate Flow

1. Go to: **https://make.powerautomate.com**

2. Click **+ Create** → **Automated cloud flow**

3. Name: **Multi-Cloud Resource Provisioner**

4. Trigger: **When an item is created** (SharePoint)

5. Click **Create**

6. Configure trigger:
   - **Site Address**: `https://netorgft1612603.sharepoint.com/sites/devops`
   - **List Name**: `Multi-Cloud Resources`

7. Click **+ New step** → **Condition**

8. Configure condition:
   - **Field**: Status (from Dynamic content)
   - **is equal to**: `Pending`

### If YES Branch:

9. Click **Add an action** → **HTTP**

10. Configure HTTP action:
```
Method: POST
URI: https://azure-tracker-backend.victoriousbeach-6b7a8fbc.eastus.azurecontainerapps.io/api/resources

Headers:
Content-Type: application/json

Body:
{
  "name": "@{triggerOutputs()?['body/ResourceGroupName']}",
  "cloud_platform": "@{triggerOutputs()?['body/CloudPlatform']}",
  "resource_type": "@{triggerOutputs()?['body/ResourceType']}",
  "location": "@{triggerOutputs()?['body/Location']}",
  "subscription_id": "@{triggerOutputs()?['body/SubscriptionId']}",
  "tags": "@{triggerOutputs()?['body/Tags']}",
  "create_github_repo": @{triggerOutputs()?['body/CreateGitHubRepo']},
  "project_name": "@{triggerOutputs()?['body/ProjectName']}"
}
```

11. Click **+ New step** → **Update item** (SharePoint)

12. Configure update:
   - **Site Address**: `https://netorgft1612603.sharepoint.com/sites/devops`
   - **List Name**: `Multi-Cloud Resources`
   - **Id**: ID (from Dynamic content)
   - **Status**: `Completed`
   - **ResourceId**: (from HTTP response body - add dynamic content)

13. Add **Parallel Branch** for error handling:
    - Action: **Update item**
    - Configure run after: **has failed**
    - **Status**: `Failed`
    - **ErrorMessage**: @{body('HTTP')?['error']}

14. Click **Save**

---

## Step 3: Test It!

1. Go to your SharePoint list:
   ```
   https://netorgft1612603.sharepoint.com/sites/devops/Lists/Multi-Cloud%20Resources
   ```

2. Click **+ New**

3. Fill in:
   - **UserName**: Likhitha Singam
   - **CloudPlatform**: Azure
   - **ResourceType**: Resource Group
   - **ResourceGroupName**: `rg-test-powerautomate-001`
   - **ProjectName**: Test Power Automate
   - **Location**: eastus
   - **Status**: Pending
   - **CreateGitHubRepo**: No

4. Click **Save**

5. Wait 1-2 minutes

6. Refresh the list

7. ✅ Status should change to **Completed**!

8. Check **ResourceId** column for the created resource

---

## Alternative: Use Web Dashboard

If you prefer, your team can also use the web dashboard directly:

**URL**: https://azure-tracker-frontend.victoriousbeach-6b7a8fbc.eastus.azurecontainerapps.io

This shows:
- All created resources
- Real-time status updates
- Search and filtering
- GitHub repo links

---

## Benefits of This Approach

✅ **No admin approval needed**  
✅ **No complex app registration**  
✅ **Power Automate is visual and easy**  
✅ **SharePoint users stay in SharePoint**  
✅ **Results shown in both SharePoint and Web Dashboard**  
✅ **Automatic error handling**  

---

## Troubleshooting

### Power Automate flow fails
- Check HTTP action configuration
- Verify backend URL is correct
- Check backend logs: `az containerapp logs show --name azure-tracker-backend --resource-group rg-azure-resources-tracker --follow`

### Status stays "Pending"
- Check if Power Automate flow ran (go to flow → Run history)
- Verify trigger condition (Status = Pending)
- Check if HTTP action succeeded

### Resource not created
- Check backend logs for errors
- Verify Azure subscription permissions
- Check ResourceGroupName follows naming rules

---

**Next**: Create the SharePoint list following Step 1, then set up Power Automate in Step 2!
