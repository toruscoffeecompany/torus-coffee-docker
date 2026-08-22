# 10 — GitHub Clone Setup (Miss Pink)

**Status:** ✅ Complete

## What We Did
1. Installed GitHub CLI (`gh` v2.96.0) via winget
2. Configured git identity: `misspink@toruscoffeecompany.com` / `Miss Pink`
3. Created `toruscoffeecompany/Torus_Ops` repo
4. Created `toruscoffeecompany/Torus_website_rebuild` repo
5. Pushed initial vault content to `Torus_Ops` (commit `a866019`)
6. Pushed website scaffold to `Torus_website_rebuild` (commit `97cd3f3`)

## Repos
| Repo | URL | Purpose |
|------|-----|---------|
| Torus_Ops | https://github.com/toruscoffeecompany/Torus_Ops | Business docs, vault backup |
| Torus_website_rebuild | https://github.com/toruscoffeecompany/Torus_website_rebuild | Website code |

## Authentication
- Method: HTTPS + PAT (git CLI)
- Note: PAT exposed in old commit `070e90e` — rotated to new token
- All pushes use git CLI to avoid REST API rate limits

## Sync Schedule
- Daily 8:30 AM via Task Scheduler: `Torus_Vault_Sync_To_GitHub`
- Script: `10_Skills_Library/05_Operations/scripts/vault_sync_to_github.py`

## Rules
- One-way push only from local vault
- Never pull from GitHub as source
- 2025 tax docs excluded from sync
