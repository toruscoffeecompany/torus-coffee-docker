# Tools/Security Tabs for Unified Dashboard on 8089

Add two new tabs to the unified dashboard:
- `/tools`: local inventory of installed tools, versions, and health
- `/security`: security findings from nikto/tshark/yara/suricata

Implementation notes:
- Frontend: reuse existing dashboard layout
- Backend: expose endpoints `GET /api/tools` and `GET /api/security-docs`
- Data source: `10_Skills_Library/05_Operations/Security/*`

Blockers:
- Requires Sir Green to add `/api/tools`, `/api/security-docs`, `/api/hw`, `/api/rig-report` routes
- Requires Sir Azure to populate security scan artifacts
