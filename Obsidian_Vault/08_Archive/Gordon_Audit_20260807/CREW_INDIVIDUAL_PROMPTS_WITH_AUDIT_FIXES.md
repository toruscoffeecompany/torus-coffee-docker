# ⚓ INDIVIDUAL CREW PROMPTS
## With Deep-Dive Audit Fixes

---

## ⚡ SIR GREEN - READ THIS NOW

```
SIR GREEN,

Miss Gordon completed a deep-dive audit.
You have 4 NEW REQUIREMENTS before executing memory fix:

READ: DEEP_DIVE_AUDIT_INDIVIDUAL_REPORTS.md → "SIR GREEN - INDIVIDUAL AUDIT REPORT"

NEW TASKS (before 2-hour fix):

1. Backup your docker-compose.yml
   cp docker-compose.yml docker-compose.yml.backup.$(date +%Y%m%d)

2. Add health checks to EVERY service
   (Use the YAML block in the audit report)
   
   Example for torus-redis:
   ```yaml
   torus-redis:
     healthcheck:
       test: ["CMD", "redis-cli", "ping"]
       interval: 30s
       timeout: 10s
       retries: 3
   ```

3. Add log rotation to /etc/docker/daemon.json
   (Copy from audit report)
   
4. Verify changes syntax:
   docker-compose config  # Should output valid YAML, no errors

THEN execute your 2-hour memory fix (EXACT_PROMPT_FOR_SIR_GREEN.md)

THEN verify output with setup verification checklist (in audit report)

Report when done:
"Health checks: PASS
 Log rotation: PASS
 Memory: 3.5 GB (from 8.02 GB)
 All containers UP
 Ready for next phase"
```

---

## 💗 MISS PINK - READ THIS NOW

```
MISS PINK,

Miss Gordon completed a deep-dive audit.
You have 8 NEW REQUIREMENTS before executing 12-hour build:

READ: DEEP_DIVE_AUDIT_INDIVIDUAL_REPORTS.md → "MISS PINK - INDIVIDUAL AUDIT REPORT"

NEW TASKS (execute IN ORDER):

PRE-PHASE 1:
  1. Run prerequisite checks (PowerShell script in audit report)
     Should show: All checks PASS
     If any FAIL: Fix before proceeding

PHASE 2 FIX:
  2. Add webhook verification test (in audit report)
     After Phase 2, run: Kill container → Verify event cascade
     Check 4 endpoints: webhook logs → alert-router logs → Obsidian note → alert-router

PHASE 3 FIX:
  3. Replace bash backup script with PowerShell version (in audit report)
     Windows doesn't run bash natively
     Use: backup-volumes.ps1 instead

PHASE 4 FIX:
  4. Add K8s resource quotas (YAML block in audit report)
     Prevents pods from consuming all memory
     Add to k8s-torus-deployment.yaml BEFORE applying

PHASE 5 FIX:
  5. Add MCP retry logic (Python code in audit report)
     Handles connection failures gracefully
     Add to mcp_server_torus.py

PHASE 6 FIX:
  6. Use failure handling guide (in audit report)
     If any check fails: Go to troubleshooting section
     Know how to recover from each failure mode

DURING EXECUTION:
  7. Add safety checks before each phase (checklist in audit report)
     Verify prerequisites BEFORE starting each phase
     Don't skip even if confident

FINAL:
  8. Backup your work at each phase boundary
     docker-compose.ps -f docker-compose-torus-pinkcady.yml config > phase_X_final.yml

Report when done:
"Prerequisite checks: PASS
 Phase 1-6: All complete
 Verification: 12/12 checks PASS
 No failures encountered
 System live and stable"
```

---

## 🔵 SIR AZURE - READ THIS NOW

```
SIR AZURE,

Miss Gordon completed a deep-dive audit.
You have 5 NEW REQUIREMENTS before GPU activation:

READ: DEEP_DIVE_AUDIT_INDIVIDUAL_REPORTS.md → "SIR AZURE - INDIVIDUAL AUDIT REPORT"

NEW TASKS (execute IN ORDER):

BEFORE GPU SETUP:
  1. Verify CUDA compatibility (commands in audit report)
     Run: nvidia-smi
     Must show: GPU present + CUDA Capability 8.6+
     If missing GPU: Stop, install nvidia drivers

DURING DOCKER SETUP:
  2. Add GPU memory limits (YAML block in audit report)
     Update docker-compose-gpu.yml
     Set: memory_limit_mb: 16000 (cap at 16GB of 24GB)
     This prevents job from starving system

BEFORE TAILSCALE:
  3. Understand device approval workflow (in audit report)
     After you run: tailscale up
     Captain or Miss Pink MUST approve in Tailscale console
     Don't proceed until approved

BEFORE SERVICES START:
  4. Secure JupyterLab + MinIO (code in audit report)
     Change JupyterLab token from 'pirate_fleet_token_2026'
     Change MinIO creds from 'minioadmin/minioadmin'
     Use: openssl rand -base64 32 (for strong passwords)

FINAL:
  5. Use GPU job submission template (Python script in audit report)
     Wraps all GPU jobs with safety limits
     Prevents job from consuming all 24GB GPU memory
     Use: python submit_gpu_job.py <job_name> <image> <script>

Report when done:
"GPU detected: NVIDIA RTX 4090
 CUDA version: 12.1+ compatible
 Docker runtime: nvidia enabled
 Tailscale: 100.110.238.68 connected
 JupyterLab: Secured with token
 MinIO: Secured with credentials
 GPU memory: Capped at 16GB
 Job template: Deployed
 Ready for GPU workloads"
```

---

## 🎯 EXECUTION PRIORITY

**DO NOT SKIP THESE FIXES:**

SIR GREEN:
  ❌ CRITICAL: Health checks (containers won't auto-alert if dead)
  ❌ CRITICAL: Log rotation (system will fill disk in 30 days otherwise)

MISS PINK:
  ❌ CRITICAL: PowerShell backup script (bash won't work on Windows)
  ❌ CRITICAL: K8s resource quotas (pods will OOM without limits)
  ❌ CRITICAL: Prerequisite checks (catch issues before they cascade)

SIR AZURE:
  ❌ CRITICAL: GPU memory limits (job can starve entire system)
  ❌ CRITICAL: Tailscale device approval (won't connect without it)
  ❌ CRITICAL: Credentials change (default creds are security risk)

---

## EXECUTION SEQUENCE

```
T+0:00  Each crew reads their audit report → Implements fixes
T+1:00  Sir Green STARTS memory fix (with health checks + log rotation)
T+1:00  Sir Azure STARTS GPU activation (with GPU limits + security)
T+2:00  Miss Pink STARTS Phase 1 (after prerequisite checks PASS)
T+3:00  Sir Green COMPLETES (signals Miss Pink)
T+5:00  Sir Azure COMPLETES (signals Captain)
T+14:00 Miss Pink COMPLETES (all phases + fixes)
T+14:00 SYSTEM LIVE (all fixes active, hardened, monitored)
```

---

⚓ **Miss Gordon says:**

Read your audit report.
Apply the fixes.
They are small but critical.
System will be production-grade after these changes.

Go.
```

---

## SEND TO EACH

**TO SIR GREEN:** Copy SIR GREEN section
**TO MISS PINK:** Copy MISS PINK section
**TO SIR AZURE:** Copy SIR AZURE section

Each crew member now has:
1. Their individual audit report (20 KB, specific to them)
2. Their individual prompt (with NEW requirements)
3. Exact code/scripts they need to add
4. Safety checks before each phase
5. Failure handling guides
