# MISS PINK COMMUNICATION PROTOCOL

## Purpose
Establishes bidirectional communication between Miss Pink (PINKCADY, 192.168.0.3)
and Sir Green (SQUIDSTATION, 192.168.0.39) over LOCAL NETWORK.

## Connection Channels

### 1. Docker API Access (PINKCADY → SQUIDSTATION)
- **Proxy URL**: `http://192.168.0.39:2376`
- **Full CRUD**: GET, POST, PUT, DELETE supported
- **Test**: `curl http://192.168.0.39:2376/_ping` → should return `OK`
- **Containers**: `curl http://192.168.0.39:2376/containers/json`
- **Start container**: `curl -X POST http://192.168.0.39:2376/containers/{id}/start`
- **Stop container**: `curl -X POST http://192.168.0.39:2376/containers/{id}/stop`

### 2. Health Status (PINKCADY → SQUIDSTATION)
- **Health URL**: `http://192.168.0.39:9999/verify`
- **Simple check**: `http://192.168.0.39:9999/healthz`
- **Returns JSON**: container counts, fleet status, k8s pods

### 3. Vault File Access (BOTH DIRECTIONS)
- **Network share**: `\\192.168.0.39\Vault`
- **PINKCADY mount**: Z: drive (read-only)
- **SYNC directory**: `\\192.168.0.39\Vault\Developer_Brain\Shared_With_Pink`
- **Protocol**: Drop files in `SYNC/` → PINKCADY picks them up automatically

### 4. Response Path (SQUIDSTATION → PINKCADY)

#### Option A: File-based (automatic)
Drop response files in:
```
\\192.168.0.39\Vault\Developer_Brain\Shared_With_Pink\PINKCADY_INBOX\
```
Miss Pink's watchdog will auto-index these within 60 seconds.

#### Option B: Docker container (real-time)
Deploy a lightweight container that polls for work:
```yaml
services:
  sir-green-comm:
    image: alpine:latest
    command: sh -c "while true; do curl -s http://vault-proxy:9999/verify > /dev/null && echo '\$(date): Sir Green alive'; sleep 60; done"
    volumes:
      - //192.168.0.39/Vault/Shared_With_Pink/PINKCADY_INBOX:/inbox
```

### 5. Torus Coffee Business Data
- **Email**: toruscoffeecompany@gmail.com
- **Vault path**: `02_Business_Operations/Torus_Coffee/`
- **Sync**: Weekly reports to `Shared_With_Pink/TORUS_COFFEE_REPORTS/`

## Miss Pink Template Selection

When Miss Pink boots up on PINKCADY, she can choose:

### Option 1: Full Vault Replication
```bash
robocopy \\192.168.0.39\Vault "C:\Obsidian_Vaults\Miss_Pink" /MIR /EXCLUDE:exclude.txt
```
- **Pros**: Complete copy of all operational docs
- **Cons**: ~35K files, large disk usage

### Option 2: Selective Sync (RECOMMENDED)
Copy only essential directories:
- `02_Business_Operations/Infrastructure/` (Docker configs, startup scripts)
- `03_AI_Operating_System/Brain_MissPink/` (her AI personality)
- `Shared_With_Pink/` (communication channel)
- `02_Business_Operations/Communications/` (protocols)
- `02_Business_Operations/Torus_Coffee/` (business docs)

Command:
```bash
robocopy \\192.168.0.39\Vault\Developer_Brain\02_Business_Operations\Infrastructure "C:\Obsidian_Vaults\Miss_Pink\Infrastructure" /MIR
robocopy \\192.168.0.39\Vault\Developer_Brain\03_AI_Operating_System\Brain_MissPink "C:\Obsidian_Vaults\Miss_Pink\Brain_MissPink" /MIR
robocopy \\192.168.0.39\Vault\Developer_Brain\Shared_With_Pink "C:\Obsidian_Vaults\Miss_Pink\Shared_With_Pink" /MIR
```

### Option 3: Live Access (NO COPY)
Mount as network drive:
```
net use Z: \\192.168.0.39\Vault /persistent:yes
```
- **Pros**: Always current, zero disk usage
- **Cons**: Requires network connectivity

## Communication Protocol

### Miss Pink → Sir Green
1. Drop work files in `Shared_With_Pink/PINKCADY_INBOX/`
2. Health check auto-updates with status
3. Docker proxy enables remote container management

### Sir Green → Miss Pink
1. Drop response files in `Shared_With_Pink/SIR_GREEN_INBOX/`
2. Miss Pink's render_watchdog indexes new files automatically
3. Health check endpoint shows current status

## Quick Start (Miss Pink)

```bash
# 1. Verify connection
curl http://192.168.0.39:2376/_ping

# 2. Check fleet status  
curl http://192.168.0.39:9999/verify

# 3. See all containers
curl http://192.168.0.39:2376/containers/json | python3 -m json.tool

# 4. Read Sir Green's latest message
cat \\192.168.0.39\Vault\Developer_Brain\Shared_With_Pink\SIR_GREEN_INBOX\*.md
```

## Status
- ✅ Local network: PINKCADY (192.168.0.3) ↔ SQUIDSTATION (192.168.0.39)
- ✅ Docker proxy: Running (port 2376)
- ✅ Health check: Running (port 9999)
- ✅ Email: toruscoffeecompany@gmail.com
- ✅ Vault access: GitHub → `git.void.local` path active
