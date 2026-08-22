# Torus Coffee Alert Definitions

**Owner:** Miss Pink  
**Created:** 2026-08-09  
**Related:** GitHub Issue #16 — Actionable alerts/services from dashboard

---

## Alert Categories

### 1. Hardware Alerts (P0)
| Alert | Check | Threshold | Action |
|-------|-------|-----------|--------|
| High CPU | `top` / `wmic cpu get loadpercentage` | >80% for 5m | Log + Discord alert |
| High Memory | `free -m` / `wmic OS get FreePhysicalMemory` | >90% usage | Log + Discord alert |
| Low Disk | `df -h` / `wmic logicaldisk where "DeviceID='C:'" get FreeSpace` | <10% free | Log + Discord alert |
| High Temperature | `wmic /namespace:\\root\wmi PATH MSAcpi_ThermalZoneTemperature` | >80°C | Log + Discord alert |

### 2. Fleet Alerts (P1)
| Alert | Check | Threshold | Action |
|-------|-------|-----------|--------|
| Tailscale Offline | `tailscale status` | Node not "active" | Log + Discord alert |
| Docker Container Down | `docker ps` | Expected container not running | Auto-restart + alert |
| Docker Healthcheck Failed | `docker ps --filter health=unhealthy` | Any unhealthy | Log + alert |
| K8s Pod Crash | `kubectl get pods -n torus` | CrashLoopBackOff | Log + alert |
| Ollama API Down | `curl http://localhost:11434/api/tags` | Returns non-200 | Restart service + alert |

### 3. Security Alerts (P0)
| Alert | Check | Threshold | Action |
|-------|-------|-----------|--------|
| File Mutation | `git diff --quiet` on critical files | Any change detected | Auto-restore + log |
| Unauthorized Access | Windows Event Log | Failed login >3 in 1hr | Log + Discord alert |
| Credential Exposure | `git secrets` scan | Pattern match | Block commit + alert |
| Firewall Breach | Windows Firewall logs | Blocked traffic spike | Log + alert |

### 4. Crew Heartbeat Alerts (P1)
| Alert | Check | Threshold | Action |
|-------|-------|-----------|--------|
| Miss Pink Heartbeat | `Crew/.heartbeat_pinkcady.json` timestamp | >10min stale | Log + alert |
| Sir Green Heartbeat | `Crew/.heartbeat_squidstation.json` | >10min stale | Log (Sir Green monitors) |
| Sir Azure Heartbeat | `Crew/.heartbeat_stealthattack.json` | >10min stale | Log (Sir Azure monitors) |
| Automation Daemon Down | `tasklist /FI "IMAGENAME eq pythonw.exe"` | No pythonw running | Auto-restart + alert |

### 5. OodA / Smart Ticket Alerts (P1)
| Alert | Check | Threshold | Action |
|-------|-------|-----------|--------|
| Trello API Error | Response status code | 401/429/5xx | Retry + alert |
| GitHub API Error | Response status code | 403/401 | Alert (may need token rotation) |
| Card Stale | Card age + no comment progress | >48h no activity | Promote + alert |
| Cooldown Stuck | Smart ticket cycle | Same card >5 cycles | Force advance + alert |

### 6. Website/Revenue Alerts (P0)
| Alert | Check | Threshold | Action |
|-------|-------|-----------|--------|
| Payment API Down | `curl https://square.link/u/...` | HTTP 5xx | Alert (revenue impact) |
| Website Offline | `curl -f http://pinkcady:3000/health` | HTTP 5xx | Auto-restart + Discord alert |
| Orders Stuck | `orders.json` status=processing | >24h | Alert + manual review |
| Inventory Sync Fail | `inventory_to_website_sync.py` | Exit code != 0 | Log + alert |

---

## Alert Routing
- **P0**: Discord → #crew-alerts → also email if available
- **P1**: Discord → #ops-notifications
- **P2**: Log only (daily report aggregation)
- **P3**: Log only (weekly review)

## Alert Definition Format (JSON)
```json
{
  "name": "hardware_cpu_high",
  "category": "hardware",
  "priority": "P0",
  "check_command": "wmic cpu get loadpercentage",
  "threshold": ">80",
  "timeout": "5m",
  "actions": ["log", "discord_alert"],
  "cooldown": "30m",
  "owner": "miss-pink"
}
```

## Implementation
Alert definitions are consumed by:
- `automation_logger.py` — checks thresholds every cycle
- `miss_pink_self_heal.py` — self-healing triggers
- `pinkcady_crew_heartbeat.py` — crew heartbeat monitor
- `check_scheduled_tasks.py` — Windows task scheduler audit
