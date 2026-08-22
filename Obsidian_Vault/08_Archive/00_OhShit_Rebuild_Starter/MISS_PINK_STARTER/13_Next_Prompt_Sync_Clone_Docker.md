# 13 — Sync Fleet Clone + Docker Connect

**Status:** ⏸️ Waiting on Sir Green + Captain decision

## Current State
- No fleet clone yet (awaiting Captain decision on method)
- Docker remote not yet accessible
- Z: drive read-only confirmed

## What We Have
- `D:\Work\Archive\backups\SQUIDSTATION_vault` — backup folder ready
- Daily 3AM robocopy job scheduled
- Z: drive mounted to `\\192.168.0.39\Obsidian_Vault` (read-only)

## What We Need
1. **Captain decision:** Fleet clone method (fresh / sync / leave-as-is)
2. **Sir Green action:** Enable Docker remote API on 2375/2376
3. **Sir Green action:** Start port 9999 service
4. **Sir Green action:** Confirm `CONNECTION_VERIFICATION.md` location

## When Ready
1. Clone fleet repo into local lane (pull-only guard)
2. Connect to SQUIDSTATION Docker daemon
3. Verify void-fleet network
4. Deploy Torus helper containers only (Captain approval required)

## Note
PINKCADY has no Hyper-V, no Docker Desktop. All Docker is remote to SQUIDSTATION.
