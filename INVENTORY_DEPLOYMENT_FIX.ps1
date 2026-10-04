# ============================================================================
# SIR_GREEN — Torus Inventory Container Fix
# ============================================================================
# This script MUST be run on SQUIDSTATION (Docker host)
# It removes the broken inventory container and deploys the fixed FastAPI image
# ============================================================================

param(
    [switch]$DryRun = $false
)

$ErrorActionPreference = "Stop"

Write-Host "=== TORUS-INVENTORY FIX ===" -ForegroundColor Cyan

# Step 1: Stop broken container
Write-Host "`n[1/3] Stopping broken torus-inventory container..." -ForegroundColor Yellow
if (-not $DryRun) {
    try {
        docker stop torus-inventory 2>&1 | Out-Null
        Write-Host "  OK: Stopped" -ForegroundColor Green
    } catch {
        Write-Host "  INFO: Container not running" -ForegroundColor Gray
    }
} else {
    Write-Host "  [DRY RUN] Would stop torus-inventory" -ForegroundColor Gray
}

# Step 2: Remove broken container
Write-Host "`n[2/3] Removing broken container..." -ForegroundColor Yellow
if (-not $DryRun) {
    try {
        docker rm torus-inventory 2>&1 | Out-Null
        Write-Host "  OK: Removed" -ForegroundColor Green
    } catch {
        Write-Host "  INFO: Container didn't exist" -ForegroundColor Gray
    }
} else {
    Write-Host "  [DRY RUN] Would remove torus-inventory" -ForegroundColor Gray
}

# Step 3: Deploy new FastAPI image
Write-Host "`n[3/3] Deploying new FastAPI image..." -ForegroundColor Yellow
if (-not $DryRun) {
    docker run -d `
        --name torus-inventory `
        --restart unless-stopped `
        -p 3200:3200 `
        -v "D:/Work/Torus Coffee Company LLC:/vault:ro" `
        torus-inventory:local
    Write-Host "  OK: Container deployed" -ForegroundColor Green
} else {
    Write-Host "  [DRY RUN] Would deploy torus-inventory:local" -ForegroundColor Gray
}

# Step 4: Wait for startup and verify health
Write-Host "`n[4/4] Verifying health endpoint..." -ForegroundColor Yellow
if (-not $DryRun) {
    Start-Sleep -Seconds 3
    try {
        $health = curl.exe -s "http://localhost:3200/health" | ConvertFrom-Json
        if ($health.status -eq "ok") {
            Write-Host "  OK: Health endpoint responding" -ForegroundColor Green
            Write-Host "  Status: $($health.service)" -ForegroundColor Green
        } else {
            Write-Host "  WARNING: Unexpected response: $($health | ConvertTo-Json)" -ForegroundColor Yellow
        }
    } catch {
        Write-Host "  WARNING: Could not verify health (container may still be starting)" -ForegroundColor Yellow
        Write-Host "  Retry in 10 seconds: curl http://localhost:3200/health" -ForegroundColor Yellow
    }
} else {
    Write-Host "  [DRY RUN] Would verify health endpoint" -ForegroundColor Gray
}

Write-Host "`n=== FIX COMPLETE ===" -ForegroundColor Cyan
Write-Host "Inventory API running on port 3200" -ForegroundColor White
Write-Host "Health: http://localhost:3200/health" -ForegroundColor White
Write-Host "Inventory: http://localhost:3200/inventory" -ForegroundColor White
