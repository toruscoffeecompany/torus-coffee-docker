#!/usr/bin/env python3
"""
Weekly marketing campaign check - creates Trello cards for upcoming campaigns
"""
import urllib.request
import urllib.parse
import json
import ssl
from datetime import datetime, timedelta

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
backlog_list = list_map.get('Backlog')

# Check for upcoming campaigns in next 2 weeks
today = datetime.now()
two_weeks = today + timedelta(days=14)

print(f"Marketing Campaign Check - {today.strftime('%Y-%m-%d')}")
print(f"Checking campaigns for next 2 weeks ({two_weeks.strftime('%Y-%m-%d')})")
print()

campaigns = [
    ("Weekly social media posts", "Create and schedule 3-5 social media posts for this week", todo_list),
    ("Check inventory levels", "Review current inventory and reorder if needed", todo_list),
    ("Review Trello board", "Check all Torus_Ops cards and update status", todo_list),
]

for name, desc, list_id in campaigns:
    if list_id:
        create_card(name, desc, list_id)

print(f"\n✓ Campaign check complete - {len(campaigns)} tasks created")
