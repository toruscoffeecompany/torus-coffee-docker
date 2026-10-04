# DASHBOARD CONNECTIONS PLAN
## Based on live dashboard state from SQUIDSTATION Chrome

### Current dashboard gaps
- Inboxes not wired to dashboard reporting
- FleetWatcher/SirGreenBot/AutomationWatcher not connected to dashboard API
- Suricata alerts empty
- CrowdSec returning 404
- TorusPOS returning 404
- No webhook/log/volume/Kubernetes metrics

### Work created
- Trello cards: 524-532
- GitHub issues: 94-102

### Next actions
1. Add dashboard reporting to ooda_loop.py and verifier_daemon.py
2. Fix CrowdSec and TorusPOS endpoints
3. Wire FleetWatcher/SirGreenBot/AutomationWatcher to dashboard
4. Add webhook/log/volume/Kubernetes metrics endpoints
5. Add alertmanager for Prometheus + Discord
