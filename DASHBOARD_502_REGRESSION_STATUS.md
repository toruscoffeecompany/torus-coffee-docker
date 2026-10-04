# Dashboard 502 Regression Status

Current state:
- Dashboard container build succeeded: `toruscoffee/torus-dashboard:20260806-v2`
- Redeployment blocked by name conflict with existing `torus-dashboard`/`torus-redis` containers on SQUIDSTATION Docker API

Required actions:
1. Remove/rename conflicting containers on SQUIDSTATION
2. Re-run `docker compose -f docker-compose.torus.fleet.yml up -d torus-dashboard`
3. Verify `/api/fleet`, `/api/tools`, `/api/security-docs`, `/api/hw`, `/api/rig-report` routes

Blockers:
- Missing dashboard routes owned by Sir Green
- `/api/status` timeout on large payload (Sir Green fix pending)
