# ⚓ UPDATED CREW PROMPTS: NOW WITH SIR AZURE + STEALTHATTACK
## Complete 4-Ship Pirate Fleet Coordination

**From:** Miss Gordon (Docker Systems)  
**To:** Entire Pirate Crew + Sir Azure  
**Date:** 2026-08-06 06:30 UTC  
**Status:** UPDATED with GPU pipeline integration

---

## THE COMPLETE PIRATE FLEET

```
🏴‍☠️ CAPTAIN (Leadership)
   Ship: Flagship (strategic oversight)
   Role: Monitor all operations

⚡ SIR GREEN (SQUIDSTATION - 192.168.0.39 / 100.83.247.14)
   Ship: SQUIDSTATION (16 CPUs, 15.59 GB RAM)
   Role: Infrastructure & memory management
   Mission: 2-hour memory crisis fix
   Status: Online

💗 MISS PINK (PINKCADY - 192.168.0.3 / 100.106.235.103)
   Ship: PINKCADY (8 CPUs, 8 GB RAM)
   Role: Operations & automation orchestrator
   Mission: 12-hour 5-phase infrastructure build
   Status: Online

🔵 SIR AZURE (STEALTHATTACK - 192.168.0.10 / 100.110.238.68)  ← NEW
   Ship: STEALTHATTACK (8 CPUs, 32 GB RAM, GPU capable)
   Role: GPU & AI pipeline operations
   Mission: 4-hour GPU infrastructure activation + integration
   Status: Activating now

🤖 MISS GORDON (Docker Systems)
   Role: Monitor health, troubleshoot, maintain documentation
   Status: On standby
```

---

## READING ORDER FOR COMPLETE CREW

### 🏴‍☠️ CAPTAIN (Same as before, now extended)

**Read (2 hours total):**
1. 00_START_HERE_GORDON_SUMMARY.md (7 min)
2. COMPLETE_AUTOMATION_ANALYSIS.md Parts 1-3 (30 min)
3. TAILSCALE_DOCKER_CONNECTIVITY_ANALYSIS.md (20 min) — NEW
4. FULL_SYSTEM_ANALYSIS_AND_ACTION_PLAN.md (executive sections, 15 min)

**New responsibility:** Monitor STEALTHATTACK GPU pipeline on dashboard

**Dashboard now shows:**
- SQUIDSTATION: 9 Torus + 6 VOID containers
- PINKCADY: 7 Torus + K3s cluster
- STEALTHATTACK: GPU services + monitoring ← NEW

---

### ⚡ SIR GREEN (SQUIDSTATION) — Same as before

**Read (30 minutes):**
1. EXACT_PROMPT_FOR_SIR_GREEN.md (your playbook)

**Mission:** 2-hour memory fix (unchanged)

**New:** After fix, coordinate with Sir Azure on GPU metrics integration

---

### 💗 MISS PINK (PINKCADY) — Slightly expanded

**Read (2 hours total):**
1. EXACT_PROMPT_FOR_MISS_PINK.md (40 min)
2. MISS_PINK_MASTER_INFRASTRUCTURE_PLAN.md (reference, 20 min)
3. TAILSCALE_DOCKER_CONNECTIVITY_ANALYSIS.md (cross-ship concepts, 20 min) — NEW
4. MISS_GORDON_END_TO_END_VERIFICATION.md (verification, 10 min)

**Mission:** 12-hour 5-phase build (unchanged)

**New:** After Phase 5 MCP toolkit, you'll see STEALTHATTACK in Claude Desktop automation queries

---

### 🔵 SIR AZURE (STEALTHATTACK) — BRAND NEW ROLE

**Read (1.5 hours):**
1. EXACT_PROMPT_FOR_SIR_AZURE.md ← YOUR PLAYBOOK (40 min)
2. TAILSCALE_DOCKER_CONNECTIVITY_ANALYSIS.md (connectivity concepts, 30 min)
3. COMPLETE_AUTOMATION_ANALYSIS.md Parts 1-3 (understand hive mind, 20 min)

**Mission:** 4-hour GPU infrastructure activation
- Hour 1: Wake STEALTHATTACK + Tailscale join
- Hour 1.5: Docker + GPU setup
- Hour 1: Integration with fleet
- Hour 0.5: Verification + testing

**Timeline:** Start after Sir Green's 2-hour fix (Sir Green and Sir Azure in parallel ok)

---

### 👥 ENTIRE CREW (Everyone including Sir Azure)

**Read (1 hour mandatory):**
1. COMPLETE_AUTOMATION_ANALYSIS.md Parts 1-3
2. TAILSCALE_DOCKER_CONNECTIVITY_ANALYSIS.md (new connectivity layer)

**Why:** Understand how 3 ships become 1 coordinated system

---

## UPDATED 48-HOUR TIMELINE

```
HOUR 0: Preparation (1 hour)
  ├─ Captain reads overview (2 hours of reading)
  ├─ Sir Green reads his playbook (30 min)
  ├─ Miss Pink reads hers (2 hours)
  ├─ Sir Azure reads his (1.5 hours)
  └─ Crew reads automation + Tailscale analysis (1 hour)

HOUR 1: Parallel execution starts
  ├─ Sir Green: Memory crisis fix (2 hours)
  │   └─ T+0:00 - T+2:00 = Memory fix complete
  └─ Sir Azure: GPU activation (4 hours, in parallel)
      └─ T+0:00 - T+4:00 = STEALTHATTACK online + integrated

HOUR 2: After Sir Green's fix completes
  └─ Miss Pink: Infrastructure build (12 hours)
      ├─ Phase 1 (1 hour): Docker optimization
      ├─ Phase 2 (2 hours): Webhooks
      ├─ Phase 3 (1.5 hours): Volumes
      ├─ Phase 4 (2 hours): Kubernetes
      ├─ Phase 5 (1 hour): MCP toolkit
      └─ Phase 6 (2 hours): Verification

HOUR 5: Status check
  ├─ Sir Green: Complete + SQUIDSTATION stable ✅
  ├─ Sir Azure: Halfway through (Hour 2.5) → GPU services running ✅
  └─ Miss Pink: Phase 1-2 complete (3 hours in) ✅

HOUR 6: STEALTHATTACK comes online
  ├─ Sir Azure: Complete + integrated ✅
  ├─ STEALTHATTACK: Visible on dashboard
  ├─ GPU metrics: Flowing to Prometheus
  ├─ Alert routing: Active for STEALTHATTACK
  └─ OODA loop: Detecting STEALTHATTACK events

HOUR 14: Full deployment complete
  ├─ Sir Green: Memory fix ✅
  ├─ Sir Azure: GPU pipeline ✅
  ├─ Miss Pink: Infrastructure build ✅
  └─ All 3 ships: Operational, coordinated, automated

HOUR 14+: System live 24/7
  ├─ Captain: Monitoring dashboard (3 ships visible)
  ├─ Sir Green: Responding to escalations (memory/infrastructure)
  ├─ Sir Azure: Managing GPU workloads + monitoring
  ├─ Miss Pink: Processing automation, running OODA loop
  └─ Hive mind: Running continuously (alerts → tasks → resolution)
```

---

## CROSS-SHIP DOCKER CONNECTIVITY

**What's now possible:**

```
From SQUIDSTATION:
  docker --context pinkcady ps                    # See PINKCADY containers
  docker --context stealthattack-gpu ps           # See STEALTHATTACK containers
  docker --context stealthattack-gpu logs gpu-monitor

From PINKCADY:
  docker --context torus-squidstation ps          # See SQUIDSTATION
  docker --context stealthattack-gpu ps           # See STEALTHATTACK
  docker --context stealthattack-gpu exec ... nvidia-smi

From STEALTHATTACK:
  docker --context squidstation ps                # See SQUIDSTATION
  docker --context pinkcady ps                    # See PINKCADY
  docker --context squidstation logs void-prometheus

RESULT: 3 ships, 1 coordinated Docker swarm (via Tailscale)
```

---

## SIR AZURE'S INTEGRATION POINTS

### During his 4-hour activation:

**Hour 1:** Wake STEALTHATTACK + Tailscale
- Machine boots
- GPU visible (nvidia-smi)
- Joins Tailscale mesh (100.110.238.68)
- Can reach both other ships

**Hour 1.5:** Docker + GPU setup
- Docker installed
- NVIDIA Container Toolkit installed
- GPU accessible in containers
- Docker API on :2375

**Hour 1:** Fleet integration
- Seen by webhook (can send events)
- Metrics flowing to Prometheus
- Alert routes configured
- OODA loop aware of STEALTHATTACK

**Hour 0.5:** Verification
- Cross-ship docker ps works
- GPU exporter responds (:9445)
- Node exporter responds (:9100)
- Dashboard shows STEALTHATTACK ✅

---

## AFTER SIR AZURE COMPLETES

**What happens next:**

```
SIR AZURE REPORTS: "STEALTHATTACK online, GPU pipeline active"
                   ↓
CAPTAIN SEES: STEALTHATTACK appears on dashboard (192.168.0.39:8089)
              Shows: GPU 0%, metrics flowing, alerts active
                   ↓
MISS PINK CAN: Query STEALTHATTACK status from Claude Desktop
               (via MCP toolkit in Phase 5)
               Example: "What's the status of STEALTHATTACK GPU?"
               Claude: "NVIDIA RTX 4090 available, idle, ready for jobs"
                   ↓
SIR GREEN CAN: Access STEALTHATTACK containers from SQUIDSTATION
               docker --context stealthattack-gpu ps
                   ↓
ANY ALERT ON STEALTHATTACK:
  GPU temp high → Email to Sir Azure
  GPU job fails → Obsidian note → OODA → Trello card
  Container crash → Alert cascade (same as Torus)
                   ↓
BACKUP INTEGRATION: Volumes can sync STEALTHATTACK→PINKCADY→Z:drive
                   ↓
AI PIPELINE READY: Any crew member can submit GPU jobs
                   Jobs run on STEALTHATTACK
                   Metrics displayed on dashboard
                   Results synced back
```

---

## STEALTHATTACK IN THE HIVE MIND

**Complete automation cascade includes STEALTHATTACK:**

```
GPU JOB STARTS ON STEALTHATTACK
  ↓
nvidia-smi reports usage
  ↓
GPU exporter :9445 collects metrics
  ↓
Prometheus on SQUIDSTATION scrapes (every 15s)
  ↓
Grafana on SQUIDSTATION displays
  ↓
Dashboard shows: "STEALTHATTACK GPU: 78% utilization"
  ↓
If GPU temp > 80°C:
  ├─ Alert fires in Prometheus
  ├─ Sent to webhook (100.106.235.103:8888)
  ├─ Alert Router processes (severity: warning)
  ├─ Obsidian note created
  ├─ OODA loop detects (60s)
  ├─ Trello card: "GPU cooling - review workload"
  ├─ GitHub issue: "[warning] GPU temp spike"
  └─ Sir Azure notified

JOB COMPLETES
  ├─ Success alert: "✅ AI job complete: model_inference (42s)"
  ├─ Obsidian notes
  ├─ Trello card updated
  ├─ GitHub issue closed
  ├─ Results synced to backup
  └─ Dashboard shows: "Job completed"

FULL CYCLE TIME: < 5 minutes (submission to dashboard + notification)
```

---

## UPDATED SUCCESS CRITERIA (48 hours)

**After Sir Green's 2-hour work:**
- Memory: 8.02 GB → 3.5 GB ✅
- All containers: UP ✅

**After Sir Azure's 4-hour work:**
- STEALTHATTACK: Online ✅
- GPU: Accessible + metrics flowing ✅
- Cross-ship docker contexts: Working ✅
- Alert routing: Active ✅
- Dashboard: Shows STEALTHATTACK ✅

**After Miss Pink's 12-hour work:**
- All 5 phases: Complete ✅
- K8s: Running ✅
- MCP: Connected ✅
- Verification: 12/12 checkpoints ✅

**System live:**
- Dashboard: All 3 ships visible + healthy ✅
- OODA loop: Processing all events ✅
- Alerts: Routing across all ships ✅
- Cross-ship: Docker access working ✅
- GPU pipeline: Ready for workloads ✅

---

## EXACT PROMPTS TO GIVE EACH CREW MEMBER

### To Captain:
```
"Read the infrastructure overview (2 hours). Make 3 decisions:
 1. Load balancing strategy?
 2. Remove Zeek?
 3. Approve full deployment?
 
 You now have 3 ships instead of 2.
 SQUIDSTATION: Infrastructure flagship
 PINKCADY: Operations hub + automation
 STEALTHATTACK: GPU pipeline (NEW)
 
 Dashboard shows all 3. Your job: Monitor + decide."
```

### To Sir Green:
```
"Execute 2-hour memory fix (EXACT_PROMPT_FOR_SIR_GREEN.md).
 After you complete, Sir Azure will activate STEALTHATTACK
 in parallel with Miss Pink's infrastructure build.
 
 When done: Report 'Memory 3.5 GB, SQUIDSTATION stable'"
```

### To Sir Azure (NEW):
```
"Execute 4-hour GPU activation (EXACT_PROMPT_FOR_SIR_AZURE.md).
 Bring STEALTHATTACK online, join the pirate fleet via Tailscale.
 
 You work in parallel with Sir Green (both start Hour 1).
 You finish before Miss Pink starts Phase 1.
 
 When done: Report 'STEALTHATTACK online, GPU pipeline active,
 integrated with fleet'"
```

### To Miss Pink:
```
"After Sir Green confirms memory stable, execute 12-hour
 infrastructure build (5 phases + verification).
 
 Note: Sir Azure will bring STEALTHATTACK online during your work.
 Around Hour 6 you'll see it appear on dashboard.
 
 Don't worry about it, just focus on phases 1-5. 
 It's automated."
```

### To Entire Crew:
```
"Read COMPLETE_AUTOMATION_ANALYSIS.md + 
 TAILSCALE_DOCKER_CONNECTIVITY_ANALYSIS.md
 
 You're now managing a 3-ship pirate fleet coordinated 
 via Tailscale mesh + Docker API.
 
 When something breaks: Check the alert, understand the 
 cascade flow, execute the fix."
```

---

## FILE LOCATIONS (UPDATED)

```
D:\Work\Torus Coffee Company LLC\00_Inbox\

CORE DOCUMENTS:
  README_START_HERE_CREW.txt ..................... Quick reference
  00_START_HERE_GORDON_SUMMARY.md ............... Entry point
  EXACT_PROMPTS_FOR_ENTIRE_CREW.md ............. Who reads what

EXACT PLAYBOOKS:
  EXACT_PROMPT_FOR_SIR_GREEN.md ................ Memory fix (2 hours)
  EXACT_PROMPT_FOR_MISS_PINK.md ............... Infrastructure (12 hours)
  EXACT_PROMPT_FOR_SIR_AZURE.md ← NEW ......... GPU activation (4 hours)

COMPLETE ANALYSIS:
  COMPLETE_AUTOMATION_ANALYSIS.md ............. 8-stage cascade
  TAILSCALE_DOCKER_CONNECTIVITY_ANALYSIS.md ← NEW ... 3-ship networking

REFERENCE:
  FULL_SYSTEM_ANALYSIS_AND_ACTION_PLAN.md ...... Crisis + solutions
  MISS_PINK_MASTER_INFRASTRUCTURE_PLAN.md ..... All 5 phases + code
  MISS_GORDON_END_TO_END_VERIFICATION.md ...... Verification checklist

Z:\SIR_GREEN_INBOX\
  EXACT_PROMPT_FOR_SIR_GREEN.md ............... Sir Green's copy
```

---

## DEPLOYMENT COORDINATION

**All 3 operations start near same time, finish in sequence:**

```
Hour 0: Prep (everyone reads)
Hour 1: Sir Green + Sir Azure start (parallel)
Hour 2: Miss Pink starts (Sir Green finishing)
Hour 5: Miss Pink Phase 1-2 (Sir Azure finishing)
Hour 6: Full team: Sir Green ✅, Sir Azure ✅, Miss Pink in Phase 3
Hour 14: Miss Pink finishes (Phases 1-6 complete)
Hour 14+: All 3 ships live, automation running 24/7
```

---

## STATUS: DEPLOYMENT READY WITH GPU PIPELINE

✅ **Captain:** Knows the 3-ship fleet topology  
✅ **Sir Green:** 2-hour memory fix ready  
✅ **Miss Pink:** 12-hour infrastructure build ready  
✅ **Sir Azure:** 4-hour GPU activation ready  
✅ **Connectivity:** Tailscale mesh + Docker API documented  
✅ **Hive mind:** 8-stage cascade includes all 3 ships  
✅ **Documentation:** Updated for new role  

**DEPLOYMENT READINESS: 100%**

⚓ **From Miss Gordon to the Complete Pirate Fleet:**

You now have three ships. Three commanders. One hive mind.

Sir Green fixes the crisis. Sir Azure brings the GPU lane. Miss Pink builds the automation.

All coordinated via Tailscale mesh. All connected via Docker API. All visible on one dashboard.

The pirate fleet is ready to sail.

Execute with confidence.

**Next:** Captain approves → Sir Green + Sir Azure start → Miss Pink builds → System lives

⚓ **HOIST THE JOLLY ROGER** 🏴‍☠️
