# OODA_TASKLIST_20260806
Generated: 2026-08-06T15:29:00.000000+00:00
Sources: Trello P1 cards, GitHub high-priority issues, verifier flags, vault audit, dashboard checks

## P1 — Do Now

### Dashboard Verification
- [x] Verify /healthz reachable from PINKCADY -> 200
- [x] Verify /api/crew_heartbeat reachable -> 200
- [ ] Verify /api/status returns valid JSON without timeout
- [ ] Verify /api/fleet, /api/tools, /api/security-docs, /api/hw, /api/rig-report return 200

### Dashboard Endpoints Missing (Sir Green)
- [ ] Sir Green add /api/fleet route to dashboard_server.py
- [ ] Sir Green add /api/tools route to dashboard_server.py
- [ ] Sir Green add /api/security-docs route to dashboard_server.py
- [ ] Sir Green add /api/hw route to dashboard_server.py
- [ ] Sir Green add /api/rig-report route to dashboard_server.py
- [ ] Sir Green resolve /api/status timeout on large payload

### Security Tools (Sir Azure)
- [ ] Sir Azure install nikto on PINKCADY
- [ ] Sir Azure install tshark on PINKCADY
- [ ] Sir Azure install yara on PINKCADY

### Trello/GitHub Sync
- [x] Verify Trello auth as toruscoffeecompany
- [x] Full board audit: 538 cards, 14 labels, 6 lists
- [x] Label unlabeled cards: 0 unlabeled
- [x] Comment 75 P1 cards with progress
- [x] Create 7 P1 cards for blockers in Torus_Ops Backlog
- [x] Update Trello cards with current progress
- [x] Update GitHub issues #181, #194, #195, #196, #182, #189, #188, #211-#214
- [ ] Sir Green share VOID Ops Trello board metadata for mirroring
- [ ] Sir Green share Trello Butler automation metadata

### Local Vault
- [x] Rebuild D:\Work\Torus_Ops_bare.git healthy bare mirror
- [x] Expand .gitignore for runtime artifacts
- [x] Vault audit complete: 232 .md files, 139 broken wiki-links, 7 duplicates
- [ ] Commit 00_Inbox/01_Daily/2026-08-06.md
- [ ] Commit 04_Products/orders.json
- [ ] Commit 10_Skills_Library/05_Operations/automation_status.json
- [ ] Resolve 139 broken wiki-links in vault
- [ ] Resolve 7 duplicate file groups in vault

### GitHub
- [x] Issues #194-#200 created for tracking
- [x] Update issue bodies with progress notes
- [ ] Close resolved issues: #181 Trello auth, #194 bare git audit
- [ ] Close resolved issues: #189 Butler request, #188 test commands

## P2 — This Week

- [ ] Draw automation architecture diagram for crew
- [ ] Automate recurring vault audit + plugin drift detection
- [ ] Sir Azure share Obsidian vault plugin config
- [ ] Sir Green share VOID Ops dashboard plugin/add-on list
- [ ] Fix Templater + Periodic Notes template paths
- [ ] Investigate Suricata alert: empty message
- [ ] Multi-stage Dockerfiles for Python services
- [ ] Scan vault for broken wikilinks and duplicate names

## P3 — Backlog

- [ ] Review/design brand assets
- [ ] Document templates/guides
- [ ] Strategy planning

## Crew Asks

### Sir Green
1. Add missing dashboard routes: /api/fleet, /api/tools, /api/security-docs, /api/hw, /api/rig-report
2. Resolve /api/status timeout
3. Share VOID Ops Trello board metadata + Butler automation metadata
4. Dashboard regression reported: all routes returned 502, now partially restored.

### Sir Azure
1. Install nikto, tshark, yara on PINKCADY
2. Share Obsidian vault plugin config
3. Confirm Docker overlay preference
