#!/usr/bin/env python3
"""
Miss Pink OODA — Fix VOID transfer + clean crew queues on Torus Ops board.

ROOT CAUSE: card_cleanup_ooda.py used wrong VOID board ID (6a7437aa41...)
instead of correct (6a595669b8f8...). Cards piled onto Torus board crew queues:
Sir Green's Queue (2925), Sir Azure's Queue (1158).

FIX:
1. Transfer ALL remaining crew-queue cards to correct VOID Ops board lists
2. Archive duplicates + stale + inbox cards on BOTH boards
3. Run cleanup on VOID Ops crew queues too
"""
import sys, os, requests, time, json
from datetime import datetime, timezone, timedelta
from collections import defaultdict

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from credential_loader import load_trello_credentials

creds = load_trello_credentials()
key, token = creds['api_key'], creds['token']

TORUS_BOARD = '6a70a3157d0db4214ac3f9a3'
VOID_BOARD = '6a595669b8f8f99c93392f4f'  # CORRECT VOID board ID

# Get lists for both boards
r = requests.get(f'https://api.trello.com/1/boards/{TORUS_BOARD}/lists',
    params={'key': key, 'token': token, 'fields': 'name,id'}, timeout=20)
torus_lists = {l['name']: l for l in r.json()}

r = requests.get(f'https://api.trello.com/1/boards/{VOID_BOARD}/lists',
    params={'key': key, 'token': token, 'fields': 'name,id'}, timeout=20)
void_lists = {l['name']: l for l in r.json()}

# Torus crew queue list IDs
torus_sir_green = torus_lists.get("Sir Green's Queue", {}).get('id')
torus_sir_azure = torus_lists.get("Sir Azure's Queue", {}).get('id')
torus_inbox = torus_lists.get("Miss Pink's Inbox", {}).get('id')

# VOID crew queue list IDs (targets for transfer)
void_sir_green = void_lists.get("Sir Green's Queue", {}).get('id')
void_sir_azure = void_lists.get("Sir Azure's Queue", {}).get('id')
void_miss_pink = void_lists.get("Miss Pink's Queue", {}).get('id')
void_done = void_lists.get("Done", {}).get('id')

# Get all open cards from Torus board
r = requests.get(f'https://api.trello.com/1/boards/{TORUS_BOARD}/cards',
    params={'key': key, 'token': token,
            'fields': 'name,id,idList,desc,dateLastActivity,closed'},
    timeout=120)
torus_open = [c for c in r.json() if not c.get('closed', False)]

# Get all open cards from VOID board
r = requests.get(f'https://api.trello.com/1/boards/{VOID_BOARD}/cards',
    params={'key': key, 'token': token,
            'fields': 'name,id,idList,desc,dateLastActivity,closed'},
    timeout=120)
void_open = [c for c in r.json() if not c.get('closed', False)]

print(f"Torus open: {len(torus_open)}")
print(f"VOID open: {len(void_open)}")

# Step 1: Transfer crew queue cards from Torus -> VOID board
transferred = 0
for c in torus_open:
    lid = c.get('idList')
    name = c.get('name', '')

    # Determine target list on VOID board based on card content
    target = None
    if 'sir_green' in name.lower() or 'Sir Green' in name:
        target = void_sir_green
    elif 'sir_azure' in name.lower() or 'Sir Azure' in name:
        target = void_sir_azure
    elif 'miss_pink' in name.lower():
        target = void_miss_pink
    elif lid == torus_sir_green:
        target = void_sir_green
    elif lid == torus_sir_azure:
        target = void_sir_azure
    elif lid == torus_inbox:
        # Inbox messages → archive on VOID board after transfer
        target = void_miss_pink

    if target:
        try:
            r = requests.put(f'https://api.trello.com/1/cards/{c["id"]}',
                params={'key': key, 'token': token,
                        'idList': target, 'idBoard': VOID_BOARD},
                timeout=15)
            if r.status_code == 200:
                transferred += 1
            else:
                print(f"  TRANSFER FAILED {c['id'][:8]}: {r.status_code}")
            time.sleep(0.1)
        except Exception as e:
            print(f"  ERROR {c['id'][:8]}: {e}")

print(f"\nStep 1 - Transferred to VOID board: {transferred}")

# Step 2: Archive remaining stale/duplicate/inbox cards on Torus board
# Get fresh count
r = requests.get(f'https://api.trello.com/1/boards/{TORUS_BOARD}/cards',
    params={'key': key, 'token': token,
            'fields': 'name,id,idList,desc,dateLastActivity,closed'},
    timeout=120)
torus_cards = [c for c in r.json() if not c.get('closed', False)]

# Find duplicates
name_counts = defaultdict(list)
for c in torus_cards:
    name_counts[c.get("name", "")].append(c)
dup_ids = set()
for name, dups in name_counts.items():
    if len(dups) > 1:
        for dup in dups[1:]:
            dup_ids.add(dup["id"])

now = datetime.now(timezone.utc)
to_archive = []
for c in torus_cards:
    name = c.get("name", "")
    desc = c.get("desc", "")

    # Skip Top 10, P0, P1
    lid = c.get("idList")
    if lid in (torus_lists["Top 10 — Focus Fleet"]["id"],
               torus_lists["P0 - Alert / Critical / Do Now"]["id"],
               torus_lists["P1 - High / Doing Now"]["id"]):
        continue

    # Duplicates
    if c["id"] in dup_ids:
        to_archive.append(c)
        continue

    # Inbox
    if "[INBOX]" in name:
        to_archive.append(c)
        continue

    # OODA processed + old
    last = c.get("dateLastActivity", "")
    try:
        act = datetime.fromisoformat(last.replace("Z", "+00:00"))
        if "OODA" in desc and (now - act) > timedelta(days=3):
            to_archive.append(c)
            continue
    except:
        pass

    # VERIFIED_DONE
    if "VERIFIED_DONE" in desc:
        to_archive.append(c)
        continue

print(f"\nStep 2 - Cards to archive on Torus board: {len(to_archive)}")

archived = 0
for c in to_archive:
    try:
        r = requests.put(f'https://api.trello.com/1/cards/{c["id"]}',
            params={'key': key, 'token': token, 'closed': 'true'}, timeout=8)
        if r.status_code == 200:
            archived += 1
        time.sleep(0.05)
    except:
        pass

print(f"Step 2 - Archived: {archived}/{len(to_archive)}")

# Step 3: Archive on VOID board — crew queues, done, P5, P4
r = requests.get(f'https://api.trello.com/1/boards/{VOID_BOARD}/cards',
    params={'key': key, 'token': token,
            'fields': 'name,id,idList,desc,dateLastActivity,closed'},
    timeout=120)
void_cards = [c for c in r.json() if not c.get('closed', False)]

# Archive criteria for VOID board:
# - Done list (after transfer)
# - P5 / P4 old cards
# - Duplicates
# - VERIFIED_DONE
void_dup_ids = set()
vn_counts = defaultdict(list)
for c in void_cards:
    vn_counts[c.get("name", "")].append(c)
for name, dups in vn_counts.items():
    if len(dups) > 1:
        for dup in dups[1:]:
            void_dup_ids.add(dup["id"])

void_to_archive = []
for c in void_cards:
    name = c.get("name", "")
    desc = c.get("desc", "")
    lid = c.get("idList")

    # Done list
    if lid == void_done:
        void_to_archive.append(c)
        continue

    # P5 / P4
    p5_id = void_lists.get("P5 - Very Low / Blocked / Postponed", {}).get('id')
    p4_id = void_lists.get("P4 - Low / Waiting", {}).get('id')
    if lid in (p5_id, p4_id):
        void_to_archive.append(c)
        continue

    # Duplicates
    if c["id"] in void_dup_ids:
        void_to_archive.append(c)
        continue

    # VERIFIED_DONE
    if "VERIFIED_DONE" in desc:
        void_to_archive.append(c)
        continue

    # Sir Green/Azure queue — archive after transfer (these are crew work items)
    sg_id = void_lists.get("Sir Green's Queue", {}).get('id')
    sa_id = void_lists.get("Sir Azure's Queue", {}).get('id')
    if lid in (sg_id, sa_id):
        # Archive crew queue cards — crew should re-promote what's still needed
        void_to_archive.append(c)
        continue

    # Inbox = 0 on VOID board already

print(f"\nStep 3 - Cards to archive on VOID board: {len(void_to_archive)}")

void_archived = 0
for c in void_to_archive:
    try:
        r = requests.put(f'https://api.trello.com/1/cards/{c["id"]}',
            params={'key': key, 'token': token, 'closed': 'true'}, timeout=8)
        if r.status_code == 200:
            void_archived += 1
        time.sleep(0.05)
    except:
        pass

print(f"Step 3 - Archived on VOID board: {void_archived}/{len(void_to_archive)}")

# Final counts
r = requests.get(f'https://api.trello.com/1/boards/{TORUS_BOARD}/cards',
    params={'key': key, 'token': token, 'fields': 'name,id,closed'},
    timeout=60)
torus_final = sum(1 for c in r.json() if not c.get('closed', False))

r = requests.get(f'https://api.trello.com/1/boards/{VOID_BOARD}/cards',
    params={'key': key, 'token': token, 'fields': 'name,id,closed'},
    timeout=60)
void_final = sum(1 for c in r.json() if not c.get('closed', False))

print(f"\n=== FINAL ===")
print(f"Torus Ops open: {torus_final}")
print(f"VOID Ops open: {void_final}")
print(f"Total: {torus_final + void_final}")
