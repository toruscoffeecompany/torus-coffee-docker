# Container Placement Rules — Local Network Build

## Host Roles

| Host | Tailscale IP | LAN IP | Role | Owner |
|------|-------------|--------|------|-------|
| SQUIDSTATION | 100.8.0.3 | 192.168.0.39 | Fleet/Security Stack (primary) | Sir Green |
| PINKCADY | 100.8.0.2 | 192.168.0.3 | Torus Coffee Ops + optional containers | Miss Pink |
| STEALTHATTACK | 100.8.0.4 | 192.168.0.32 | Render/AI containers only | Sir Azure |

## Container Placement

### SQUIDSTATION (Primary Fleet Host)
- **torus-redis** (port 6379, bound to 127.0.0.1)
- **torus-website** (port 3005:3000)
- **torus-alert-router** (port 4000, bound 127.0.0.1)
- **torus-dashboard** (port 3000, internal only)
- **torus-inventory** (port 3200, bound 127.0.0.1)
- **torus-pos** (port 3100, bound 127.0.0.1)
- **torus-backup** (port 8080, internal only)
- **node-exporter** (port 9100)
- **cadvisor** (port 8081:8080)
- **prometheus** (port 9090)
- **grafana** (port 3002:3000)

### PINKCADY (Miss Pink's Host — optional containers)
- **torus-redis** (optional local instance for development)
- **torus-dashboard** (optional local dev)
- Ollama container (llama3.2, port 11434)

### STEALTHATTACK (Sir Azure's Host — render/AI only)
- **ComfyUI** (GPU-accelerated, port 8188)
- **Render nodes** (Blender, FFmpeg)
- No fleet/security containers — SQUIDSTATION owns these

## Resource Limits
All containers use `deploy.resources.limits` and `deploy.resources.reservations` per docker-compose spec.
