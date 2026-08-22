#!/usr/bin/env python3
"""
Generate Trello card for Sir Azure AI art asset request.
"""
import urllib.request
import urllib.parse
import json
import ssl
import sys

from credential_loader import load_trello_credentials

CREDENTIALS = load_trello_credentials()
API_KEY = CREDENTIALS["api_key"]
TOKEN = CREDENTIALS["token"]
BOARD_ID = "6a70a3157d0db4214ac3f9a3"
LIST_ID = "5f3e7b9c8b9e4b3d7c8b9e4b"  # To_Do list
ctx = ssl.create_default_context()

def create_card(name, desc, list_id=LIST_ID):
    url = f"https://api.trello.com/1/cards?key={API_KEY}&token={TOKEN}&name={urllib.parse.quote(name)}&desc={urllib.parse.quote(desc)}&idList={list_id}"
    req = urllib.request.Request(url, method="POST")
    with urllib.request.urlopen(req, context=ctx, timeout=15) as r:
        result = json.loads(r.read())
        print(f"Created card: {result['name']} ({result['id']})")
        return result

if __name__ == "__main__":
    name = sys.argv[1] if len(sys.argv) > 1 else "New Asset Request"
    desc = sys.argv[2] if len(sys.argv) > 2 else "Asset request for Sir Azure"
    create_card(name, desc)
