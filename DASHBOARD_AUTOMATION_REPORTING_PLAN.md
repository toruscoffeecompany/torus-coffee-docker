# DASHBOARD AUTOMATION REPORTING PLAN

## Goal
Feed dashboard status from local automations without editing Sir Green's dashboard_server.py.

## Approach
- Write local `dashboard_automation_status.json` from Miss Pink's automations.
- Let Sir Green add optional ingestion into dashboard_server.py if he wants.
- Use existing watchers/scripts to update the local JSON.

## Watchers to report
- pinkcady_crew_heartbeat.py -> heartbeat OK
- verifier_daemon.py -> verification result
- ooda_loop.py -> counts/status
- backfill_inboxes.py -> processed count
- pinkcady_comms_watcher.py -> comms state
- pinkcady_rig_reporter.py -> report success/failure

## Trello/GitHub
- Card 524: dashboard automation reporting
- Card 525: process Sir Azure backlog
- Card 526: fix CrowdSec 404
- Card 527: fix TorusPOS 404
- Card 528: investigate empty Suricata alert
