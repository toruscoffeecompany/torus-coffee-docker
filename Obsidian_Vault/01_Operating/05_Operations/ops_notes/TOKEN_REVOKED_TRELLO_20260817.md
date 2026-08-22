# 🔴 CRITICAL: Trello API Token Revoked — Action Required

**Date**: 2026-08-17  
**Status**: BLOCKED — All Trello API calls failing with 401/400 "invalid app token"  
**Owner**: Captain Bryon Smith (Miss Pink)

---

## What Happened

The Trello API token **`ATTA5fa83ac8abb79f4f0431b2753c87cb04fe898aa700ff84d1f1c1648f180034d2dC1621D9C`** (76 chars) was **valid and working** until approximately 2026-08-17T16:30 UTC. It was used to:

- ✅ Post 5 verification comments on TORUS_OPS Done cards (Batch 1)
- ✅ Post 10 verification comments + 2 card moves on VOID_OPS Done cards (Batch 2)

Sometime between Batch 2 verification and now, the token was **revoked/revoked at Trello's end**. The API now returns:
- `400 Bad Request: invalid token` when querying the token directly
- `401 Unauthorized: invalid app token` for all board/card operations

## What Was NOT Done

- ❌ No Trello cards can be read, created, or updated
- ❌ 5 missing TORUS_OPS cards could not be created
- ❌ VOID_OPS Done card verification cannot continue (Batch 3+)
- ❌ No alternative tokens or API keys were found anywhere in the vault

## How to Fix (Captain Action Required)

1. Visit: `https://trello.com/1/authorize?response_type=token&key=TRELLO_KEY_REMOVED_SEE_CREDENTIAL_FILE&scope=read,write,account&expiration=never&name=Torus+Coffee+Ops&power-up-user=me`
2. Click "Allow" to re-authorize
3. Copy the new token (starts with `ATTA`)
4. Paste it into: `Obsidian_Vault/01_Operating/Operating Paperwork/Trello_API_Credentials.md`
5. Let Miss Pink know the new token

## Boards Affected

| Board | Name | ID | Status |
|-------|------|-----|--------|
| VOID_OPS | Void Pirate Trading Co Ops | `6a595669...` | ❌ Token revoked |
| TORUS_OPS | Torus Coffee Ops | `6a70a315...` | ❌ Token revoked |
| Sir Azure | Uses TORUS_OPS board | — | ❌ Same token |

## Alternative: Manual Card Management

Until the token is restored:
- ✅ Docker containers: verified via direct HTTP/socket checks
- ✅ Dashboard endpoints: verified via curl
- ✅ Container health: verified via `docker ps` + `docker logs`
- ❌ Trello card comments/moves: blocked — need manual CAPTAiN intervention
- ❌ New card creation: blocked — document in Obsidian instead

## Workaround Cards Created in Obsidian

All card content that would have been created on Trello is documented here:

1. `ops_notes/trello_tokens_revoked_20260817.md` — Full audit of missing cards
2. This file — Token revocation notice

## Impact on Crew Coordination

- Sir Green's OODA loop: Cannot sync Trello to TORUS_OPS/SQUIDSTATION
- Sir Azure's queue mapping: Cannot process `sir-azure` labeled cards
- Discord bot: `trello_client.py` has hardcoded backup token — will fail same way
- Crew comms: Card comments for verification status cannot be posted
