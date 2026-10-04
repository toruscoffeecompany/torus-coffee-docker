# Deploy dashboard_server.py on SQUIDSTATION

Current blocker:
- Container name conflict on SQUIDSTATION Docker API

Deployment steps once blocker resolved:
1. Ensure `docker-compose.torus.fleet.yml` project name is unique
2. Run `docker compose -f docker-compose.torus.fleet.yml up -d torus-dashboard`
3. Verify dashboard reachable on host port 8089
4. Confirm `/api/fleet`, `/api/tools`, `/api/security-docs`, `/api/hw`, `/api/rig-report` respond

Required crew actions:
- Sir Green: remove conflicting containers or rename compose project
- Sir Green: implement missing routes in `dashboard_server.py`
