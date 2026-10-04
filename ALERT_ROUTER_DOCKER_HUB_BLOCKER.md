# Alert Router Docker Hub Push Blocker

Status: BLOCKED

Symptom:
- `toruscoffee/torus-alert-router:latest` push blocked
- SQUIDSTATION images blocked by auth

Required actions:
1. Provide SQUIDSTATION with Docker Hub PAT or org write access
2. Re-run push from SQUIDSTATION or PINKCADY
3. Verify image exists on shared Docker Hub
4. Deploy `torus-alert-router` via `docker-compose.torus.fleet.yml`

Workaround:
- Use local image tag until Hub auth resolved
