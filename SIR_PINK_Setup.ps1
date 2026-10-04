# SIR_PINK — Torus Coffee Company Docker/Hermes Agent Setup
# Run this on PINKCADY after Docker Desktop is installed
# This configures the local Hermes agent for SQUIDSTATION Docker access

param(
    [switch]$DryRun = $false
)

$ErrorActionPreference = "Stop"

Write-Host "=== SIR_PINK TORUS DOCKER SETUP ===" -ForegroundColor Cyan

# Step 1: Verify Docker is running
Write-Host "`n[1/4] Verifying Docker..." -ForegroundColor Yellow
try {
    $dockerVersion = docker --version
    Write-Host "  OK: $dockerVersion" -ForegroundColor Green
} catch {
    Write-Host "  FAIL: Docker not found. Install Docker Desktop first." -ForegroundColor Red
    exit 1
}

# Step 2: Create Torus Docker context
Write-Host "`n[2/4] Creating Torus Docker context..." -ForegroundColor Yellow
$contextName = "torus-squidstation"
$dockerHost = "tcp://192.168.0.39:2375"

# Check if context already exists
$existingContext = docker context ls --format "{{.Name}}" 2>$null | Where-Object { $_ -eq $contextName }
if ($existingContext) {
    Write-Host "  OK: Context '$contextName' already exists" -ForegroundColor Green
} else {
    if (-not $DryRun) {
        docker context create $contextName --docker "$dockerHost" 2>&1 | Out-Null
        Write-Host "  OK: Created context '$contextName'" -ForegroundColor Green
    } else {
        Write-Host "  [DRY RUN] Would create context '$contextName'" -ForegroundColor Gray
    }
}

# Step 3: Set default context
Write-Host "`n[3/4] Setting default context..." -ForegroundColor Yellow
if (-not $DryRun) {
    docker context use $contextName 2>&1 | Out-Null
    Write-Host "  OK: Default context set to '$contextName'" -ForegroundColor Green
} else {
    Write-Host "  [DRY RUN] Would set default context to '$contextName'" -ForegroundColor Gray
}

# Step 4: Verify connection
Write-Host "`n[4/4] Verifying SQUIDSTATION connection..." -ForegroundColor Yellow
if (-not $DryRun) {
    $info = docker info --format "{{.ServerVersion}} {{.OperatingSystem}}" 2>&1
    Write-Host "  OK: Connected: $info" -ForegroundColor Green
    
    $containers = docker ps --format "{{.Names}}" 2>&1
    $containerCount = ($containers | Measure-Object).Count
    Write-Host "  OK: Containers visible: $containerCount" -ForegroundColor Green
} else {
    Write-Host "  [DRY RUN] Would verify connection" -ForegroundColor Gray
}

Write-Host "`n=== SIR_PINK SETUP COMPLETE ===" -ForegroundColor Cyan
Write-Host "Docker context: $contextName" -ForegroundColor White
Write-Host "Docker host: $dockerHost" -ForegroundColor White
Write-Host "`nTo use: docker --context $contextName <command>" -ForegroundColor Gray
Write-Host "To switch default: docker context use $contextName" -ForegroundColor Gray
