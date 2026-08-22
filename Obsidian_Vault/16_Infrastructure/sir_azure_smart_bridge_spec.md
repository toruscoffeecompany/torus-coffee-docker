# Smart Bridge to Sir Azure — GPU Render Pipeline Spec

## Bridge: Miss Pink ↔ Sir Azure (STEALTHATTACK)

### Objective
Connect Miss Pink's automation pipeline (PINKCADY) to Sir Azure's GPU render
rig (STEALTHATTACK) so that AI image/video generation jobs can be offloaded
to the better graphics hardware.

### Host Map
| Host | Tailscale IP | LAN IP | Role | Assigned To |
|------|-------------|--------|------|-------------|
| PINKCANY | 100.8.0.3 | 192.168.0.3 | Ops + Ollama LLM | Miss Pink |
| STEALTHATTACK | 100.8.0.4 | 192.168.0.32 | Render/AI containers | Sir Azure |
| SQUIDSTATION | 100.8.0.5 | 192.168.0.39 | Fleet/security stack | Captain/Sir Green |

### Current State
- PINKCADY has NVIDIA GeForce GT 1030 (limited CUDA compute)
- STEALTHATTACK hosts ComfyUI on port 8188 (GPU-accelerated)
- ComfyUI container is defined in docker-compose.torus.fleet.yml
- Sir Azure's profile: SIR_AZURE_ASTRO_PROFILE.md — Render Midshipman

### Bridge Specification

#### 1. Render Job Relay
- Miss Pink's automation places render prompts in shared queue
- Queue location: `Z:\Developer_Brain\Shared_With_Pink\Render_Queue\` (or vault path)
- Sir Azure's render watcher picks up jobs from queue
- Output written to shared relay queue

#### 2. API Endpoint
- `POST http://STEALTHATTACK:8188/api/render/comfy/prompt` — submit ComfyUI prompt
- `POST http://STEALTHATTACK:8188/api/render/status` — check job status
- Authentication: shared crew token (from secrets.local.json vault)

#### 3. Crew Assignment
- **Job submitter:** Miss Pink (PINKCADY)
- **Job processor:** Sir Azure (STEALTHATTACK)
- **Job relay:** alert_router.py routes render results back to Miss Pink's inbox

#### 4. What Sir Azure Needs to Do
1. Confirm STEALTHATTACK's GPU model (RTX series)
2. Verify ComfyUI container is running and accessible on port 8188 via Tailscale
3. Confirm shared render queue path is mounted/accessible
4. Set up render_watcher.py to consume jobs from queue
5. Test a sample prompt from Miss Pink's automation

#### 5. Files Referenced
- `Docker/docker-compose.torus.fleet.yml` — ComfyUI service definition
- `14_Infrastructure/container_placement_rules.md` — Host placement rules
- `10_Skills_Library/05_Operations/AUTOMATION_TRACKER.md` — AI pipeline task
- `10_Skills_Library/05_Operations/Crew/Torus_Crew/SIR_AZURE_ASTRO_PROFILE.md` — Sir Azure's profile

### Priority
P1 — High (blocks AI media pipeline)

### Due Date
2026-08-13 (7 days from today)
