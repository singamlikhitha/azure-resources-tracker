# Quick Setup Script for SharePoint Multi-Cloud Tracker

# Prerequisites:
# 1. Install PnP PowerShell: Install-Module -Name PnP.PowerShell -Scope CurrentUser
# 2. Have SharePoint site URL ready
# 3. Have list name ready (default: "Multi-Cloud Resources")
# 4. Have backend app credentials (Client ID, Client Secret from appregnew.aspx)

# ============================================
# CONFIGURATION - UPDATE THESE VALUES
# ============================================

# TODO: Update with your actual SharePoint site name (e.g., /sites/IT-Resources)
$SharePointSiteUrl = "https://netorgft1612603.sharepoint.com/sites/YOUR-SITE-NAME-HERE"
$ListName = "Multi-Cloud Resources"
$BackendWebhookUrl = "https://azure-tracker-backend.victoriousbeach-6b7a8fbc.eastus.azurecontainerapps.io/api/webhook/sharepoint"
$WebhookClientState = "whs-$(Get-Random)-$(Get-Date -Format 'yyyyMMddHHmmss')"  # Must match WEBHOOK_SECRET in backend
$AzureResourceGroup = "rg-azure-resources-tracker"
$BackendAppName = "azure-tracker-backend"

# TODO: Get these from https://netorgft1612603.sharepoint.com/_layouts/15/appregnew.aspx
$SharePointClientId = "YOUR-CLIENT-ID-HERE"
$SharePointClientSecret = "YOUR-CLIENT-SECRET-HERE"

# ============================================
# SCRIPT START
# ============================================

Write-Host "======================================" -ForegroundColor Cyan
Write-Host "SharePoint Multi-Cloud Tracker Setup" -ForegroundColor Cyan
Write-Host "======================================" -ForegroundColor Cyan
Write-Host ""

# Step 1: Connect to SharePoint
Write-Host "Step 1: Connecting to SharePoint..." -ForegroundColor Yellow
try {
    Connect-PnPOnline -Url $SharePointSiteUrl -Interactive
    Write-Host "✓ Connected successfully" -ForegroundColor Green
} catch {
    Write-Host "✗ Failed to connect: $_" -ForegroundColor Red
    exit
}

# Step 2: Check if list exists
Write-Host ""
Write-Host "Step 2: Checking if list exists..." -ForegroundColor Yellow
$list = Get-PnPList -Identity $ListName -ErrorAction SilentlyContinue

if ($null -eq $list) {
    Write-Host "List '$ListName' not found. Please create it manually first." -ForegroundColor Red
    Write-Host "Refer to SHAREPOINT_MULTICLOUD_SETUP.md for instructions." -ForegroundColor Yellow
    exit
} else {
    Write-Host "✓ List '$ListName' found" -ForegroundColor Green
}

# Step 3: Verify required columns
Write-Host ""
Write-Host "Step 3: Verifying list columns..." -ForegroundColor Yellow

$requiredColumns = @(
    "UserName",
    "CloudPlatform",
    "ResourceType",
    "ResourceGroupName",
    "ProjectName",
    "Status",
    "DateOfCreation",
    "ResourceId",
    "GitHubRepoUrl"
)

$fields = Get-PnPField -List $ListName
$missingColumns = @()

foreach ($column in $requiredColumns) {
    $field = $fields | Where-Object { $_.InternalName -eq $column }
    if ($null -eq $field) {
        $missingColumns += $column
        Write-Host "  ✗ Missing: $column" -ForegroundColor Red
    } else {
        Write-Host "  ✓ Found: $column" -ForegroundColor Green
    }
}

if ($missingColumns.Count -gt 0) {
    Write-Host ""
    Write-Host "Missing columns detected. Please add them manually:" -ForegroundColor Red
    $missingColumns | ForEach-Object { Write-Host "  - $_" -ForegroundColor Yellow }
    Write-Host ""
    Write-Host "Refer to Part 1, Step 2 in SHAREPOINT_MULTICLOUD_SETUP.md" -ForegroundColor Yellow
    exit
}

# Step 4: Configure webhook
Write-Host ""
Write-Host "Step 4: Setting up webhook..." -ForegroundColor Yellow

# Check existing webhooks
$existingWebhooks = Get-PnPWebhookSubscriptions -List $ListName

if ($existingWebhooks.Count -gt 0) {
    Write-Host "Existing webhooks found:" -ForegroundColor Yellow
    $existingWebhooks | ForEach-Object {
        Write-Host "  - ID: $($_.Id)" -ForegroundColor Gray
        Write-Host "    URL: $($_.NotificationUrl)" -ForegroundColor Gray
        Write-Host "    Expires: $($_.ExpirationDateTime)" -ForegroundColor Gray
    }
    
    $response = Read-Host "Remove existing webhooks and create new one? (y/n)"
    if ($response -eq 'y') {
        foreach ($webhook in $existingWebhooks) {
            Remove-PnPWebhookSubscription -List $ListName -Identity $webhook.Id
            Write-Host "  ✓ Removed webhook $($webhook.Id)" -ForegroundColor Green
        }
    }
}

# Add new webhook
try {
    $expirationDate = (Get-Date).AddMonths(6)
    $webhook = Add-PnPWebhookSubscription `
        -List $ListName `
        -NotificationUrl $BackendWebhookUrl `
        -ExpirationDate $expirationDate `
        -ClientState $WebhookClientState
    
    Write-Host "✓ Webhook created successfully" -ForegroundColor Green
    Write-Host "  ID: $($webhook.Id)" -ForegroundColor Gray
    Write-Host "  Expires: $expirationDate" -ForegroundColor Gray
} catch {
    Write-Host "✗ Failed to create webhook: $_" -ForegroundColor Red
    Write-Host "Make sure the backend URL is accessible via HTTPS" -ForegroundColor Yellow
}

# Step 5: Update Azure Container App environment variables
Write-Host ""
Write-Host "Step 5: Updating backend configuration..." -ForegroundColor Yellow

if ($SharePointClientId -eq "YOUR-CLIENT-ID-HERE" -or $SharePointClientSecret -eq "YOUR-CLIENT-SECRET-HERE") {
    Write-Host "⚠ SharePoint credentials not configured in this script" -ForegroundColor Yellow
    Write-Host "Please run the following command manually with your credentials:" -ForegroundColor Yellow
    Write-Host ""
    Write-Host "az containerapp update ``" -ForegroundColor Cyan
    Write-Host "  --name $BackendAppName ``" -ForegroundColor Cyan
    Write-Host "  --resource-group $AzureResourceGroup ``" -ForegroundColor Cyan
    Write-Host "  --set-env-vars ``" -ForegroundColor Cyan
    Write-Host "    `"SHAREPOINT_ENABLED=true`" ``" -ForegroundColor Cyan
    Write-Host "    `"SHAREPOINT_SITE_URL=$SharePointSiteUrl`" ``" -ForegroundColor Cyan
    Write-Host "    `"SHAREPOINT_LIST_NAME=$ListName`" ``" -ForegroundColor Cyan
    Write-Host "    `"SHAREPOINT_CLIENT_ID=your-client-id`" ``" -ForegroundColor Cyan
    Write-Host "    `"SHAREPOINT_CLIENT_SECRET=your-client-secret`"" -ForegroundColor Cyan
} else {
    try {
        az containerapp update `
            --name $BackendAppName `
            --resource-group $AzureResourceGroup `
            --set-env-vars `
                "SHAREPOINT_ENABLED=true" `
                "SHAREPOINT_SITE_URL=$SharePointSiteUrl" `
                "SHAREPOINT_LIST_NAME=$ListName" `
                "SHAREPOINT_CLIENT_ID=$SharePointClientId" `
                "SHAREPOINT_CLIENT_SECRET=$SharePointClientSecret"
        
        Write-Host "✓ Backend configuration updated" -ForegroundColor Green
    } catch {
        Write-Host "✗ Failed to update backend: $_" -ForegroundColor Red
    }
}

# Step 6: Summary
Write-Host ""
Write-Host "======================================" -ForegroundColor Cyan
Write-Host "Setup Complete!" -ForegroundColor Cyan
Write-Host "======================================" -ForegroundColor Cyan
Write-Host ""
Write-Host "Next Steps:" -ForegroundColor Yellow
Write-Host "1. Verify backend environment variables are set correctly" -ForegroundColor White
Write-Host "2. Test by creating a new item in the SharePoint list" -ForegroundColor White
Write-Host "3. Watch the Status column change from Pending → In Progress → Completed" -ForegroundColor White
Write-Host "4. Check backend logs if issues occur:" -ForegroundColor White
Write-Host "   az containerapp logs show --name $BackendAppName --resource-group $AzureResourceGroup --follow" -ForegroundColor Gray
Write-Host ""
Write-Host "Webhook will expire on: $expirationDate" -ForegroundColor Yellow
Write-Host "Remember to renew it before expiration!" -ForegroundColor Yellow
Write-Host ""
Write-Host "For detailed instructions, see: SHAREPOINT_MULTICLOUD_SETUP.md" -ForegroundColor Cyan
