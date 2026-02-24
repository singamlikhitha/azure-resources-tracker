# Create SharePoint List - Multi-Cloud Resources
# This script automatically creates the SharePoint list with all required columns

# Prerequisites:
# Install-Module -Name PnP.PowerShell -Scope CurrentUser

# ============================================
# CONFIGURATION
# ============================================

$SiteUrl = "https://netorgft1612603.sharepoint.com/sites/devops"
$ListName = "Multi-Cloud Resources"
$ListDescription = "Multi-cloud resource provisioning tracker for Azure, GCP, and AWS"

# ============================================
# SCRIPT START
# ============================================

Write-Host "==========================================" -ForegroundColor Cyan
Write-Host "Creating SharePoint List: $ListName" -ForegroundColor Cyan
Write-Host "==========================================" -ForegroundColor Cyan
Write-Host ""

try {
    # Connect to SharePoint
    Write-Host "[1/17] Connecting to SharePoint..." -ForegroundColor Yellow
    Connect-PnPOnline -Url $SiteUrl -Interactive
    Write-Host "✅ Connected successfully" -ForegroundColor Green
    Write-Host ""

    # Check if list exists
    Write-Host "[2/17] Checking if list exists..." -ForegroundColor Yellow
    $existingList = Get-PnPList -Identity $ListName -ErrorAction SilentlyContinue
    
    if ($existingList) {
        Write-Host "⚠️  List '$ListName' already exists!" -ForegroundColor Yellow
        $overwrite = Read-Host "Do you want to delete and recreate it? (yes/no)"
        
        if ($overwrite -eq "yes") {
            Write-Host "Deleting existing list..." -ForegroundColor Yellow
            Remove-PnPList -Identity $ListName -Force
            Write-Host "✅ Deleted existing list" -ForegroundColor Green
        } else {
            Write-Host "❌ Cancelled. Existing list kept." -ForegroundColor Red
            exit
        }
    }
    
    # Create the list
    Write-Host "[3/17] Creating list '$ListName'..." -ForegroundColor Yellow
    $list = New-PnPList -Title $ListName -Template GenericList -OnQuickLaunch
    Write-Host "✅ List created" -ForegroundColor Green
    Write-Host ""

    # Add Column 1: UserName
    Write-Host "[4/17] Adding column: UserName (Single line of text)..." -ForegroundColor Yellow
    Add-PnPField -List $ListName -DisplayName "UserName" -InternalName "UserName" -Type Text -Required
    Write-Host "✅ UserName added" -ForegroundColor Green

    # Add Column 2: CloudPlatform
    Write-Host "[5/17] Adding column: CloudPlatform (Choice)..." -ForegroundColor Yellow
    Add-PnPField -List $ListName -DisplayName "CloudPlatform" -InternalName "CloudPlatform" -Type Choice -Required `
        -Choices @("Azure", "GCP", "AWS") -DefaultValue "Azure"
    Write-Host "✅ CloudPlatform added" -ForegroundColor Green

    # Add Column 3: ResourceType
    Write-Host "[6/17] Adding column: ResourceType (Choice)..." -ForegroundColor Yellow
    Add-PnPField -List $ListName -DisplayName "ResourceType" -InternalName "ResourceType" -Type Choice -Required `
        -Choices @("Resource Group", "Project", "Account") -DefaultValue "Resource Group"
    Write-Host "✅ ResourceType added" -ForegroundColor Green

    # Add Column 4: ResourceGroupName
    Write-Host "[7/17] Adding column: ResourceGroupName (Single line of text)..." -ForegroundColor Yellow
    Add-PnPField -List $ListName -DisplayName "ResourceGroupName" -InternalName "ResourceGroupName" -Type Text -Required
    Write-Host "✅ ResourceGroupName added" -ForegroundColor Green

    # Add Column 5: ProjectName
    Write-Host "[8/17] Adding column: ProjectName (Single line of text)..." -ForegroundColor Yellow
    Add-PnPField -List $ListName -DisplayName "ProjectName" -InternalName "ProjectName" -Type Text -Required
    Write-Host "✅ ProjectName added" -ForegroundColor Green

    # Add Column 6: SubscriptionId
    Write-Host "[9/17] Adding column: SubscriptionId (Single line of text)..." -ForegroundColor Yellow
    Add-PnPField -List $ListName -DisplayName "SubscriptionId" -InternalName "SubscriptionId" -Type Text
    Write-Host "✅ SubscriptionId added" -ForegroundColor Green

    # Add Column 7: Location
    Write-Host "[10/17] Adding column: Location (Single line of text)..." -ForegroundColor Yellow
    Add-PnPField -List $ListName -DisplayName "Location" -InternalName "Location" -Type Text
    Write-Host "✅ Location added" -ForegroundColor Green

    # Add Column 8: CreateGitHubRepo
    Write-Host "[11/17] Adding column: CreateGitHubRepo (Yes/No)..." -ForegroundColor Yellow
    Add-PnPField -List $ListName -DisplayName "CreateGitHubRepo" -InternalName "CreateGitHubRepo" -Type Boolean
    Write-Host "✅ CreateGitHubRepo added" -ForegroundColor Green

    # Add Column 9: Tags
    Write-Host "[12/17] Adding column: Tags (Multiple lines of text)..." -ForegroundColor Yellow
    Add-PnPField -List $ListName -DisplayName "Tags" -InternalName "Tags" -Type Note
    Write-Host "✅ Tags added" -ForegroundColor Green

    # Add Column 10: DateOfCreation
    Write-Host "[13/17] Adding column: DateOfCreation (Date and time)..." -ForegroundColor Yellow
    Add-PnPField -List $ListName -DisplayName "DateOfCreation" -InternalName "DateOfCreation" -Type DateTime `
        -DisplayFormat "DateAndTime"
    Write-Host "✅ DateOfCreation added" -ForegroundColor Green

    # Add Column 11: Status
    Write-Host "[14/17] Adding column: Status (Choice)..." -ForegroundColor Yellow
    Add-PnPField -List $ListName -DisplayName "Status" -InternalName "Status" -Type Choice -Required `
        -Choices @("Pending", "In Progress", "Completed", "Failed") -DefaultValue "Pending"
    Write-Host "✅ Status added" -ForegroundColor Green

    # Add Column 12: ResourceId
    Write-Host "[15/17] Adding column: ResourceId (Single line of text)..." -ForegroundColor Yellow
    Add-PnPField -List $ListName -DisplayName "ResourceId" -InternalName "ResourceId" -Type Text
    Write-Host "✅ ResourceId added" -ForegroundColor Green

    # Add Column 13: AzureResourceGroupId
    Write-Host "[16/17] Adding column: AzureResourceGroupId (Single line of text)..." -ForegroundColor Yellow
    Add-PnPField -List $ListName -DisplayName "AzureResourceGroupId" -InternalName "AzureResourceGroupId" -Type Text
    Write-Host "✅ AzureResourceGroupId added" -ForegroundColor Green

    # Add Column 14: GitHubRepoUrl
    Write-Host "[17/17] Adding column: GitHubRepoUrl (Hyperlink)..." -ForegroundColor Yellow
    Add-PnPField -List $ListName -DisplayName "GitHubRepoUrl" -InternalName "GitHubRepoUrl" -Type URL
    Write-Host "✅ GitHubRepoUrl added" -ForegroundColor Green

    # Add Column 15: ErrorMessage
    Write-Host "[17/17] Adding column: ErrorMessage (Multiple lines of text)..." -ForegroundColor Yellow
    Add-PnPField -List $ListName -DisplayName "ErrorMessage" -InternalName "ErrorMessage" -Type Note
    Write-Host "✅ ErrorMessage added" -ForegroundColor Green
    Write-Host ""

    # Create default views
    Write-Host "Creating custom views..." -ForegroundColor Yellow
    
    # View 1: All Items (default - already exists)
    Write-Host "  ✅ All Items (default view)" -ForegroundColor Green
    
    # View 2: Pending Requests
    Write-Host "  Creating view: Pending Requests..." -ForegroundColor Yellow
    $pendingView = Add-PnPView -List $ListName -Title "Pending Requests" -Fields "ID","UserName","CloudPlatform","ResourceType","ResourceGroupName","ProjectName","DateOfCreation","Status" -Query '<Where><Eq><FieldRef Name="Status"/><Value Type="Choice">Pending</Value></Eq></Where><OrderBy><FieldRef Name="DateOfCreation" Ascending="FALSE"/></OrderBy>'
    Write-Host "  ✅ Pending Requests view created" -ForegroundColor Green
    
    # View 3: Completed
    Write-Host "  Creating view: Completed..." -ForegroundColor Yellow
    $completedView = Add-PnPView -List $ListName -Title "Completed" -Fields "ID","UserName","CloudPlatform","ResourceType","ResourceGroupName","ResourceId","GitHubRepoUrl","DateOfCreation","Status" -Query '<Where><Eq><FieldRef Name="Status"/><Value Type="Choice">Completed</Value></Eq></Where><OrderBy><FieldRef Name="DateOfCreation" Ascending="FALSE"/></OrderBy>'
    Write-Host "  ✅ Completed view created" -ForegroundColor Green
    
    # View 4: Failed
    Write-Host "  Creating view: Failed..." -ForegroundColor Yellow
    $failedView = Add-PnPView -List $ListName -Title "Failed" -Fields "ID","UserName","CloudPlatform","ResourceType","ResourceGroupName","ErrorMessage","DateOfCreation","Status" -Query '<Where><Eq><FieldRef Name="Status"/><Value Type="Choice">Failed</Value></Eq></Where><OrderBy><FieldRef Name="DateOfCreation" Ascending="FALSE"/></OrderBy>'
    Write-Host "  ✅ Failed view created" -ForegroundColor Green
    
    # View 5: My Requests
    Write-Host "  Creating view: My Requests..." -ForegroundColor Yellow
    $myView = Add-PnPView -List $ListName -Title "My Requests" -Fields "ID","CloudPlatform","ResourceType","ResourceGroupName","ProjectName","Status","ResourceId","GitHubRepoUrl","DateOfCreation" -Query '<Where><Eq><FieldRef Name="Author"/><Value Type="Integer"><UserID/></Value></Eq></Where><OrderBy><FieldRef Name="DateOfCreation" Ascending="FALSE"/></OrderBy>' -PersonalView
    Write-Host "  ✅ My Requests view created" -ForegroundColor Green
    Write-Host ""

    # Get the list URL
    $listUrl = "$SiteUrl/Lists/$($ListName -replace ' ', '%20')"

    # Success summary
    Write-Host "==========================================" -ForegroundColor Green
    Write-Host "✅ SUCCESS! List created with 15 columns" -ForegroundColor Green
    Write-Host "==========================================" -ForegroundColor Green
    Write-Host ""
    Write-Host "List URL:" -ForegroundColor Cyan
    Write-Host $listUrl -ForegroundColor White
    Write-Host ""
    Write-Host "Columns created:" -ForegroundColor Cyan
    Write-Host "  1. UserName (Text, Required)" -ForegroundColor White
    Write-Host "  2. CloudPlatform (Choice: Azure/GCP/AWS, Required)" -ForegroundColor White
    Write-Host "  3. ResourceType (Choice: Resource Group/Project/Account, Required)" -ForegroundColor White
    Write-Host "  4. ResourceGroupName (Text, Required)" -ForegroundColor White
    Write-Host "  5. ProjectName (Text, Required)" -ForegroundColor White
    Write-Host "  6. SubscriptionId (Text)" -ForegroundColor White
    Write-Host "  7. Location (Text)" -ForegroundColor White
    Write-Host "  8. CreateGitHubRepo (Yes/No)" -ForegroundColor White
    Write-Host "  9. Tags (Multiple lines)" -ForegroundColor White
    Write-Host "  10. DateOfCreation (Date and Time)" -ForegroundColor White
    Write-Host "  11. Status (Choice: Pending/In Progress/Completed/Failed, Required)" -ForegroundColor White
    Write-Host "  12. ResourceId (Text)" -ForegroundColor White
    Write-Host "  13. AzureResourceGroupId (Text)" -ForegroundColor White
    Write-Host "  14. GitHubRepoUrl (Hyperlink)" -ForegroundColor White
    Write-Host "  15. ErrorMessage (Multiple lines)" -ForegroundColor White
    Write-Host ""
    Write-Host "Views created:" -ForegroundColor Cyan
    Write-Host "  • All Items (default)" -ForegroundColor White
    Write-Host "  • Pending Requests" -ForegroundColor White
    Write-Host "  • Completed" -ForegroundColor White
    Write-Host "  • Failed" -ForegroundColor White
    Write-Host "  • My Requests (personal view)" -ForegroundColor White
    Write-Host ""
    Write-Host "Next Steps:" -ForegroundColor Yellow
    Write-Host "1. Register SharePoint app: https://netorgft1612603.sharepoint.com/_layouts/15/appregnew.aspx" -ForegroundColor White
    Write-Host "2. Grant permissions: https://netorgft1612603.sharepoint.com/_layouts/15/appinv.aspx" -ForegroundColor White
    Write-Host "3. Update setup-sharepoint.ps1 with Client ID and Secret" -ForegroundColor White
    Write-Host "4. Run: .\setup-sharepoint.ps1" -ForegroundColor White
    Write-Host ""

} catch {
    Write-Host ""
    Write-Host "==========================================" -ForegroundColor Red
    Write-Host "❌ ERROR" -ForegroundColor Red
    Write-Host "==========================================" -ForegroundColor Red
    Write-Host $_.Exception.Message -ForegroundColor Red
    Write-Host ""
    Write-Host "Troubleshooting:" -ForegroundColor Yellow
    Write-Host "• Make sure you have site owner or admin permissions" -ForegroundColor White
    Write-Host "• Verify the site URL is correct" -ForegroundColor White
    Write-Host "• Check if PnP.PowerShell module is installed: Get-Module -ListAvailable PnP.PowerShell" -ForegroundColor White
    Write-Host ""
}

