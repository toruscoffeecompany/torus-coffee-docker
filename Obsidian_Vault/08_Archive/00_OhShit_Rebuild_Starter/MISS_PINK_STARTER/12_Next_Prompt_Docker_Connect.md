# 12 — Docker Connect (Miss Pink)

**Status:** ⏸️ Waiting on Sir Green

## Current State
- SQUIDSTATION ping: ✅ 1-4ms, 0% loss
- Z: drive: ✅ Mounted read-only
- Docker API on 2375: ❌ Unreachable
- Docker API on 2376: ❌ Unreachable
- Port 9999: ❌ Unreachable

## What Miss Pink Needs From Sir Green
1. Enable Docker remote API on SQUIDSTATION (port 2375 or 2376)
2. Start service on port 9999
3. Confirm `CONNECTION_VERIFICATION.md` location

## What Miss Pink Has Done
- Created `D:\Work\Archive\backups\SQUIDSTATION_vault` for backups
- Scheduled daily 3AM robocopy backup Task Scheduler job
- Verified Z: drive read-only access to SQUIDSTATION vault

## When Sir Green Enables Docker
1. Test connection: `curl http://192.168.0.39:2375/_ping`
2. List containers: `curl http://192.168.0.39:2375/containers/json`
3. Verify port 9999: `curl http://192.168.0.39:9999/verify`
4. Run `setup_pink_docker.py` if available

## Note
PINKCADY does NOT run Docker locally. All Docker operations are remote to SQUIDSTATION.
