from pathlib import Path
from datetime import datetime, timezone, timedelta
import sys
sys.path.insert(0, '10_Skills_Library/05_Operations/scripts')
from calendar_sync import _fetch_trello_cards, _is_relevant_trello, _is_due_near_term, _build_schedule

lists, cards = _fetch_trello_cards()
lists_by_id = {l['id']: l for l in lists}
relevant = [c for c in cards if _is_relevant_trello(c, lists_by_id) and _is_due_near_term(c)]
print('relevant', len(relevant))

tickets = []
for c in relevant[:20]:
    tickets.append({
        'source': 'trello',
        'id': c['id'],
        'summary': c.get('name',''),
        'due': c.get('due'),
        'priority': 5,
        'minutes': 60,
    })
print('tickets', len(tickets))
for t in tickets:
    print(t['summary'], t['due'])

placements = _build_schedule(tickets)
print('placements', len(placements))
for p in placements:
    print(p['date'], p['start'].isoformat(), p['end'].isoformat(), p['item']['summary'])
