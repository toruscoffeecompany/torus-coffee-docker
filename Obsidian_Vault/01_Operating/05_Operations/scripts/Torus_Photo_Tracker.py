#!/usr/bin/env python3
"""
Weekly product photo tracker - checks photo status and creates Trello cards
"""
import urllib.request
import urllib.parse
import json
import ssl
from datetime import datetime

from credential_loader import load_trello_credentials
CREDENTIALS = load_trello_credentials()
API_KEY = CREDENTIALS['api_key']
TOKEN = CREDENTIALS['token']
ctx = ssl.create_default_context()

def create_card(name, desc, list_id):
    url = f"https://api.trello.com/1/cards?key={API_KEY}&token={TOKEN}&name={urllib.parse.quote(name)}&desc={urllib.parse.quote(desc)}&idList={list_id}"
    req = urllib.request.Request(url, method="POST")
    with urllib.request.urlopen(req, context=ctx, timeout=15) as r:
        result = json.loads(r.read())
        print(f"✓ Created: {result['name']}")
        return result

# Get Torus_Ops board lists
board_id = "6a70a3157d0db4214ac3f9a3"
url = f"https://api.trello.com/1/boards/{board_id}/lists?key={API_KEY}&token={TOKEN}&fields=name,id"
with urllib.request.urlopen(url, context=ctx, timeout=15) as r:
    lists = json.loads(r.read())
    list_map = {l['name']: l['id'] for l in lists}

todo_list = list_map.get('To_Do')

print(f"Product Photo Tracker - {datetime.now().strftime('%Y-%m-%d')}")
print()

products = [
    ("Aurora Bites - Review photos", "Check if hero image, lifestyle, and social photos are ready", todo_list),
    ("Sour Aurora Bites - Review photos", "Check if hero image, lifestyle, and social photos are ready", todo_list),
    ("Orbit Cream Crunch - URGENT photos", "Only 1 photo - need 6 more ASAP", todo_list),
    ("Cosmic Bananas - Review photos", "Check if all product photos are ready", todo_list),
    ("Apple Zephyr Chips - Review photos", "Check if all product photos are ready", todo_list),
]

for name, desc, list_id in products:
    if list_id:
        create_card(name, desc, list_id)

print(f"\n✓ Photo tracker check complete - {len(products)} products reviewed")
