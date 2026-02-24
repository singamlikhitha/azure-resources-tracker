# Manual SharePoint Setup Guide - Simple Steps

$TenantUrl = "https://netorgft1612603.sharepoint.com"
$SiteName = "devops"  # Change this if needed
$SiteUrl = "$TenantUrl/sites/$SiteName"
$ListName = "Multi-Cloud Resources"
$BackendUrl = "https://azure-tracker-backend.victoriousbeach-6b7a8fbc.eastus.azurecontainerapps.io"

Write-Host "============================================" -ForegroundColor Cyan
Write-Host "SharePoint Setup - Manual Guide" -ForegroundColor Cyan
Write-Host "============================================" -ForegroundColor Cyan
Write-Host ""

# STEP 1: Create SharePoint List
Write-Host "STEP 1: Create SharePoint List" -ForegroundColor Yellow
Write-Host "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━" -ForegroundColor Gray
Write-Host ""
Write-Host "Open this URL in your browser:" -ForegroundColor White
Write-Host $SiteUrl -ForegroundColor Cyan
Write-Host ""
Write-Host "Then:" -ForegroundColor White
Write-Host "1. Click [+ New] → [List]" -ForegroundColor White
Write-Host "2. Name it: Multi-Cloud Resources" -ForegroundColor White
Write-Host "3. Click [Create]" -ForegroundColor White
Write-Host "4. Add these 15 columns (click [+ Add column]):" -ForegroundColor White
Write-Host ""
Write-Host "   • UserName (Single line of text, Required)" -ForegroundColor Gray
Write-Host "   • CloudPlatform (Choice: Azure,GCP,AWS, Required)" -ForegroundColor Gray
Write-Host "   • ResourceType (Choice: Resource Group,Project,Account, Required)" -ForegroundColor Gray  
Write-Host "   • ResourceGroupName (Single line of text, Required)" -ForegroundColor Gray
Write-Host "   • ProjectName (Single line of text, Required)" -ForegroundColor Gray
Write-Host "   • SubscriptionId (Single line of text)" -ForegroundColor Gray
Write-Host "   • Location (Single line of text)" -ForegroundColor Gray
Write-Host "   • CreateGitHubRepo (Yes/No)" -ForegroundColor Gray
Write-Host "   • Tags (Multiple lines of text)" -ForegroundColor Gray
Write-Host "   • DateOfCreation (Date and time)" -ForegroundColor Gray
Write-Host "   • Status (Choice: Pending,In Progress,Completed,Failed, Required)" -ForegroundColor Gray
Write-Host "   • ResourceId (Single line of text)" -ForegroundColor Gray
Write-Host "   • AzureResourceGroupId (Single line of text)" -ForegroundColor Gray
Write-Host "   • GitHubRepoUrl (Hyperlink)" -ForegroundColor Gray
Write-Host "   • ErrorMessage (Multiple lines of text)" -ForegroundColor Gray
Write-Host ""
$continue = Read-Host "Press ENTER when you've created the list with all columns"

# STEP 2: Register SharePoint App
Write-Host ""
Write-Host "STEP 2: Register SharePoint App" -ForegroundColor Yellow
Write-Host "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━" -ForegroundColor Gray
Write-Host ""
Write-Host "Open this URL:" -ForegroundColor White
Write-Host "$TenantUrl/_layouts/15/appregnew.aspx" -ForegroundColor Cyan
Write-Host ""
Write-Host "Then:" -ForegroundColor White
Write-Host "1. Click [Generate] for Client Id" -ForegroundColor White
Write-Host "2. Click [Generate] for Client Secret" -ForegroundColor White
Write-Host "3. Fill in:" -ForegroundColor White
Write-Host "   Title: Multi-Cloud Resource Provisioner" -ForegroundColor Gray
Write-Host "   App Domain: victoriousbeach-6b7a8fbc.eastus.azurecontainerapps.io" -ForegroundColor Gray
Write-Host "   Redirect URI: https://victoriousbeach-6b7a8fbc.eastus.azurecontainerapps.io" -ForegroundColor Gray
Write-Host "4. Click [Create]" -ForegroundColor White
Write-Host "5. SAVE the Client Id and Client Secret!" -ForegroundColor Yellow
Write-Host ""
$ClientId = Read-Host "Paste your Client Id here"
$ClientSecret = Read-Host "Paste your Client Secret here"

# STEP 3: Grant Permissions
Write-Host ""
Write-Host "STEP 3: Grant Permissions" -ForegroundColor Yellow
Write-Host "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━" -ForegroundColor Gray
Write-Host ""
Write-Host "Open this URL:" -ForegroundColor White
Write-Host "$TenantUrl/_layouts/15/appinv.aspx" -ForegroundColor Cyan
Write-Host ""
Write-Host "Then:" -ForegroundColor White
Write-Host "1. Paste your Client Id: $ClientId" -ForegroundColor White
Write-Host "2. Click [Lookup]" -ForegroundColor White
Write-Host "3. In Permission Request XML, paste this:" -ForegroundColor White
Write-Host ""
$permXml = '<AppPermissionRequests AllowAppOnlyPolicy="true"><AppPermissionRequest Scope="http://sharepoint/content/sitecollection/web/list" Right="Manage"/></AppPermissionRequests>'
Write-Host $permXml -ForegroundColor Gray
Write-Host ""
Set-Clipboard -Value $permXml
Write-Host "✅ XML copied to clipboard! Just paste it." -ForegroundColor Green
Write-Host ""
Write-Host "4. Click [Create]" -ForegroundColor White
Write-Host "5. Click [Trust It]" -ForegroundColor White
Write-Host ""
$continue = Read-Host "Press ENTER when done"

# STEP 4: Create Webhook
Write-Host ""
Write-Host "STEP 4: Create Webhook" -ForegroundColor Yellow
Write-Host "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━" -ForegroundColor Gray
Write-Host ""

try {
    $WebhookSecret = "whs-$(Get-Random)-$(Get-Date -Format 'yyyyMMddHHmmss')"
    
    Write-Host "Connecting to SharePoint..." -ForegroundColor White
    Connect-PnPOnline -Url $SiteUrl -Interactive
    
    Write-Host "Creating webhook subscription..." -ForegroundColor White
    $webhook = Add-PnPWebhookSubscription -List $ListName `
        -NotificationUrl "$BackendUrl/api/webhook/sharepoint" `
        -ExpirationDate (Get-Date).AddMonths(6) `
        -ClientState $WebhookSecret
    
    Write-Host "✅ Webhook created!" -ForegroundColor Green
    Write-Host "   Webhook ID: $($webhook.Id)" -ForegroundColor Gray
    Write-Host ""
} catch {
    Write-Host "❌ Error: $($_.Exception.Message)" -ForegroundColor Red
    $WebhookSecret = "whs-$(Get-Random)-$(Get-Date -Format 'yyyyMMddHHmmss')"
    Write-Host ""
    Write-Host "Manual webhook command:" -ForegroundColor Yellow
    Write-Host "Connect-PnPOnline -Url '$SiteUrl' -Interactive" -ForegroundColor Gray
    Write-Host "Add-PnPWebhookSubscription -List '$ListName' -NotificationUrl '$BackendUrl/api/webhook/sharepoint' -ExpirationDate (Get-Date).AddMonths(6) -ClientState '$WebhookSecret'" -ForegroundColor Gray
    Write-Host ""
}

# STEP 5: Update Backend
Write-Host ""
Write-Host "STEP 5: Update Backend" -ForegroundColor Yellow
Write-Host "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━" -ForegroundColor Gray
Write-Host ""

try {
    Write-Host "Updating Azure Container App..." -ForegroundColor White
    
    az containerapp update `
        --name azure-tracker-backend `
        --resource-group rg-azure-resources-tracker `
        --set-env-vars `
            "SHAREPOINT_ENABLED=true" `
            "SHAREPOINT_SITE_URL=$SiteUrl" `
            "SHAREPOINT_LIST_NAME=$ListName" `
            "SHAREPOINT_CLIENT_ID=$ClientId" `
            "SHAREPOINT_CLIENT_SECRET=$ClientSecret" `
            "WEBHOOK_SECRET=$WebhookSecret" `
        --output none
    
    Write-Host "✅ Backend updated!" -ForegroundColor Green
} catch {
    Write-Host "❌ Error updating backend" -ForegroundColor Red
    Write-Host ""
    Write-Host "Manual command:" -ForegroundColor Yellow
    Write-Host "az containerapp update --name azure-tracker-backend --resource-group rg-azure-resources-tracker --set-env-vars SHAREPOINT_ENABLED=true SHAREPOINT_SITE_URL='$SiteUrl' SHAREPOINT_LIST_NAME='$ListName' SHAREPOINT_CLIENT_ID='$ClientId' SHAREPOINT_CLIENT_SECRET='$ClientSecret' WEBHOOK_SECRET='$WebhookSecret'" -ForegroundColor Gray
}

# SUCCESS
Write-Host ""
Write-Host "============================================" -ForegroundColor Green
Write-Host "✅ SETUP COMPLETE!" -ForegroundColor Green
Write-Host "============================================" -ForegroundColor Green
Write-Host ""
Write-Host "Test your integration:" -ForegroundColor Cyan
Write-Host "1. Go to: $SiteUrl/Lists/Multi-Cloud%20Resources" -ForegroundColor White
Write-Host "2. Click [+ New]" -ForegroundColor White
Write-Host "3. Fill in:" -ForegroundColor White
Write-Host "   - UserName: Likhitha Singam" -ForegroundColor Gray
Write-Host "   - CloudPlatform: Azure" -ForegroundColor Gray
Write-Host "   - ResourceType: Resource Group" -ForegroundColor Gray
Write-Host "   - ResourceGroupName: rg-test-001" -ForegroundColor Gray
Write-Host "   - ProjectName: Test" -ForegroundColor Gray
Write-Host "   - Status: Pending" -ForegroundColor Gray
Write-Host "4. Click [Save]" -ForegroundColor White
Write-Host "5. Wait 2-3 minutes, refresh page" -ForegroundColor White
Write-Host "6. Status should be 'Completed' ✅" -ForegroundColor White
Write-Host ""
Write-Host "Your list URL:" -ForegroundColor Yellow
Write-Host "$SiteUrl/Lists/Multi-Cloud%20Resources" -ForegroundColor Cyan
Write-Host ""
