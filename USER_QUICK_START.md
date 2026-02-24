# Quick Start: Request Cloud Resources via SharePoint

## 📍 SharePoint List URL
**https://netorgft1612603.sharepoint.com/sites/devops/Lists/Multi-Cloud%20Resource%20Requests**

---

## 🚀 How to Create a Resource

### Step 1: Click **+ New**

### Step 2: Fill out the form

| Field | What to Enter |
|-------|---------------|
| **Title** | Brief description (e.g., "Dev environment for Project X") |
| **CloudPlatform** | Select: **Azure**, **GCP**, or **AWS** |
| **ResourceType** | Azure → **Resource Group**<br>GCP → **Project**<br>AWS → **Account** |
| **ResourceName** | Azure: `rg-project-env` (e.g., `rg-webapp-dev`)<br>GCP: `project-name-123`<br>AWS: Any name |
| **AzureSubscription** | (Azure only) Select: **ZCS Admin** or **ZionAi Projects** |
| **Location** | (Azure only) e.g., `eastus`, `westus` |
| **GithubRepo** | **Yes** if you want a GitHub repo |
| **Tags** | Optional: `Team:Engineering, Environment:Dev` |
| **Status** | Leave as **Pending** |

### Step 3: Click **Save**

### Step 4: Wait 2-3 minutes and refresh

### Step 5: Check results
- **Status = Completed** ✅ Success! Check **ResourceId**
- **Status = Failed** ❌ Check **ErrorMessage**

---

## 📋 Examples

### Azure Resource Group
- Title: `Web App Development Environment`
- CloudPlatform: `Azure`
- ResourceType: `Resource Group`
- ResourceName: `rg-webapp-dev`
- AzureSubscription: `ZCS Admin`
- Location: `eastus`
- GithubRepo: `Yes`

### GCP Project
- Title: `Data Pipeline Project`
- CloudPlatform: `GCP`
- ResourceType: `Project`
- ResourceName: `data-pipeline-2026`
- GithubRepo: `Yes`

### AWS Account
- Title: `Testing Account`
- CloudPlatform: `AWS`
- ResourceType: `Account`
- ResourceName: `test-account-team-a`
- Tags: `email:your.email@company.com`

---

## ✅ Naming Rules

### Azure Resource Groups
- ✅ Letters, numbers, hyphens, underscores
- ✅ 1-90 characters
- ✅ Examples: `rg-webapp-prod`, `rg-data-dev`

### GCP Projects
- ✅ Lowercase letters, numbers, hyphens
- ✅ 6-30 characters, start with letter
- ✅ Examples: `my-project-123`, `data-platform-dev`

### AWS Accounts
- ✅ Any characters
- ✅ Examples: `Production Account`, `Dev-Team-1`

---

## 🔍 Track Your Requests

### View All Your Requests
Click **My Requests** view in the SharePoint list

### Check Status
- **Pending** = Waiting to be processed
- **Creating** = Being created right now
- **Completed** = ✅ Done! Resource created
- **Failed** = ❌ Error (check ErrorMessage column)

---

## ❓ Troubleshooting

### My request is stuck on "Pending"
Contact IT support - the automation may need attention

### Status changed to "Failed"
Check the **ErrorMessage** column for details:
- "Name already exists" → Try a different name
- "Invalid name" → Check naming rules above
- "Permission denied" → Contact admin

### GitHub repo not created
- Make sure **GithubRepo** was set to **Yes**
- Check **GitHubRepoUrl** column for the link

---

## 📊 What You Get

### Azure Resource Group
- ✅ Resource group in selected subscription
- ✅ ResourceId shows the full Azure resource ID
- ✅ Optional GitHub repo

### GCP Project
- ✅ New GCP project
- ✅ ResourceId shows the project ID
- ✅ Optional GitHub repo

### AWS Account
- ✅ New AWS account (via Organizations)
- ✅ ResourceId shows the account ID
- ✅ Optional GitHub repo

---

## 📞 Need Help?

Contact your cloud platform admin or DevOps team.

Include:
- Link to your SharePoint request
- What you're trying to create
- Error message (if any)

---

**Happy provisioning! 🎉**
