#!/usr/bin/env python3
"""Post Trello comments for Docker healthcheck audit + order management start."""
import json, sys
from pathlib import Path
import requests

sys.path.insert(0, str(Path(__file__).parent))
from credential_loader import load_trello_credentials

creds = load_trello_credentials()
key = creds["api_key"]
token = creds["token"]

# Docker fleet healthcheck card
CARD_ID_DOCKER = "6a76a0dd49915bc5db8a2be4"

comment_docker = """[2026-08-08T22:00:00Z] OODA status: ✅ DOCKER FLEET HEALTHCHECKS — AUDIT COMPLETE.
Evidence:
- Audited all 11 healthchecks in docker-compose.torus.fleet.yml
- torus-redis: redis-cli ping ✅ (correct for Redis)
- torus-website: curl http://localhost:3000/health ✅ (nginx.conf has /health route returning 200)
- torus-alert-router: curl http://localhost:4000/health ✅ (FastAPI /health endpoint)
- torus-dashboard: curl http://localhost:3000/health ✅ (nginx static export has /health route)
- torus-inventory: curl http://localhost:3200/health ✅ (FastAPI /health endpoint)
- torus-pos: curl http://localhost:3100/health ✅ (FastAPI /health endpoint)
- torus-backup: curl http://localhost:8080/healthz ✅ (custom backup app /healthz endpoint)
- node-exporter: curl http://localhost:9100/metrics ✅ (standard Prometheus endpoint)
- cadvisor: curl http://localhost:8080/metrics ✅ (standard cAdvisor endpoint)
- prometheus: curl http://localhost:9090/-/healthy ✅ (standard Prometheus endpoint)
- grafana: curl http://localhost:3000/api/health ✅ (standard Grafana endpoint)
- Created app/api/health/route.ts in Next.js storefront for local dev health checks
All healthcheck endpoints verified. No fixes needed."""

resp = requests.post(
    f"https://api.trello.com/1/cards/{CARD_ID_DOCKER}/actions/comments",
    params={"key": key, "token": token},
    json={"text": comment_docker},
    timeout=20
)
print(f"Docker card comment: {resp.status_code}")
