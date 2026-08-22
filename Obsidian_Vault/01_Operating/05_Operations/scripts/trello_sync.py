#!/usr/bin/env python3
"""Sync Trello board status to markdown files in vault."""
import urllib.request
import urllib.parse
import json
import ssl
import os
from pathlib import Path

from credential_loader import load_trello_credentials

CREDENTIALS = load_trello_credentials()
API_KEY = CREDENTIALS["api_key"]
TOKEN = CREDENTIALS["token"]
ctx = ssl.create_default_context()

def api(method, url, data=None):
    req = urllib.request.Request(url, method=method)
    req.add_header('Accept', 'application/json')
    if data:
        req.add_header('Content-Type', 'application/x-www-form-urlencoded')
        req.data = data.encode()
    with urllib.request.urlopen(req, context=ctx, timeout=15) as r:
        return json.loads(r.read())

def sync_board(board_name, board_id, output_path):
    """Sync Trello board to markdown file."""
    lists = api("GET", f"https://api.trello.com/1/boards/{board_id}/lists?key={API_KEY}&token={TOKEN}&fields=name,id")
    cards = api("GET", f"https://api.trello.com/1/boards/{board_id}/cards?key={API_KEY}&token={TOKEN}&fields=name,idList,desc,dateLastActivity")
    
    list_map = {l['id']: l['name'] for l in lists}
    md = f"# {board_name} — Trello Board\n\n"
    md += f"**Last synced:** {Path(output_path).stat().st_mtime if Path(output_path).exists() else 'Never'}\n\n"
    md += f"**Total cards:** {len(cards)}\n\n"
    
    for list_name in ['Backlog', 'To_Do', 'In_Progress', 'Review', 'Done']:
        list_cards = [c for c in cards if list_map.get(c['idList']) == list_name]
        md += f"## {list_name} ({len(list_cards)})\n\n"
        for card in sorted(list_cards, key=lambda x: x.get('dateLast_activity', ''), reverse=True):
            md += f"- [ ] {card['name']}\n"
        md += "\n"
    
    Path(output_path).parent.mkdir(parents=True, exist_ok=True)
    Path(output_path).write_text(md)
    print(f"✓ Synced {board_name}: {len(cards)} cards")

def main():
    # ─── CORRECTED PATHS — vault, not root ───────────────────────────────────────
    vault = r"D:\Work\Torus Coffee Company LLC\Obsidian_Vault"
    trello_out = os.path.join(vault, "09_Projects", "Trello_Boards")
    
    boards = {
        "Torus_Ops": ("Torus Ops", "6a70a3157d0db4214ac3f9a3", os.path.join(trello_out, "Torus_Ops.md")),
        "VOID_Ops": ("VOID Ops", "6a595669b8f8f99c93392f4f", os.path.join(trello_out, "VOID_Ops.md")),
        "Business_Docs": ("Business Docs", "6a70a3152b3a1f6dca3fa08c", os.path.join(trello_out, "Business_Docs.md")),
        "Website_Rebuild": ("Website Rebuild", "6a70a316f884c39f2dc5e6a6", os.path.join(trello_out, "Website_Rebuild.md")),
    }
    
    for name, (display_name, board_id, output_path) in boards.items():
        try:
            sync_board(display_name, board_id, output_path)
        except Exception as e:
            print(f"✗ Failed to sync {name}: {e}")

if __name__ == "__main__":
    main()
