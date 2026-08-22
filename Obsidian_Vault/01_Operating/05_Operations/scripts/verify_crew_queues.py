#!/usr/bin/env python3
"""Verify crew queue lists are synced between Torus_Ops and VOID Ops."""
import json
import requests
from pathlib import Path
from datetime import datetime

SCRIPT_DIR = Path(__file__).resolve().parent
REPO_ROOT = SCRIPT_DIR.parent.parent.parent
CREDENTIALS_PATH = Path(r"D:/Work/Torus Coffee Company LLC/Obsidian_Vault/01_Operating/Operating Paperwork/Trello_API_Credentials.md")
TORUS_BOARD_ID = "6a70a3157d0db4214ac3f9a3"
VOID_BOARD_ID = "6a595669b8f8f99c93392f4f"
INDEX_PATH = REPO_ROOT / "10_Skills_Library/05_Operations/TRELLO_CARD_INDEX.json"

def get_trello_credentials():
    creds = CREDENTIALS_PATH.read_text(encoding="utf-8")
    key = next(line for line in creds.splitlines() if line.startswith("`d6ee")).strip("`")
    token = next(line for line in creds.splitlines() if line.startswith("`ATTA")).strip("`")
    return key, token

def verify_queues():
    key, token = get_trello_credentials()
    
    # Get both boards' lists
    torus_lists = requests.get(
        f"https://api.trello.com/1/boards/{TORUS_BOARD_ID}/lists",
        params={"key": key, "token": token, "fields": "id,name", "filter": "all"},
        timeout=10,
    ).json()
    
    void_lists = requests.get(
        f"https://api.trello.com/1/boards/{VOID_BOARD_ID}/lists",
        params={"key": key, "token": token, "fields": "id,name", "filter": "all"},
        timeout=10,
    ).json()
    
    torus_queue_names = {l['name'] for l in torus_lists if "Queue" in l['name']}
    void_queue_names = {l['name'] for l in void_lists if "Queue" in l['name']}
    
    results = {
        "timestamp": datetime.now().isoformat(),
        "torus_ops_queues": sorted(torus_queue_names),
        "void_ops_queues": sorted(void_queue_names),
        "queues_match": torus_queue_names == void_queue_names,
        "torus_azure_count": 0,
        "torus_green_count": 0,
        "void_azure_count": 0,
        "void_green_count": 0,
        "cross_board_duplicates": [],
        "missing_labels": [],
        "missing_descriptions": [],
    }
    
    # Check queue cards
    for board_name, board_id, lists in [("torus_ops", TORUS_BOARD_ID, torus_lists), ("void_ops", VOID_BOARD_ID, void_lists)]:
        azure_list = next((l for l in lists if l['name'] == "Sir Azure's Queue"), None)
        green_list = next((l for l in lists if l['name'] == "Sir Green's Queue"), None)
        
        if azure_list:
            cards = requests.get(
                f"https://api.trello.com/1/lists/{azure_list['id']}/cards",
                params={"key": key, "token": token, "fields": "id,name,labels,desc", "filter": "all"},
                timeout=10,
            ).json()
            results[f"{board_name}_azure_count"] = len(cards)
            
            for c in cards:
                labels = [l['name'] for l in c.get('labels', [])]
                if 'sir-azure' not in labels and 'Sir Azure' not in c.get('name', ''):
                    results['missing_labels'].append(f"{board_name}: {c['id']}")
                if not c.get('desc', '').strip():
                    results['missing_descriptions'].append(f"{board_name}: {c['id']}")
        
        if green_list:
            cards = requests.get(
                f"https://api.trello.com/1/lists/{green_list['id']}/cards",
                params={"key": key, "token": token, "fields": "id,name,labels,desc", "filter": "all"},
                timeout=10,
            ).json()
            results[f"{board_name}_green_count"] = len(cards)
            
            for c in cards:
                labels = [l['name'] for l in c.get('labels', [])]
                if 'sir-green' not in labels and 'Sir Green' not in c.get('name', ''):
                    results['missing_labels'].append(f"{board_name}: {c['id']}")
                if not c.get('desc', '').strip():
                    results['missing_descriptions'].append(f"{board_name}: {c['id']}")
    
    # Save verification results
    Path("10_Skills_Library/05_Operations/QUEUE_VERIFICATION.json").write_text(
        json.dumps(results, indent=2),
        encoding="utf-8"
    )
    
    print("=== QUEUE VERIFICATION ===")
    print(f"Torus_Ops queues: {results['torus_ops_queues']}")
    print(f"VOID Ops queues: {results['void_ops_queues']}")
    print(f"Queues match: {'✅' if results['queues_match'] else '❌'}")
    print(f"\nCard counts:")
    print(f"  Torus_Ops Sir Azure's Queue: {results['torus_azure_count']}")
    print(f"  Torus_Ops Sir Green's Queue: {results['torus_green_count']}")
    print(f"  VOID Ops Sir Azure's Queue: {results['void_azure_count']}")
    print(f"  VOID Ops Sir Green's Queue: {results['void_green_count']}")
    print(f"\nMissing labels: {len(results['missing_labels'])}")
    print(f"Missing descriptions: {len(results['missing_descriptions'])}")
    
    return results

if __name__ == "__main__":
    verify_queues()
