# HIGH_PRIORITY_TASKLIST_20260806
Generated: 2026-08-06T15:40:00.000000+00:00
Sources: Trello deep dive (539 cards), GitHub deep dive (100 issues), verifier flags, dashboard checks

## P1 — Execute Now

### Dashboard (Sir Green)
- [ ] Add /api/fleet route to dashboard_server.py
- [ ] Add /api/tools route to dashboard_server.py
- [ ] Add /api/security-docs route to dashboard_server.py
- [ ] Add /api/hw route to dashboard_server.py
- [ ] Add /api/rig-report route to dashboard_server.py
- [ ] Fix /api/status timeout on large payload
- [ ] Investigate dashboard 502 regression root cause

### Security (Sir Azure)
- [ ] Install nikto on PINKCADY
- [ ] Install tshark on PINKCADY
- [ ] Install yara on PINKCADY

### Trello/GitHub Sync
- [x] Trello auth verified as toruscoffeecompany
- [x] Full board audit: 539 cards, 14 labels, 6 lists
- [x] 0 unlabeled cards, 0 duplicates
- [x] 75 P1 cards commented with progress
- [x] 7 P1 blocker cards created in Torus_Ops Backlog
- [x] GitHub issues updated with progress (11 issues)
- [ ] Sir Green share VOID Ops Trello board metadata
- [ ] Sir Green share Trello Butler automation metadata

### Local Vault
- [x] Rebuild D:\Work\Torus_Ops_bare.git healthy bare mirror
- [x] Expand .gitignore for runtime artifacts
- [x] Vault audit complete: 232 .md files, 139 broken wiki-links, 7 duplicates
- [ ] Resolve 139 broken wiki-links (mostly in node_modules/website artifacts)
- [ ] Resolve 7 duplicate file groups
- [ ] Commit local vault changes

### Automation
- [x] OODA loop operational: 1min cycle
- [x] Backfill inboxes operational
- [x] Continuous tasklist: 350 tasks, 15min cycle
- [x] Verifier daemon: 5min cycle
- [x] Heartbeat reporter: posting to dashboard
- [x] Self-healing loop: 30s timeout

## P2 — This Week

- [ ] Draw automation architecture diagram for crew
- [ ] Automate recurring vault audit + plugin drift detection
- [ ] Sir Azure share Obsidian vault plugin config
- [ ] Sir Green share VOID Ops dashboard plugin/add-on list
- [ ] Fix Templater + Periodic Notes template paths
- [ ] Investigate Suricata alert: empty message
- [ ] Multi-stage Dockerfiles for Python services
- [ ] Verify all Windows Task Scheduler jobs point to real scripts

## P3 — Backlog

- [ ] Review/design brand assets
- [ ] Document templates/guides
- [ ] Strategy planning
- [ ] Self-learning/self-correcting automation wrapper

## Trello P1 Cards (82 total)
Top actionable P1 cards:
1. [P1] Sir Green: add /api/fleet route to dashboard_server.py
2. [P1] Sir Green: add /api/tools route to dashboard_server.py
3. [P1] Sir Green: add /api/security-docs route to dashboard_server.py
4. [P1] Sir Green: add /api/hw route to dashboard_server.py
5. [P1] Sir Green: add /api/rig-report route to dashboard_server.py
6. [P1] Sir Azure: install nikto tshark yara on PINKCADY
7. [P1] Miss Pink: commit orders.json and automation_status changes
8. [P1] torus-alert-router: implement Discord/Gmail/Obsidian integrations
9. [P1] torus-inventory: deploy fixed FastAPI image on SQUIDSTATION
10. [P1] torus-website: build Next.js + Dockerfile + push image

## GitHub P1 Issues (95 total)
Top actionable P1 issues:
1. #196 Dashboard improvements for Sir Green's local network monitor
2. #195 Full Obsidian vault deep-dive audit + organization improvements
3. #194 Audit and reconcile D:\Work\Torus_Ops_bare.git with vault/GitHub
4. #182 Diagnose PINKCADY -> SQUIDSTATION dashboard connectivity
5. #181 Fix Trello API auth for toruscoffeecompany — invalid key 401
6. #189 FOLLOW-UP: Sir Green Trello Butler automation metadata request sent
7. #188 FOLLOW-UP: Sir Green exact dashboard test commands sent
8. #211-#214 Inbox messages from Miss Pink to Sir Green/Sir Azure

## Crew Asks

### Sir Green
1. Add missing dashboard routes: /api/fleet, /api/tools, /api/security-docs, /api/hw, /api/rig-report
2. Resolve /api/status timeout
3. Share VOID Ops Trello board metadata + Butler automation metadata
4. Dashboard regression reported and tracked in #214

### Sir Azure
1. Install nikto, tshark, yara on PINKCADY
2. Share Obsidian vault plugin config
3. Confirm Docker overlay preference
