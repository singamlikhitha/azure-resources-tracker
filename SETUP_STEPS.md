# SharePoint Setup - Step-by-Step Guide
**Your Tenant:** netorgft1612603.sharepoint.com  
**Date:** February 24, 2026

---

## STEP 1: Create SharePoint List (Manual) ✋

1. Navigate to your SharePoint site:
   - Go to: **https://netorgft1612603.sharepoint.com/sites/[YOUR-SITE-NAME]**
   - Or create a new site if needed

2. Click **+ New** → **List**

3. Name the list: **Multi-Cloud Resources**

4. Click **Create**

5. Add the following 15 custom columns:

### Column 1: UserName
- Click **+ Add column** → **Single line of text**
- Name: `UserName`
- Required: Yes
- Click **Save**

### Column 2: CloudPlatform
- Click **+ Add column** → **Choice**
- Name: `CloudPlatform`
- Choices (one per line):
  ```
  Azure
  GCP
  AWS
  ```
- Default: `Azure`
- Required: Yes
- Click **Save**

### Column 3: ResourceType
- Click **+ Add column** → **Choice**
- Name: `ResourceType`
- Choices (one per line):
  ```
  Resource Group
  Project
  Account
  ```
- Default: `Resource Group`
- Required: Yes
- Click **Save**

### Column 4: ResourceGroupName
- Click **+ Add column** → **Single line of text**
- Name: `ResourceGroupName`
- Required: Yes
- Click **Save**

### Column 5: ProjectName
- Click **+ Add column** → **Single line of text**
- Name: `ProjectName`
- Required: Yes
- Click **Save**

### Column 6: SubscriptionId
- Click **+ Add column** → **Single line of text**
- Name: `SubscriptionId`
- Required: No
- Click **Save**

### Column 7: Location
- Click **+ Add column** → **Single line of text**
- Name: `Location`
- Required: No
- Click **Save**

### Column 8: CreateGitHubRepo
- Click **+ Add column** → **Yes/No**
- Name: `CreateGitHubRepo`
- Default: No
- Click **Save**

### Column 9: Tags
- Click **+ Add column** → **Multiple lines of text**
- Name: `Tags`
- Required: No
- Type: Plain text
- Click **Save**

### Column 10: DateOfCreation
- Click **+ Add column** → **Date and time**
- Name: `DateOfCreation`
- Include time: Yes
- Default: Today's date
- Click **Save**

### Column 11: Status
- Click **+ Add column** → **Choice**
- Name: `Status`
- Choices (one per line):
  ```
  Pending
  In Progress
  Completed
  Failed
  ```
- Default: `Pending`
- Required: Yes
- Click **Save**

### Column 12: ResourceId
- Click **+ Add column** → **Single line of text**
- Name: `ResourceId`
- Required: No
- Click **Save**

### Column 13: AzureResourceGroupId
- Click **+ Add column** → **Single line of text**
- Name: `AzureResourceGroupId`
- Required: No
- Click **Save**

### Column 14: GitHubRepoUrl
- Click **+ Add column** → **Hyperlink**
- Name: `GitHubRepoUrl`
- Format: Hyperlink
- Required: No
- Click **Save**

### Column 15: ErrorMessage
- Click **+ Add column** → **Multiple lines of text**
- Name: `ErrorMessage`
- Required: No
- Type: Plain text
- Click **Save**

✅ **STEP 1 COMPLETE!** Your list now has all 15 columns.

---

## STEP 2: Register SharePoint App 🔐

1. Open this URL in your browser (you must be SharePoint admin):
   ```
   https://netorgft1612603.sharepoint.com/_layouts/15/appregnew.aspx
   ```

2. Click **Generate** button next to **Client Id** (copy the value)

3. Click **Generate** button next to **Client Secret** (copy the value)

4. Fill in the form:
   - **Title:** `Multi-Cloud Resource Provisioner`
   - **App Domain:** `victoriousbeach-6b7a8fbc.eastus.azurecontainerapps.io`
   - **Redirect URI:** `https://victoriousbeach-6b7a8fbc.eastus.azurecontainerapps.io`

5. Click **Create**

6. **IMPORTANT:** Save these values securely (you'll need them later):
   ```
   Client Id: [YOUR-CLIENT-ID]
   Client Secret: [YOUR-CLIENT-SECRET]
   ```

✅ **STEP 2 COMPLETE!** Your app is registered.

---

## STEP 3: Grant App Permissions 🔓

1. Open this URL in your browser:
   ```
   https://netorgft1612603.sharepoint.com/_layouts/15/appinv.aspx
   ```

2. In **App Id** field, paste your **Client Id** from Step 2

3. Click **Lookup**

4. The form should auto-fill with your app details

5. In **Permission Request XML** box, paste this exactly:
   ```xml
   <AppPermissionRequests AllowAppOnlyPolicy="true">
     <AppPermissionRequest Scope="http://sharepoint/content/sitecollection/web/list" 
                           Right="Manage"/>
   </AppPermissionRequests>
   ```

6. Click **Create**

7. Click **Trust It** on the confirmation page

✅ **STEP 3 COMPLETE!** Your app has permissions.

---

## STEP 4: Install PnP PowerShell Module 📦

Open PowerShell as Administrator and run:

```powershell
Install-Module -Name PnP.PowerShell -Force -AllowClobber
```

If prompted, type **Y** to accept.

✅ **STEP 4 COMPLETE!** PnP PowerShell is installed.

---

## STEP 5: Run the Setup Script 🚀

1. Open the file: `setup-sharepoint.ps1` in this folder

2. Update these values at the top:
   ```powershell
   $SiteUrl = "https://netorgft1612603.sharepoint.com/sites/[YOUR-SITE-NAME]"
   $ListName = "Multi-Cloud Resources"
   $BackendUrl = "https://azure-tracker-backend.victoriousbeach-6b7a8fbc.eastus.azurecontainerapps.io"
   $SharePointClientId = "[YOUR-CLIENT-ID-FROM-STEP-2]"
   $SharePointClientSecret = "[YOUR-CLIENT-SECRET-FROM-STEP-2]"
   $WebhookSecret = "secure-random-string-$(Get-Random)-$(Get-Date -Format 'yyyyMMddHHmmss')"
   ```

3. Save the file

4. Open PowerShell (regular, not admin needed)

5. Navigate to the folder:
   ```powershell
   cd "C:\Users\LikhithaReddySingam\OneDrive\azure-resources-tracker"
   ```

6. Run the script:
   ```powershell
   .\setup-sharepoint.ps1
   ```

7. When prompted, sign in to SharePoint with your admin account

8. The script will:
   - ✅ Verify your list has all required columns
   - ✅ Create webhook subscription
   - ✅ Update backend environment variables
   - ✅ Provide summary

✅ **STEP 5 COMPLETE!** Webhook is configured and backend is updated.

---

## STEP 6: Test the Integration 🧪

1. Go to your SharePoint list:
   ```
   https://netorgft1612603.sharepoint.com/sites/[YOUR-SITE-NAME]/Lists/Multi-Cloud%20Resources
   ```

2. Click **+ New**

3. Fill in the form:
   - **UserName:** `Likhitha Singam`
   - **CloudPlatform:** `Azure`
   - **ResourceType:** `Resource Group`
   - **ResourceGroupName:** `rg-test-sharepoint-001`
   - **ProjectName:** `SharePoint Integration Test`
   - **SubscriptionId:** *(leave blank to use default)*
   - **Location:** `eastus`
   - **CreateGitHubRepo:** `No`
   - **Status:** `Pending`
   - **DateOfCreation:** *(auto-filled)*

4. Click **Save**

5. **Wait 2-3 minutes**

6. Refresh the page (F5)

7. Check the item:
   - **Status** should change to **Completed** ✅
   - **ResourceId** should show the Azure resource group ID
   - If **Status** = **Failed**, check **ErrorMessage**

✅ **STEP 6 COMPLETE!** Your SharePoint integration works!

---

## Troubleshooting 🔧

### Issue: "Access Denied" when registering app
**Solution:** You need SharePoint admin permissions. Contact your IT admin.

### Issue: Webhook not triggering (Status stays "Pending")
**Solution:** 
1. Check backend logs:
   ```powershell
   az containerapp logs show --name azure-tracker-backend --resource-group rg-azure-resources-tracker --follow
   ```
2. Verify webhook exists:
   ```powershell
   Connect-PnPOnline -Url "https://netorgft1612603.sharepoint.com/sites/[YOUR-SITE]" -Interactive
   Get-PnPWebhookSubscriptions -List "Multi-Cloud Resources"
   ```

### Issue: Backend not creating resources
**Solution:**
1. Check environment variables are set:
   ```powershell
   az containerapp show --name azure-tracker-backend --resource-group rg-azure-resources-tracker --query "properties.configuration.secrets" -o table
   ```
2. Verify `SHAREPOINT_ENABLED=true`

### Issue: "Column not found" error
**Solution:** Double-check all 15 columns are created exactly as specified (case-sensitive).

---

## What's Next? 🎯

### Share with Your Team
Send them the link to your SharePoint list and the user guide:
- **User Guide:** `SHAREPOINT_USER_GUIDE.md`
- **List URL:** `https://netorgft1612603.sharepoint.com/sites/[YOUR-SITE]/Lists/Multi-Cloud%20Resources`

### Set Up Views (Optional)
Create filtered views for easier navigation:

**Pending Requests View:**
```
Filter: Status = "Pending"
Sort: DateOfCreation (newest first)
```

**My Requests View:**
```
Filter: [Me] in UserName
Sort: DateOfCreation (newest first)
```

**Completed View:**
```
Filter: Status = "Completed"
Sort: DateOfCreation (newest first)
```

### Set Up Email Notifications (Optional)
Use Power Automate:
1. Trigger: When item Status changes to "Completed"
2. Action: Send email to UserName with ResourceId and GitHubRepoUrl

---

## Need Help? 💬

- Check logs: `az containerapp logs show --name azure-tracker-backend --resource-group rg-azure-resources-tracker --follow`
- Review docs: `SHAREPOINT_MULTICLOUD_SETUP.md` (detailed guide)
- Test manually: Use the backend API directly at `https://azure-tracker-backend.victoriousbeach-6b7a8fbc.eastus.azurecontainerapps.io/docs`

---

**Happy provisioning! 🚀**
