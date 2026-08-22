# TORUS OPS - Missing Card Creation Attempt (Blocked)
**Date**: 2026-08-17
**By**: Miss Pink (@miss-pink-bryon)

## Blocked: Trello API Token Invalid
The Trello API key/token combination returns 401 "invalid app token" for all API calls.
The token `ATTA5fa83...` (76 chars) is documented correctly in:
- `Obsidian_Vault/01_Operating/Operating Paperwork/Trello_API_Credentials.md`
- `Obsidian_Vault/02_Business_Operations/Communications/Discord/miss_pink_bot/scripts/trello_client.py`

**Action needed**: Captain needs to regenerate Trello token at https://trello.com/1/authorize

## Missing Cards Identified (cannot create without valid token):

1. **P0: Docker Desktop 4.88 — WSL2 backend fix + TCP 2375/2376**
   - Status: FIXED. Docker Desktop 4.88 working with WSL2.
   - All 10 containers rebuilt from source (toruscoffee/*:20260817-v4)
   - TCP 2375/2376 NOT exposed (Docker Desktop 4.88 limitation — npipe only)
   
2. **P1: Fix Docker credential helper PATH issue + persist**
   - Fixed via setx user PATH + clean config.json (no credsStore)
   - docker-credential-desktop.exe at C:/Program Files/Docker/Docker/resources/bin/
   
3. **P1: Audit VOID_OPS Done cards (batches 3+)**
   - Batch 1: 5 verified ✅
   - Batch 2: 8 verified, 2 reopened 🔁
   - Continue with batch 3+
   
4. **P2: Verify Hermes profiles + skills intact after Docker rebuild**
   - Profile path: C:/Users/torus/AppData/Local/hermes/profiles/
   
5. **P2: Verify Docker data backup (182GB wsl_backup_20260817)**
   - Backup at C:/Users/torus/AppData/Local/Docker/wsl_backup_20260817/
   - All containers rebuilt from source, backup preserved
