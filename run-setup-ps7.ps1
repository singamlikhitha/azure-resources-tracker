# Launch quick-start.ps1 in PowerShell 7
$scriptPath = Join-Path $PSScriptRoot "quick-start.ps1"

if ($PSVersionTable.PSVersion.Major -lt 7) {
    Write-Host "Launching in PowerShell 7..." -ForegroundColor Yellow
    pwsh -NoExit -File $scriptPath
} else {
    & $scriptPath
}
