#!/usr/bin/env python3
"""Trello deep dive audit and labeling for Torus Coffee Company."""
import urllib.request, json, ssl, time, re

from credential_loader import load_trello_credentials

CREDENTIALS = load_trello_credentials()
API_KEY = CREDENTIALS["api_key"]
TOKEN = CREDENTIALS["token"]
ctx = ssl.create_default_context()

BOARDS = {
    "Torus_Ops": "6a70a3157d0db4214ac3f9a3",
    "Business_Docs": "6a70a3152b3a1f6dca3fa08c",
    "Website_Rebuild": "6a70a316f884c39f2dc5e6a6",
}

LABEL_MAP = {
    "Torus_Ops": {
        "P1": "6a70acc569135c796d8eba5d",
        "P2": "6a70acc56f143597877f576e",
        "P3": "6a70acc6fddcac79f411267f",
    },
    "Business_Docs": {
        "P1": "6a70acc52d2b702243dca15c",
        "P2": "6a70acc61ae452c4542b5e51",
        "P3": "6a70acc65b8e3ad52e674812",
    },
    "Website_Rebuild": {
        "P1": "6a70acc568dc8165d0228ae3",
        "P2": "6a70acc6f9e5cc3562930ed9",
        "P3": "6a70acc76261415e68aec958",
    },
}

# Priority classification rules
def classify_card(name, board):
    name_lower = name.lower()
    
    # Skip list headers and test cards
    if name in ['Blocked', 'In Progress', 'Done', 'Automation Alert', 'Test Card']:
        return None
    
    # P1: Critical blockers, deployment, Docker, production issues
    if any(kw in name_lower for kw in [
        'docker', 'deploy', 'squidstation', 'torus-inventory', 
        'blocked', 'critical', 'production', 'revenue', 'payment',
        'square', 'oauth', 'server', 'ssl', 'dns', 'hosting'
    ]):
        return "P1"
    
    # P2: High priority integrations, website, automations
    if any(kw in name_lower for kw in [
        'website', 'buffer', 'zapier', 'hubspot', 'trello',
        'automation', 'script', 'api', 'integration', 'test',
        'social media', 'facebook', 'instagram', 'meta',
        'next.js', 'tailwind', 'build', 'contact form',
        'vendor', 'application', 'sop', 'inventory', 'sync'
    ]):
        return "P2"
    
    # P3: Documentation, research, templates, setup
    if any(kw in name_lower for kw in [
        'create', 'setup', 'install', 'configure', 'template',
        'guide', 'document', 'research', 'draft', 'design',
        'artwork', 'graphic', 'photo', 'image', 'campaign',
        'calendar', 'strategy', 'analytics', 'seo', 'profile',
        'account', 'page', 'channel', 'publish', 'content',
        'email signature', 'banner', 'barcode', 'gtin',
        'compliance', 'legal', 'privacy', 'terms'
    ]):
        return "P3"
    
    # Default P2 for unclassified task cards
    return "P2"

def api_get(path):
    url = f"https://api.trello.com/1{path}?key={API_KEY}&token={TOKEN}"
    with urllib.request.urlopen(url, context=ctx, timeout=15) as r:
        return json.loads(r.read())

def api_put(path, data):
    url = f"https://api.trello.com/1{path}?key={API_KEY}&token={TOKEN}"
    req = urllib.request.Request(url, data=json.dumps(data).encode(), method="PUT")
    req.add_header('Content-Type', 'application/json')
    with urllib.request.urlopen(req, context=ctx, timeout=15) as r:
        return json.loads(r.read())

print("=== TRELLO DEEP DIVE AUDIT & LABELING ===\n")

stats = {
    "P1": 0,
    "P2": 0,
    "P3": 0,
    "skipped": 0,
    "already_labeled": 0,
    "updated": 0,
    "errors": 0,
}

for board_name, board_id in BOARDS.items():
    print(f"--- {board_name} ---")
    lists = api_get(f"/boards/{board_id}/lists")
    
    for lst in lists:
        cards = api_get(f"/lists/{lst['id']}/cards")
        for card in cards:
            name = card['name']
            card_id = card['id']
            labels = card.get('labels', [])
            label_ids = [l['id'] for l in labels]
            
            priority = classify_card(name, board_name)
            if priority is None:
                stats["skipped"] += 1
                continue
            
            # Check if already has a priority label
            existing = any(lid in LABEL_MAP[board_name].values() for lid in label_ids)
            if existing:
                stats["already_labeled"] += 1
                continue
            
            # Apply label
            label_id = LABEL_MAP[board_name][priority]
            try:
                api_put(f"/cards/{card_id}", {"idLabels": label_id})
                print(f"  [{priority}] {name}")
                stats[priority] += 1
                stats["updated"] += 1
                time.sleep(0.1)
            except Exception as e:
                print(f"  [ERROR] {name}: {e}")
                stats["errors"] += 1
    
    print()
    time.sleep(0.5)

print("=== AUDIT SUMMARY ===")
print(f"P1 assigned: {stats['P1']}")
print(f"P2 assigned: {stats['P2']}")
print(f"P3 assigned: {stats['P3']}")
print(f"Skipped (list headers): {stats['skipped']}")
print(f"Already labeled: {stats['already_labeled']}")
print(f"Updated: {stats['updated']}")
print(f"Errors: {stats['errors']}")
