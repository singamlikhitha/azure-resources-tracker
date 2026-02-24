# SharePoint Setup - Interactive Quick Start
# This script guides you through the entire setup process step-by-step

$TenantUrl = "https://netorgft1612603.sharepoint.com"
$BackendUrl = "https://azure-tracker-backend.victoriousbeach-6b7a8fbc.eastus.azurecontainerapps.io"

Write-Host "==========================================" -ForegroundColor Cyan
Write-Host "SharePoint Multi-Cloud Setup - Quick Start" -ForegroundColor Cyan
Write-Host "==========================================" -ForegroundColor Cyan
Write-Host ""
Write-Host "This wizard will help you set up SharePoint integration." -ForegroundColor White
Write-Host ""

# Step 1: Get Site Name
Write-Host "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━" -ForegroundColor Cyan
Write-Host "STEP 1: SharePoint Site" -ForegroundColor Yellow
Write-Host "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━" -ForegroundColor Cyan
Write-Host ""
Write-Host "Your tenant: $TenantUrl" -ForegroundColor White
Write-Host ""
$SiteName = Read-Host "Enter your site name (e.g., 'IT-Resources', 'DevOps', 'CloudOps')"

if ([string]::IsNullOrWhiteSpace($SiteName)) {
    Write-Host "❌ Site name is required. Exiting." -ForegroundColor Red
    exit
}

$SiteUrl = "$TenantUrl/sites/$SiteName"
Write-Host ""
Write-Host "✅ Site URL: $SiteUrl" -ForegroundColor Green
Write-Host ""

# Step 2: Check if PnP PowerShell is installed
Write-Host "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━" -ForegroundColor Cyan
Write-Host "STEP 2: Check Prerequisites" -ForegroundColor Yellow
Write-Host "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━" -ForegroundColor Cyan
Write-Host ""

$pnpModule = Get-Module -ListAvailable -Name PnP.PowerShell -ErrorAction SilentlyContinue

if (!$pnpModule) {
    Write-Host "⚠️  PnP.PowerShell module not found" -ForegroundColor Yellow
    Write-Host ""
    $installPnP = Read-Host "Do you want to install it now? (yes/no)"
    
    if ($installPnP -eq "yes") {
        Write-Host "Installing PnP.PowerShell module..." -ForegroundColor Yellow
        Install-Module -Name PnP.PowerShell -Scope CurrentUser -Force -AllowClobber
        Write-Host "✅ PnP.PowerShell installed" -ForegroundColor Green
    } else {
        Write-Host "❌ PnP.PowerShell is required. Please install it and run this script again." -ForegroundColor Red
        Write-Host "   Install command: Install-Module -Name PnP.PowerShell -Scope CurrentUser" -ForegroundColor White
        exit
    }
} else {
    Write-Host "✅ PnP.PowerShell module is installed" -ForegroundColor Green
}
Write-Host ""

# Step 3: Create SharePoint List
Write-Host "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━" -ForegroundColor Cyan
Write-Host "STEP 3: Create SharePoint List" -ForegroundColor Yellow
Write-Host "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━" -ForegroundColor Cyan
Write-Host ""
Write-Host "Option 1: Create list automatically (recommended)" -ForegroundColor White
Write-Host "Option 2: Create list manually in SharePoint UI" -ForegroundColor White
Write-Host ""
$createMethod = Read-Host "Choose option (1 or 2)"

if ($createMethod -eq "1") {
    Write-Host ""
    Write-Host "Running automated list creation script..." -ForegroundColor Yellow
    Write-Host ""
    
    # Update the create-sharepoint-list.ps1 with the site URL
    $createScriptPath = Join-Path $PSScriptRoot "create-sharepoint-list.ps1"
    if (Test-Path $createScriptPath) {
        # Read the script
        $scriptContent = Get-Content $createScriptPath -Raw
        # Replace the site URL
        $scriptContent = $scriptContent -replace '\$SiteUrl = "https://netorgft1612603.sharepoint.com/sites/YOUR-SITE-NAME-HERE"', "`$SiteUrl = `"$SiteUrl`""
        # Save it back
        Set-Content $createScriptPath -Value $scriptContent
        
        # Run the script
        & $createScriptPath
    } else {
        Write-Host "❌ create-sharepoint-list.ps1 not found" -ForegroundColor Red
        exit
    }
    
    Write-Host ""
    $continue = Read-Host "Did the list creation succeed? (yes/no)"
    if ($continue -ne "yes") {
        Write-Host "❌ Please fix the issues and run this script again." -ForegroundColor Red
        exit
    }
} elseif ($createMethod -eq "2") {
    Write-Host ""
    Write-Host "Opening SharePoint site in your browser..." -ForegroundColor Yellow
    Start-Process $SiteUrl
    Write-Host ""
    Write-Host "Manual steps:" -ForegroundColor Cyan
    Write-Host "1. Click '+ New' → 'List'" -ForegroundColor White
    Write-Host "2. Name it 'Multi-Cloud Resources'" -ForegroundColor White
    Write-Host "3. Refer to SETUP_STEPS.md for detailed column creation" -ForegroundColor White
    Write-Host ""
    $continue = Read-Host "Press ENTER when you've created the list with all 15 columns"
} else {
    Write-Host "❌ Invalid option. Exiting." -ForegroundColor Red
    exit
}

Write-Host ""
Write-Host "✅ SharePoint list is ready" -ForegroundColor Green
Write-Host ""

# Step 4: Register SharePoint App
Write-Host "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━" -ForegroundColor Cyan
Write-Host "STEP 4: Register SharePoint App" -ForegroundColor Yellow
Write-Host "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━" -ForegroundColor Cyan
Write-Host ""
Write-Host "Opening app registration page..." -ForegroundColor Yellow
Write-Host ""

$appRegUrl = "$TenantUrl/_layouts/15/appregnew.aspx"
Start-Process $appRegUrl

Write-Host "Follow these steps in the browser:" -ForegroundColor Cyan
Write-Host "1. Click 'Generate' next to Client Id" -ForegroundColor White
Write-Host "2. Click 'Generate' next to Client Secret" -ForegroundColor White
Write-Host "3. Fill in:" -ForegroundColor White
Write-Host "   Title: Multi-Cloud Resource Provisioner" -ForegroundColor Gray
Write-Host "   App Domain: victoriousbeach-6b7a8fbc.eastus.azurecontainerapps.io" -ForegroundColor Gray
Write-Host "   Redirect URI: https://victoriousbeach-6b7a8fbc.eastus.azurecontainerapps.io" -ForegroundColor Gray
Write-Host "4. Click 'Create'" -ForegroundColor White
Write-Host "5. SAVE the Client Id and Client Secret (you'll need them next)" -ForegroundColor Yellow
Write-Host ""

$continue = Read-Host "Press ENTER when you've saved the Client Id and Secret"

Write-Host ""
$ClientId = Read-Host "Paste the Client Id here"
$ClientSecret = Read-Host "Paste the Client Secret here" -AsSecureString
$ClientSecretPlain = [Runtime.InteropServices.Marshal]::PtrToStringAuto([Runtime.InteropServices.Marshal]::SecureStringToBSTR($ClientSecret))

if ([string]::IsNullOrWhiteSpace($ClientId) -or [string]::IsNullOrWhiteSpace($ClientSecretPlain)) {
    Write-Host "❌ Client Id and Secret are required. Exiting." -ForegroundColor Red
    exit
}

Write-Host ""
Write-Host "✅ App credentials saved" -ForegroundColor Green
Write-Host ""

# Step 5: Grant Permissions
Write-Host "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━" -ForegroundColor Cyan
Write-Host "STEP 5: Grant App Permissions" -ForegroundColor Yellow
Write-Host "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━" -ForegroundColor Cyan
Write-Host ""
Write-Host "Opening permission grant page..." -ForegroundColor Yellow
Write-Host ""

$appInvUrl = "$TenantUrl/_layouts/15/appinv.aspx"
Start-Process $appInvUrl

Write-Host "Follow these steps in the browser:" -ForegroundColor Cyan
Write-Host "1. Paste your Client Id: $ClientId" -ForegroundColor White
Write-Host "2. Click 'Lookup'" -ForegroundColor White
Write-Host "3. In 'Permission Request XML', paste:" -ForegroundColor White
Write-Host ""
Write-Host '<AppPermissionRequests AllowAppOnlyPolicy="true">' -ForegroundColor Gray
Write-Host '  <AppPermissionRequest Scope="http://sharepoint/content/sitecollection/web/list"' -ForegroundColor Gray
Write-Host '                        Right="Manage"/>' -ForegroundColor Gray
Write-Host '</AppPermissionRequests>' -ForegroundColor Gray
Write-Host ""
Write-Host "4. Click 'Create'" -ForegroundColor White
Write-Host "5. Click 'Trust It'" -ForegroundColor White
Write-Host ""

# Copy XML to clipboard
$permissionXml = '<AppPermissionRequests AllowAppOnlyPolicy="true"><AppPermissionRequest Scope="http://sharepoint/content/sitecollection/web/list" Right="Manage"/></AppPermissionRequests>'
Set-Clipboard -Value $permissionXml
Write-Host "✅ Permission XML copied to clipboard. Paste it in the browser!" -ForegroundColor Green
Write-Host ""

$continue = Read-Host "Press ENTER when you've granted permissions"

Write-Host ""
Write-Host "✅ Permissions granted" -ForegroundColor Green
Write-Host ""

# Step 6: Configure Webhook
Write-Host "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━" -ForegroundColor Cyan
Write-Host "STEP 6: Create Webhook Subscription" -ForegroundColor Yellow
Write-Host "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━" -ForegroundColor Cyan
Write-Host ""
Write-Host "Creating webhook..." -ForegroundColor Yellow

try {
    # Generate webhook secret
    $WebhookSecret = "whs-$(Get-Random)-$(Get-Date -Format 'yyyyMMddHHmmss')"
    
    # Connect to SharePoint
    Write-Host "Connecting to SharePoint..." -ForegroundColor Yellow
    Connect-PnPOnline -Url $SiteUrl -Interactive
    
    # Create webhook
    Write-Host "Adding webhook subscription..." -ForegroundColor Yellow
    $webhook = Add-PnPWebhookSubscription -List "Multi-Cloud Resources" `
        -NotificationUrl "$BackendUrl/api/webhook/sharepoint" `
        -ExpirationDate (Get-Date).AddMonths(6) `
        -ClientState $WebhookSecret
    
    Write-Host "✅ Webhook created successfully" -ForegroundColor Green
    Write-Host "   Webhook ID: $($webhook.Id)" -ForegroundColor Gray
    Write-Host "   Expires: $($webhook.ExpirationDateTime)" -ForegroundColor Gray
    Write-Host ""
    
} catch {
    Write-Host "❌ Failed to create webhook: $($_.Exception.Message)" -ForegroundColor Red
    Write-Host ""
    Write-Host "You can create it manually later using setup-sharepoint.ps1" -ForegroundColor Yellow
    $WebhookSecret = "whs-$(Get-Random)-$(Get-Date -Format 'yyyyMMddHHmmss')"
}

# Step 7: Update Backend
Write-Host "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━" -ForegroundColor Cyan
Write-Host "STEP 7: Update Backend Configuration" -ForegroundColor Yellow
Write-Host "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━" -ForegroundColor Cyan
Write-Host ""
Write-Host "Updating Azure Container App environment variables..." -ForegroundColor Yellow

try {
    # Check if Azure CLI is logged in
    $azAccount = az account show 2>$null | ConvertFrom-Json
    
    if (!$azAccount) {
        Write-Host "⚠️  Not logged in to Azure CLI" -ForegroundColor Yellow
        Write-Host "Logging in..." -ForegroundColor Yellow
        az login
    }
    
    # Update environment variables
    az containerapp update `
        --name azure-tracker-backend `
        --resource-group rg-azure-resources-tracker `
        --set-env-vars `
            "SHAREPOINT_ENABLED=true" `
            "SHAREPOINT_SITE_URL=$SiteUrl" `
            "SHAREPOINT_LIST_NAME=Multi-Cloud Resources" `
            "SHAREPOINT_CLIENT_ID=$ClientId" `
            "SHAREPOINT_CLIENT_SECRET=$ClientSecretPlain" `
            "WEBHOOK_SECRET=$WebhookSecret" `
        --output none
    
    Write-Host "✅ Backend configuration updated" -ForegroundColor Green
    Write-Host ""
    
} catch {
    Write-Host "❌ Failed to update backend: $($_.Exception.Message)" -ForegroundColor Red
    Write-Host ""
    Write-Host "Manual update command:" -ForegroundColor Yellow
    Write-Host "az containerapp update --name azure-tracker-backend --resource-group rg-azure-resources-tracker --set-env-vars SHAREPOINT_ENABLED=true SHAREPOINT_SITE_URL=$SiteUrl SHAREPOINT_LIST_NAME='Multi-Cloud Resources' SHAREPOINT_CLIENT_ID=$ClientId SHAREPOINT_CLIENT_SECRET='YOUR-SECRET' WEBHOOK_SECRET=$WebhookSecret" -ForegroundColor Gray
    Write-Host ""
}

# Step 8: Test
Write-Host "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━" -ForegroundColor Cyan
Write-Host "STEP 8: Test the Integration" -ForegroundColor Yellow
Write-Host "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━" -ForegroundColor Cyan
Write-Host ""

$listUrl = "$SiteUrl/Lists/Multi-Cloud%20Resources"
Write-Host "Opening your SharePoint list..." -ForegroundColor Yellow
Start-Process $listUrl

Write-Host ""
Write-Host "To test the integration:" -ForegroundColor Cyan
Write-Host "1. Click '+ New' in SharePoint" -ForegroundColor White
Write-Host "2. Fill in:" -ForegroundColor White
Write-Host "   UserName: Likhitha Singam" -ForegroundColor Gray
Write-Host "   CloudPlatform: Azure" -ForegroundColor Gray
Write-Host "   ResourceType: Resource Group" -ForegroundColor Gray
Write-Host "   ResourceGroupName: rg-test-webhook-001" -ForegroundColor Gray
Write-Host "   ProjectName: Webhook Test" -ForegroundColor Gray
Write-Host "   Status: Pending" -ForegroundColor Gray
Write-Host "3. Click 'Save'" -ForegroundColor White
Write-Host "4. Wait 2-3 minutes and refresh" -ForegroundColor White
Write-Host "5. Status should change to 'Completed'" -ForegroundColor White
Write-Host ""

# Summary
Write-Host "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━" -ForegroundColor Green
Write-Host "✅ SETUP COMPLETE!" -ForegroundColor Green
Write-Host "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━" -ForegroundColor Green
Write-Host ""
Write-Host "Configuration Summary:" -ForegroundColor Cyan
Write-Host "  Site URL: $SiteUrl" -ForegroundColor White
Write-Host "  List Name: Multi-Cloud Resources" -ForegroundColor White
Write-Host "  List URL: $listUrl" -ForegroundColor White
Write-Host "  Backend URL: $BackendUrl" -ForegroundColor White
Write-Host "  Webhook Secret: $WebhookSecret" -ForegroundColor White
Write-Host ""
Write-Host "Next Steps:" -ForegroundColor Yellow
Write-Host "• Share the list with your team members" -ForegroundColor White
Write-Host "• Give them Contribute permissions" -ForegroundColor White
Write-Host "• Share SHAREPOINT_USER_GUIDE.md with them" -ForegroundColor White
Write-Host "• Monitor backend logs: az containerapp logs show --name azure-tracker-backend --resource-group rg-azure-resources-tracker --follow" -ForegroundColor White
Write-Host ""
Write-Host "Documentation:" -ForegroundColor Yellow
Write-Host "• SETUP_STEPS.md - Detailed setup guide" -ForegroundColor White
Write-Host "• SHAREPOINT_USER_GUIDE.md - User reference" -ForegroundColor White
Write-Host "• SHAREPOINT_MULTICLOUD_SETUP.md - Complete technical guide" -ForegroundColor White
Write-Host ""
Write-Host "Happy provisioning! 🚀" -ForegroundColor Cyan
