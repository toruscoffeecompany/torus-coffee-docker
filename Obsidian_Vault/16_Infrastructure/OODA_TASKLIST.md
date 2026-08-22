# OODA Tasklist — Full System Audit Checklist

## OODA Cycle 1: Security Audit (Every 5 minutes)
1. **Scan for exposed secrets**
   - Run `TOOL_AG_OPSEC_SECURITY_AUDIT.py` against vault root `D:\Work\Torus Coffee Company LLC`
   - Check `00_Inbox/` for `.env`, `.pem`, `.key` files
   - Scan `10_Skills_Library/` for hardcoded API keys/tokens
   - Report any findings to P1-P0 Trello card

2. **Verify card duplication prevention**
   - Check `smart_ticket_cycle.py` has `recently_promoted` cooldown active
   - Verify `inbox_alert_processor.py` has `find_card_by_name()` dedup
   - Count open cards on Torus Ops board — alert if >150
   - Clear any duplicates in Sir Green's Queue / Sir Azure's Queue

3. **Verify Docker daemon healthy**
   - `curl -s http://localhost:2375/version` → expect HTTP 200
   - `docker ps` → expect 10 containers running (torus-light stack)
   - Check for OOMKill (code 137) containers → if found, add mem_limit

## OODA Cycle 2: Trello Sync (Every 5 minutes)
4. **Sync VOID Ops → Torus Ops for Miss Pink**
   - Read `Miss Pink's Queue` list on VOID Ops board (`6a595669b8f8f99c93392f4f`)
   - Transfer unique cards (by name) to Torus Ops board (`6a70a3157d0db4214ac3f9a3`)
   - **NEVER sync Sir Green's Queue or Sir Azure's Queue** — those are exclusive
   - Use crew coordination lock: `trello_sync` claim before writing

5. **Process Miss Pink's Inbox (Torus Ops)**
   - Read `Miss Pink's Inbox` list on Torus Ops
   - For each card: claim `msg:{id}` lock, process directive, post comment, move to Done
   - Use crew coordination to avoid duplicate processing

6. **Card hygiene**
   - Verify all P0/P1/P2 cards have current due dates
   - Verify all P1/P2/P3 cards have priority labels
   - Post status comments on stale cards (>24h no update)

## OODA Cycle 3: Git + Vault (Every 10 minutes)
7. **Git hygiene**
   - `git status` → check for stray 2GB blobs or `nul` files
   - `git gc --prune=now` → clean stale refs
   - Commit any unsynced vault changes
   - Push to origin/main

8. **Vault health**
   - Verify `00_Vault_Home.md` exists and is current
   - Check `00_Inbox/` for unprocessed messages
   - Verify shared comms path: `Z:\Developer_Brain\Shared_With_Pink\Shared_With_Pink`
   - Verify local outbox: `02_Business_Operations/Communications/Outbox/`

## OODA Cycle 4: Process + Disk Health (Every 5 minutes)
9. **Process health**
   - Verify `pythonw.exe` processes are running (OODA workers)
   - Check for stuck processes (>2h runtime, 0 activity)
   - Verify scheduled tasks are enabled: `Torus_Continuous_OODA`, `Torus_Smart_Ticket_Cycle`

10. **Disk space**
    - PINKCADY C: drive: alert if <10% free
    - Docker root (`/var/lib/docker`): alert if >80% used
    - Vault directory: check for `nul` files (Windows special file)
    - Clean temp files if needed

## OODA Cycle 5: Fleet Mesh (Every 5 minutes)
11. **Fleet connectivity**
    - Verify Docker daemon on PINKCADY: `curl http://localhost:2375/version`
    - Check SQUIDSTATION: `docker -H tcp://192.168.0.39:2375 version`
    - Alert if either rig offline
    - Do NOT check STEALTHATTACK (Sir Azure's exclusive domain)

12. **Container health**
    - `docker ps` on PINKCADY → expect 10 containers (torus-light stack)
    - Verify all health checks passing
    - Auto-restart failed containers

---

## Execution Order
1. Cycle 1 (Security) — claim `security_scan` lock
2. Cycle 2 (Trello) — claim `trello_sync` lock
3. Cycle 3 (Git) — claim `git_auto` lock
4. Cycle 4 (Process) — no lock needed
5. Cycle 5 (Fleet) — no lock needed

Each cycle claims its lock via `crew_coordination.py`, executes, then releases.
If lock is held by another crew member, skip that cycle and continue.

## Emergency Break Conditions
- If Torus Ops board >150 open cards: STOP ALL SYNC, run `ultra_fast_archiver_v10.py`
- If PINKCADY disk <5%: alert P0, kill non-critical containers
- If Docker daemon down: alert P0, attempt restart, escalate to Captain
