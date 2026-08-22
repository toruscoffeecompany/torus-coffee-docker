# Suricata Alert Investigation: Empty Message

Observed:
- Suricata alert fired with empty message payload

Investigation steps:
1. Review `/var/log/suricata/eve.json` for surrounding events
2. Check rule ID and signature
3. Correlate with dashboard/Prometheus alerts
4. If benign, add suppression rule
5. If real, escalate to Sir Green/Sir Azure

Current finding:
- Likely benign or instrumentation artifact; no immediate action required.
