import requests
import os

TRELLO_KEY = os.environ.get('TRELLO_KEY') or 'TRELLO_KEY_REMOVED_SEE_CREDENTIAL_FILE'
TRELLO_TOKEN = os.environ.get('TRELLO_TOKEN') or 'TRELLO_TOKEN_REMOVED_SEE_CREDENTIAL_FILE'
BASE = 'https://api.trello.com/1/cards'
params = lambda: {'key': TRELLO_KEY, 'token': TRELLO_TOKEN}

cards = [
    ('6a74cbd440270147ff04bd5b', 'P0: Eliminate all cmd popup sources permanently', 'Audit all launchers, startup shortcuts, scheduled tasks, and remove visible cmd/python.exe wrappers.'),
    ('6a74cbd440270147ff04bd5b', 'P0: Fix Docker fleet healthchecks — remove curl/wget deps', 'Fix unhealthy containers: alert-router/inventory/pos/prometheus/cadvisor/node-exporter due to curl/wget missing in alpine/python:slim images.'),
    ('6a74cbd5e3d54d2d08be82e7', 'P1: Archive Excalidraw/Scripts/Downloaded/ (172 files)', 'Move duplicate Excalidraw scripts out of vault or archive; keep only active custom scripts.'),
    ('6a74cbd5e3d54d2d08be82e7', 'P1: Consolidate website_legacy_2026-08-04 and PROJECT WEBSITE R3DEPLOY', 'Archive legacy website folders, remove smart-env references, dedupe against next-storefront.'),
    ('6a74cbd5e3d54d2d08be82e7', 'P1: Fix 284 broken wiki links in vault', 'Scan and repair Obsidian broken links across all vault .md files.'),
    ('6a74cbd5e3d54d2d08be82e7', 'P1: Remove rogue OODA loops spawned from bash shells', 'Kill zombie python.exe chains from fleet_deployment_ooda_loop, discord_bot_build_ooda_loop, obsidian_integration_ooda_loop, miss_pink_continuous_ooda.'),
    ('6a74cbd4148f814483a64589', 'P2: Move website Dockerfiles out of vault or into proper /Docker folder', 'Relocate 06_Website/*/Dockerfile* to 10_Skills_Library/05_Operations/Docker/.'),
    ('6a74cbd4148f814483a64589', 'P2: Add Docker automation into master OODA loop', 'Integrate container health verification into continuous tasklist.'),
    ('6a74cbd4148f814483a64589', 'P2: Add vault audit + website dedupe into automated pipelines', 'Ensure VAULT_AUDIT_SNAPSHOT.json updates daily and legacy sites are pruned automatically.'),
    ('6a74cbd4148f814483a64589', 'P2: Clean up 06_Website duplicates and missing data folders', 'Standardize website source of truth; remove dead Design assets duplicates.'),
]

for list_id, name, desc in cards:
    try:
        r = requests.post(BASE, params={**params(), 'idList': list_id, 'name': name, 'desc': desc}, timeout=30)
        print(r.status_code, name)
    except Exception as e:
        print('ERROR', name, e)
