# ============================================================================
# TORUS DOCKER FLEET — MASTER DEPLOYMENT SCRIPT
# ============================================================================
# Run this from SQUIDSTATION to deploy the complete Torus Coffee fleet
# Prerequisites:
#   - Docker running on SQUIDSTATION
#   - torus-network bridge created
#   - All images built on PINKCADY and accessible
# ============================================================================

param(
    [switch]$DryRun = $false,
    [switch]$SkipHealthChecks = $false
)

$ErrorActionPreference = "Stop"
$ScriptDir = Split-Path -Parent $MyInvocation.MyCommand.Path

Write-Host \"=== TORUS COFFEE DOCKER FLEET DEPLOYMENT ===\" -ForegroundColor Cyan
Write-Host \"Date: $(Get-Date -Format 'yyyy-MM-dd HH:mm:ss')\" -ForegroundColor White
Write-Host \"Host: $(hostname)\" -ForegroundColor White
Write-Host \"\" -ForegroundColor White

# Step 1: Verify Docker context
Write-Host \"[1/6] Verifying Docker context...\" -ForegroundColor Yellow
if (-not $DryRun) {
    try {
        $dockerInfo = docker info --format \"{{.ServerVersion}}\"
        Write-Host \"  OK: Docker running (version $dockerInfo)\" -ForegroundColor Green
    } catch {
        Write-Host \"  FAIL: Docker not accessible\" -ForegroundColor Red
        exit 1
    }
} else {
    Write-Host \"  [DRY RUN] Would verify Docker\" -ForegroundColor Gray
}

# Step 2: Create torus-network if missing
Write-Host \"[2/6] Creating torus-network...\" -ForegroundColor Yellow
if (-not $DryRun) {
    $networks = docker network ls --format \"{{.Name}}\"
    if ($networks -notcontains \"torus-network\") {
        docker network create torus-network
        Write-Host \"  OK: torus-network created\" -ForegroundColor Green
    } else {
        Write-Host \"  OK: torus-network already exists\" -ForegroundColor Green
    }
} else {
    Write-Host \"  [DRY RUN] Would create torus-network\" -ForegroundColor Gray
}

# Step 3: Stop existing fleet
Write-Host \"[3/6] Stopping existing fleet...\" -ForegroundColor Yellow
if (-not $DryRun) {
    docker compose -f \"$ScriptDir/docker-compose.torus.fleet.yml\" down 2>&1 | Out-Null
    Write-Host \"  OK: Fleet stopped\" -ForegroundColor Green
} else {
    Write-Host \"  [DRY RUN] Would stop fleet\" -ForegroundColor Gray
}

# Step 4: Deploy fleet
Write-Host \"[4/6] Deploying fleet...\" -ForegroundColor Yellow
if (-not $DryRun) {
    docker compose -f \"$ScriptDir/docker-compose.torus.fleet.yml\" up -d
    Write-Host \"  OK: Fleet deployed\" -ForegroundColor Green
} else {
    Write-Host \"  [DRY RUN] Would deploy fleet\" -ForegroundColor Gray
}

# Step 5: Wait and check health
Write-Host \"[5/6] Waiting for services to start (30 seconds)...\" -ForegroundColor Yellow
Start-Sleep -Seconds 5

Write-Host \"[6/6] Checking health endpoints...\" -ForegroundColor Yellow
if (-not $SkipHealthChecks) {
    $services = @{
        \"torus-redis\" = \"127.0.0.1:6379\"
        \"torus-inventory\" = \"127.0.0.1:3200\"
        \"torus-pos\" = \"127.0.0.1:3100\"
        \"torus-dashboard\" = \"0.0.0.0:3000\" # internal only
        \"torus-website\" = \"0.0.0.0:3005\" # check via container
        \"torus-alert-router\" = \"127.0.0.1:4000\"
    }
    
    foreach ($service in $services.GetEnumerator()) {
        try {
            if ($service.Value -contains \"0.0.0.0\") {
                # Internal service, check via docker
                $health = docker exec $service.Key curl -s http://localhost:3000/health 2>$null | ConvertFrom-Json
            } else {
                # External service, check directly
                $port = $service.Value.Split(\":\")[1]
                $health = curl.exe -s \"http://localhost:$port/health\" 2>$null | ConvertFrom-Json
            }
            
            if ($health.status -eq \"ok\") {
                Write-Host \"  ✓ $($service.Key): healthy\" -ForegroundColor Green
            } else {
                Write-Host \"  ⚠ $($service.Key): check needed\" -ForegroundColor Yellow
            }
        } catch {
            Write-Host \"  ✗ $($service.Key): unreachable\" -ForegroundColor Red
        }
    }
} else {
    Write-Host \"  [SKIPPED] Health checks skipped\" -ForegroundColor Gray
}

Write-Host \"\" -ForegroundColor White
Write-Host \"=== DEPLOYMENT COMPLETE ===\" -ForegroundColor Cyan
Write-Host \"Fleet status:\" -ForegroundColor White
docker compose -f \"$ScriptDir/docker-compose.torus.fleet.yml\" ps
Write-Host \"\" -ForegroundColor White
Write-Host \"Access points:\" -ForegroundColor White
Write-Host \"  Website: http://192.168.0.39:3005\" -ForegroundColor Gray
Write-Host \"  Dashboard: http://192.168.0.39:3000 (LAN only)\" -ForegroundColor Gray
Write-Host \"  Inventory API: http://192.168.0.39:3200\" -ForegroundColor Gray
Write-Host \"  POS API: http://192.168.0.39:3100\" -ForegroundColor Gray
Write-Host \"  Prometheus: http://192.168.0.39:9090\" -ForegroundColor Gray
Write-Host \"  Grafana: http://192.168.0.39:3002\" -ForegroundColor Gray
Write-Host \"\" -ForegroundColor White
Write-Host \"View logs: docker compose logs -f <service>\" -ForegroundColor Gray
Write-Host \"Stop fleet: docker compose down\" -ForegroundColor Gray
