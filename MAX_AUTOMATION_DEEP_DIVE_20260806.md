# DEEP DIVE: MAX OUT DOCKER AUTOMATION
## Target: webhooks, logs, volumes, Kubernetes

### Current state
- 9 containers on torus-network
- Prometheus + Grafana + node-exporter + cAdvisor running
- torus-alert-router has /health, but integrations not live
- Backup runs locally, no S3
- No centralized logging beyond json-file driver
- No Kubernetes manifests
- Cross-host mesh: Tailscale only; no overlay/Swarm

### Improvements to implement
1. Add fleet-wide restart policies and healthcheck retries
2. Add Loki/fluent-bit for log aggregation
3. Add webhook broadcaster for container events
4. Add backup volume snapshot + optional S3 upload
5. Enable Kubernetes on SQUIDSTATION and PINKCADY
6. Add alertmanager + notification routes for Prometheus
7. Add service mesh DNS + retries for internal APIs
8. Add cron-driven health + fleet verification script
