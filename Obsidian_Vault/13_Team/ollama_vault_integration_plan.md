# Ollama Vault Integration Plan

**Date:** 2026-08-08  
**Owner:** Miss Pink (with Sir Green coordination)  
**Status:** 🟡 In Progress  

---

## 1. Current State

| Component | Status | Notes |
|-----------|--------|-------|
| Ollama installed on PINKCADY | ✅ Yes | `C:\Users\torus\AppData\Local\Programs\Ollama\ollama.exe` |
| Ollama models downloaded | 🔴 None | `ollama list` returns empty |
| Ollama service running | 🔴 Not running | `ollama ps` shows empty |
| Obsidian Ollama plugin | 🔴 Not installed | 16 community plugins active, none Ollama-specific |
| Network access (Tailscale) | ✅ 4 nodes | pinkcady, squidstation, stealthattack, squidstation-docker-desktop |
| Docker/K8s on SQUIDSTATION | ✅ Running | 37h uptime, k8s cluster active |

## 2. Target Architecture
```
                    ┌─────────────────────────────────┐
                    │         SQUIDSTATION             │
                    │    (K8s cluster 100.83.247.14)   │
                    │                                  │
                    │  ┌──────────┐  ┌─────────────┐  │
                    │  │  Ollama   │  │ Model Cache │  │
                    │  │  Service  │  │ (shared vol)│  │
                    │  │ :11434    │  │             │  │
                    │  └────┬──────┘  └──────┬──────┘  │
                    │       │                │        │
                    └───────┼────────────────┼────────┘
                            │                │
       Tailscale mesh ─ ─ ─ ┼ ─ ─ ─ ─ ─ ─ ─ ─┼ ─ ─ ─ ─ ─ ─ ─ ─ ─ ─
                            │                │
              ┌─────────────┼─┐          ┌────┼────────────┐
              │ PINKCADY    │ │          │ STEALTHATTACK  │
              │ 100.106.235.│ │          │ 100.110.238.68 │
              │ Obsidian    │ │          │ Obsidian       │
              │ Ollama pl.  │ │          │ Ollama pl.     │
              │ localhost:  │ │          │ localhost:    │
              │ 11434 →     │ │          │ 11434 →       │
              │ Tailscale   │ │          │ Tailscale     │
              └─────────────┘ │          └────────────────┘
```

## 3. Implementation Steps

### Phase 1: Local PINKCADY Setup (P1 card)
1. Install "Obsidian Ollama" community plugin
2. Configure API endpoint: `http://localhost:11434`
3. Pull models: `llama3.2:3b`, `nomic-embed-text`, `mxbai-embed-large`
4. Test chat + embedding functionality
5. Document in vault

### Phase 2: SQUIDSTATION K8s Deployment (P2 card)
1. Create `ollama-deployment.yaml` with GPU support
2. Deploy via k8s: `kubectl apply -f ollama-deployment.yaml`
3. Expose service on Tailscale IP: `100.83.247.14:11434`
4. Configure persistent volume for model cache

### Phase 3: Fleet-Wide Configuration (P2 card)
1. Test API access from PINKCADY: `curl http://100.83.247.14:11434/api/tags`
2. Test from STEALTHATTACK: same endpoint
3. Configure Obsidian Ollama plugin on each node to point to `http://100.83.247.14:11434`
4. Create `ollama_client_config.json` in vault for all nodes

## 4. Discord Bot Deployment (P1 card)
See: "Deploy Discord crew bots" Trello card
- Requires manual approval from Sir Green for app creation

## 5. Verification
- `ollama list` returns models on all nodes
- Obsidian Ollama plugin responds to prompts
- Tailscale connectivity verified between all nodes
- Discord bots respond in guild `1527500149365018774`

---
*Created by: Miss Pink OODA cycle 2026-08-08*
