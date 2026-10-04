# Sir Azure: ComfyUI/Redis/MinIO/Postgres/Nginx on SQUIDSTATION

Stack:
- ComfyUI: AI image generation
- Redis: job queue/cache
- MinIO: local object storage
- Postgres: metadata persistence
- Nginx: reverse proxy

Free-tier path:
1. Use existing SQUIDSTATION Docker engine
2. Create compose override or new compose file
3. Bind-mount models to existing storage
4. Expose only local network ports

Next actions:
1. Sir Azure to create `docker-compose.sir-azure.yml` on SQUIDSTATION
2. Test ComfyUI UI on local port
3. Add health checks and restart policies
