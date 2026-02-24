# SharePoint List Template - Multi-Cloud Resources

## Quick Reference Card for Users

### What This List Does
Submit requests to automatically create cloud resources in Azure, GCP, or AWS with optional GitHub repositories.

---

## How to Submit a Request

### For Azure Resource Group:
1. Click **+ New**
2. Fill in:
   - **UserName:** Your Name
   - **CloudPlatform:** Azure
   - **ResourceType:** Resource Group
   - **ResourceGroupName:** `rg-yourproject-dev`
   - **ProjectName:** Your Project Name
   - **SubscriptionId:** (optional - select from list)
   - **Location:** eastus, westus, etc.
   - **CreateGitHubRepo:** Yes/No
   - **Tags:** (optional) `Environment:Dev, Team:Engineering`
3. Click **Save**
4. Wait 2-3 minutes, refresh page
5. Check **Status** column - should change to "Completed"
6. Check **ResourceId** and **GitHubRepoUrl** columns for results

### For GCP Project:
1. Click **+ New**
2. Fill in:
   - **UserName:** Your Name
   - **CloudPlatform:** GCP
   - **ResourceType:** Project
   - **ResourceGroupName:** `my-project-123` (lowercase, 6-30 chars)
   - **ProjectName:** My Project Display Name
   - **CreateGitHubRepo:** Yes/No
3. Click **Save**

### For AWS Account:
1. Click **+ New**
2. Fill in:
   - **UserName:** Your Name
   - **CloudPlatform:** AWS
   - **ResourceType:** Account
   - **ResourceGroupName:** `my-aws-account`
   - **ProjectName:** Account Display Name
   - **Tags:** `email:your.email@company.com` (REQUIRED)
   - **CreateGitHubRepo:** Yes/No
3. Click **Save**

---

## Status Meanings

| Status | Meaning |
|--------|---------|
| **Pending** | Request submitted, waiting for processing |
| **In Progress** | Resources are being created right now |
| **Completed** | ✅ Success! Resources created. Check ResourceId and GitHubRepoUrl columns |
| **Failed** | ❌ Something went wrong. Check ErrorMessage column for details |

---

## Column Guide

### Fields You Fill Out:

| Column | Required | Description | Examples |
|--------|----------|-------------|----------|
| **UserName** | Yes | Your full name | John Doe |
| **CloudPlatform** | Yes | Where to create | Azure, GCP, AWS |
| **ResourceType** | Yes | What to create | Resource Group, Project, Account |
| **ResourceGroupName** | Yes | Resource identifier | `rg-myapp-dev`, `my-gcp-project` |
| **ProjectName** | Yes | Human-readable name | My Application Dev Environment |
| **SubscriptionId** | No | Azure subscription (leave blank for default) | |
| **Location** | No | Azure region only | eastus, westus |
| **CreateGitHubRepo** | No | Want a GitHub repo? | Yes/No (default: No) |
| **Tags** | No | Additional metadata | `Environment:Dev, Team:Platform` |
| **DateOfCreation** | Auto | Auto-filled with today's date | |
| **Status** | Auto | Set to "Pending" | Pending |

### Fields Automatically Filled:

| Column | Description |
|--------|-------------|
| **ResourceId** | Cloud resource ID (Azure RG, GCP Project, AWS Account) |
| **AzureResourceGroupId** | Legacy - Azure RG ID |
| **GitHubRepoUrl** | Link to created GitHub repo (if requested) |
| **ErrorMessage** | Error details if Status = Failed |

---

## Naming Rules

### Azure Resource Group Names:
- ✅ Letters, numbers, hyphens, underscores, periods, parentheses
- ✅ 1-90 characters
- ✅ Can't end with period
- ✅ Examples: `rg-webapp-prod`, `rg_data_dev`, `rg.test.001`

### GCP Project IDs:
- ✅ Lowercase letters, numbers, hyphens
- ✅ 6-30 characters
- ✅ Must start with letter
- ✅ Examples: `my-project-123`, `data-platform-dev`

### AWS Account Names:
- ✅ Any characters
- ✅ Used for identification only
- ✅ Examples: `Production Account`, `Development-Team-1`

---

## Tags Format

Tags are optional key-value pairs. Format: `key:value, key:value`

**Examples:**
- `Environment:Production, Cost Center:IT-001`
- `Owner:John Doe, Team:Platform Engineering`
- `Application:WebApp, Version:v2.0`

**For AWS accounts, you MUST include:**
- `email:your.email@company.com`

---

## Troubleshooting

### Request Stuck in "Pending"
- Wait 5 minutes and refresh
- If still pending after 10 minutes, contact admin
- Admin can check backend logs

### Status Changed to "Failed"
- Look at **ErrorMessage** column
- Common errors:
  - **Name already exists:** Choose a different name
  - **Invalid name format:** Check naming rules above
  - **Permission denied:** Contact admin - credentials may be missing
  - **GCP/AWS not available:** Service not configured yet

### Error: "Unauthorized" or "Access Denied"
- You may not have permission to create items
- Contact list admin to grant Contribute permission

### GitHub Repo Not Created
- Check **GitHubRepoUrl** column - might be empty if:
  - CreateGitHubRepo was set to "No"
  - GitHub org is full (rare)
  - Repo name already exists
- Check **ErrorMessage** for details

---

## Tips

### Best Practices:
1. **Use descriptive names** - Include project/app name and environment
2. **Add tags** - Helps with cost tracking and organization
3. **Check existing resources** - Don't create duplicates
4. **Use standard naming** - Follow your team's conventions
5. **Request GitHub repos** - Good for tracking and documentation

### Standard Naming Conventions:
```
Azure:     rg-{project}-{environment}
           Example: rg-webapp-dev, rg-api-prod

GCP:       {company}-{project}-{environment}
           Example: acme-webapp-dev

AWS:       {Team} {Environment} Account
           Example: Platform Engineering Dev Account
```

### Commonly Used Locations:
- **East US** - Primary region for most US workloads
- **West Europe** - Primary for European workloads
- **Southeast Asia** - Primary for APAC workloads

---

## Need Help?

Contact your cloud platform admin or DevOps team.

Include in your message:
- Link to the SharePoint item
- What you were trying to create
- Error message from ErrorMessage column (if failed)
- Screenshot of the form you filled out

---

## Webhook Renewal Reminder (For Admins)

SharePoint webhooks expire every 6 months. If requests stop processing automatically:

```powershell
# Check webhook expiration
Connect-PnPOnline -Url "https://yourtenant.sharepoint.com/sites/yoursite" -Interactive
Get-PnPWebhookSubscriptions -List "Multi-Cloud Resources"

# Renew webhook
Add-PnPWebhookSubscription `
  -List "Multi-Cloud Resources" `
  -NotificationUrl "https://azure-tracker-backend.victoriousbeach-6b7a8fbc.eastus.azurecontainerapps.io/api/webhook/sharepoint" `
  -ExpirationDate (Get-Date).AddMonths(6) `
  -ClientState "secure-random-string-123456"
```

---

**Happy provisioning! 🚀**
