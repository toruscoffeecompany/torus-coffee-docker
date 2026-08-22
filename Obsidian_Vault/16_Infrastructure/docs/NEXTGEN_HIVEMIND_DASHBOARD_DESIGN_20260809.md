# Next-Gen HiveMind Dashboard Design

## Overview
The Next-Gen HiveMind Dashboard unifies crew status, container health, and security metrics across all local network hosts (SQUIDSTATION, PINKCADY, STEALTHATTACK).

## WHITE WHALE OPSEC Auth
- **Protocol:** Level 1-3 classification framework (Landlubber → Deckhand → Quartermaster)
- **Auth:** Client-side SHA-256 + HMAC passphrase gate (v3.0)
- **Port:** Dashboard accessible via Tailscale only (100.x.x.x)
- **Gateway:** Consolidated gateway routes /dashboard, /trello, /github, /vault-sync

## API Endpoints (TOOL_AE Dashboard)
- `GET /` — Service status
- `GET /health` — Health check (force-dynamic)
- `GET /status` — Fleet service health
- `GET /vault-sync` — Git dirty state + crew state files
- `GET /trello` — Board card counts by list + priority
- `GET /github` — Open issue counts per repo

## Architecture
```
[Internet]
  └── [Tailscale] ← only access path
      ├── PINKCADY:11434     (Ollama)
      ├── SQUIDSTATION:6000  (TOOL_AE Dashboard)
      └── STEALTHATTACK:8188 (ComfyUI)
```

## Host Placement
See `container_placement_rules.md` for full placement matrix.

## Deployment
- Docker compose: `Docker/docker-compose.torus.fleet.yml`
- Healthchecks: wget (not curl for Alpine base images)
- Volumes: named volumes for persistence, bind mounts for config
