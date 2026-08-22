# HIGH PRIORITY TASKS — 2026-08-06
Generated: 2026-08-06T08:30:00.000000+00:00
Source: Trello boards + GitHub issues + vault audit findings

## P1 — DO TODAY
1. **Rotate Trello API key+token** — all automation blocked until done
2. **Fix dashboard_server.py bind** — confirm 0.0.0.0, firewall, port 81 path
3. **Verify 9090/9100 port regression** — Prometheus/Alertmanager returning 404
4. **Cleanup D:\Work\Torus_Ops_bare.git** — broken bare mirror needs disposition
5. **Apply vault broken-link fixes** — 139 broken wiki-links identified

## P2 — THIS WEEK
6. **Mirror Sir Green’s Trello Butler automation** — request sent, awaiting response
7. **Standardize Obsidian configs across crew** — Sir Azure/Sir Green configs needed
8. **Deploy recommended dashboard tools** — Netdata, Uptime Kuma, Loki, Portainer
9. **Create unified backlog sync** — merge 3 Trello boards into 1 view
10. **Add Docker volume backup automation** — torus-backup image exists, not scheduled

## P3 — NEXT WEEK
11. **Implement alert-router webhook fallback** — Discord/Gmail/Slack routing
12. **Deploy K8s demo workloads to SQUIDSTATION** — namespace torus ready
13. **Create Excalidraw diagrams for all systems** — fleet, network, automation flow
14. **Set up Trello Top 10 automation** — blocked by P1
15. **Review and merge duplicate Trello board files** — Backlog.md, Done.md, etc.

## GitHub Issue Mapping
- #155-#164: board audit, Obsidian deep-dive, recurring automation
- #171-#176: Top 10 automation, dashboard/Trello follow-ups
- #181: Trello API 401 auth blocker
- #182: PINKCADY→SQUIDSTATION dashboard connectivity
- #185-#186: Obsidian improvements + Excalidraw diagram
- #188-#189: exact test commands + Butler request
- #194-#200: vault audit, bare git, dashboard recommendations

## Trello Card Counts
- Torus_Ops: Backlog 7, To_Do 7, In_Progress 6, Review 5, Done 4
- Business_Docs: Backlog 3, To_Do 1, In_Progress 2, Review 2, Done 1
- Website_Rebuild: Backlog 1, To_Do 1, In_Progress 0, Review 0, Done 0
- Total: 40 cards across 3 boards

## Automation Status
- ooda_loop.py: OK (60s cycle)
- backfill_inboxes.py: OK
- board_audit.py: OK (retagged=15)
- trello_top10_sync.py: OK (blocked by Trello API)
- vault_audit.py: OK (broken=139, duplicates=6)
- self_healing_loop.py: OK
- verifier_daemon.py: OK (9 flags, mostly dashboard/security tools)
EOF