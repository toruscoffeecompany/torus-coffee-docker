# Sir Azure Steelwake — Final Build Template & Checklist

**Based on:** SQUIDSTATION Discord bot designs + Gordon’s architecture template  
**Station:** STEALTHATTACK (Son's PC)  
**Role:** Render Midshipman / Heavy Lift Officer  
**Color:** #4F7FFF

---

## Hardware Checklist

### Required
- [ ] RTX 3060 12GB GPU confirmed
- [ ] Docker Desktop installed
- [ ] ComfyUI installed and running
- [ ] Stable Diffusion models loaded
- [ ] Tailscale installed and authenticated
- [ ] Hermes agent installed

### Verify
```bash
# GPU detection
nvidia-smi

# Docker
docker --version

# Tailscale
tailscale status

# Network connectivity
ping 192.168.0.39
```

---

## Docker Setup

### 1. Create Docker Context
```bash
docker context create squidstation \
  --docker "host=tcp://192.168.0.39:2375" \
  --description "VOID/Torus Shared Docker"
```

### 2. Test Connection
```bash
docker context use squidstation
docker ps -a
```

### 3. Render Pipeline Containers
```yaml
# docker-compose.azure.yml
version: '3.8'
services:
  comfyui:
    image: comfyui:latest
    ports:
      - "8188:8188"
    volumes:
      - ./ComfyUI:/app
    deploy:
      resources:
        reservations:
          devices:
            - driver: nvidia
              count: all
              capabilities: [gpu]

  stable-diffusion:
    image: stabilityai/sdxl:latest
    volumes:
      - ./models:/models
    deploy:
      resources:
        reservations:
          devices:
            - driver: nvidia
              count: all
              capabilities: [gpu]
```

---

## Discord Bot Setup

### 1. Create Discord Application
- Name: `VOID Sir Azure Steelwake`
- Bot username: `Sir Azure Steelwake`
- Channel: `#sir-azure`
- Token env: `DISCORD_SIR_AZURE_TOKEN`

### 2. Enable Intents
- MESSAGE CONTENT INTENT: ✅
- SERVER MEMBERS INTENT: ✅

### 3. Upload Assets
- Icon: `sir_azure_icon.png` (1024×1024)
- Banner: `sir_azure_banner.png` (1120×450)
- Theme: Azure blue (#4F7FFF) over graphite

### 4. Add to crew_map.json
```json
"sir_azure": {
  "name": "Sir Azure Steelwake",
  "discord_user_id": "REPLACE_WITH_SIR_AZURE_DISCORD_USER_ID",
  "rank": 4,
  "title": "Render Midshipman / Heavy Lift Officer",
  "role": "render_midshipman",
  "station": "STEALTHATTACK (Son's PC)",
  "channel": "sir-azure",
  "account_type": "bot",
  "sync_target": "Hermes on STEALTHATTACK",
  "reports_to": ["sir_green", "captain", "sir_violet"],
  "responsibilities": [
    "AI image generation (ComfyUI, SDXL)",
    "AI video/animations for Crownless Fortune",
    "Pixel art assets for video game",
    "Batch render execution",
    "Asset export to crew relay queue",
    "Vault write on STEALTHATTACK station only"
  ],
  "discord_token_env": "DISCORD_SIR_AZURE_TOKEN",
  "status": "planned",
  "opsec_note": "family hardware, minor operator, sandboxed to art/render tasks"
}
```

---

## Hermes Agent Setup

### Environment Variables
```bash
export DOCKER_HOST="tcp://192.168.0.39:2375"
export HERMES_NAME="SIR_AZURE"
export HERMES_INSTANCE="stealthattack"
export DISCORD_SIR_AZURE_TOKEN="your-token-here"
```

### Start Script
```bash
# Start Discord bot
python discord_crew_bot.py --crew sir_azure

# Start relay watcher
python relay_watcher.py --crew sir_azure --queue relay_queue.jsonl --poll 5
```

---

## Render Pipeline

### ComfyUI Workflow
1. Receive prompt from Sir Green/Sir Violet
2. Load SDXL model
3. Generate image with Azure blue theme
4. Save to output folder
5. Export to crew relay queue
6. Post completion to Discord #sir-azure

### Batch Render Execution
```bash
# Example batch command
python batch_render.py \
  --prompts prompts.txt \
  --output ./output \
  --model SDXL \
  --steps 30 \
  --cfg 7.5
```

---

## Vault Access

### Read Access (All Crew)
- `Z:\Developer_Brain\09_Cosmos_Library\` — cosmos library
- `Z:\Developer_Brain\03_AI_Operating_System\` — AI system
- `Z:\Developer_Brain\Shared_With_Pink\` — comms bridge

### Write Access (STEALTHATTACK Only)
- `Z:\Developer_Brain\03_AI_Operating_System\Brain_Azure\` — personal brain
- `Z:\Developer_Brain\09_Cosmos_Library\01_Astrology\Crew\RENDER_STEELWAKE_ASTRO_PROFILE.md` — own profile

---

## Integration Points

### With Sir Green
- Receives render tasks via Discord #sir-azure
- Reports batch progress in GPU/thermal terms
- Exports assets to relay queue for Sir Green

### With Sir Violet
- Receives art direction/lore requirements
- Confirms scope before rendering
- Delivers finished frames to art pipeline

### With Miss Pink
- Receives Torus Coffee product image requests
- Delivers processed/upscaled product photos
- Updates inventory_master.json with image status

---

## Activation Sequence

1. [ ] Hardware spec check (GPU, RAM, PSU, MB)
2. [ ] Docker Desktop installed
3. [ ] ComfyUI + SDXL models loaded
4. [ ] Tailscale authenticated
5. [ ] Discord bot created and token saved
6. [ ] crew_map.json updated with Discord user ID
7. [ ] chat_lines.json updated with Sir Azure phrases
8. [ ] Hermes agent configured
9. [ ] Discord bot tested
10. [ ] Render pipeline tested
11. [ ] Vault access verified
12. [ ] Relay queue tested

---

## Status

- ✅ Astro profile complete
- ✅ Discord bot design complete
- ✅ Build template created
- ⏳ Awaiting hardware check + Discord app creation

---

## Next Steps

1. **Captain/Sir Green:** Verify STEALTHATTACK hardware specs
2. **Sir Azure:** Create Discord application + bot
3. **Sir Azure:** Test ComfyUI + SDXL pipeline
4. **Miss Pink:** Request product photo batch renders
5. **All crew:** Verify relay queue communication
