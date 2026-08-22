from pathlib import Path
import requests
from datetime import datetime, timezone

vault = Path('D:/Work/Torus Coffee Company LLC')
creds_file = vault / '01_Operating/Operating Paperwork/Trello_API_Credentials.md'
text = creds_file.read_text(encoding='utf-8')
api_key = None
token = None
lines = text.splitlines()
for i, line in enumerate(lines):
    if 'API Key' in line and i + 1 < len(lines):
        api_key = lines[i + 1].strip().strip('`')
    elif 'Token' in line and 'OAuth' not in line and i + 1 < len(lines):
        token = lines[i + 1].strip().strip('`')
if not api_key or not token:
    raise RuntimeError('Could not load Trello credentials')

boards = {
    'Torus_Ops': '6a70a3157d0db4214ac3f9a3',
    'Business_Docs': '6a70a3152b3a1f6dca3fa08c',
    'Website_Rebuild': '6a70a316f884c39f2dc5e6a6',
}
out = []
for name, bid in boards.items():
    r = requests.get(f'https://api.trello.com/1/boards/{bid}/cards', params={'key': api_key, 'token': token, 'fields': 'name,idList,labels,url'}, timeout=30)
    print(f'board={name} status={r.status_code}')
    r.raise_for_status()
    cards = r.json()
    r2 = requests.get(f'https://api.trello.com/1/boards/{bid}/lists', params={'key': api_key, 'token': token, 'fields': 'name'}, timeout=30)
    print(f'lists status={r2.status_code}')
    r2.raise_for_status()
    lists = r2.json()
    list_map = {l['id']: l['name'] for l in lists}
    out.append(f'## {name}')
    out.append(f'cards={len(cards)} lists={len(lists)}')
    out.append('```')
    for card in cards[:25]:
        labels = ','.join(l['name'] for l in card.get('labels', []))
        out.append(f"{card['name']} | {list_map.get(card.get('idList'), '?')} | {labels} | {card.get('url', '')}")
    out.append('```')
print('\n'.join(out))
