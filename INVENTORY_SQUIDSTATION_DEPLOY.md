# torus-inventory: Deploy Fixed FastAPI Image on SQUIDSTATION

Current state:
- Image built and tagged locally
- Deployment pending SQUIDSTATION container restart

Steps:
1. Push fixed image to shared Docker Hub or load locally on SQUIDSTATION
2. Run inventory service on SQUIDSTATION with volume mounts for `inventory.json`
3. Verify `/health` and `/items` endpoints
4. Update Trello card with deployment evidence

Blocker:
- SQUIDSTATION Docker context and auth
