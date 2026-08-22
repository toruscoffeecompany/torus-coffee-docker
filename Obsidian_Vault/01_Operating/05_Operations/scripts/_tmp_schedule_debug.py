from pathlib import Path
from datetime import datetime, timezone, timedelta
import sys
sys.path.insert(0, '10_Skills_Library/05_Operations/scripts')
from calendar_sync import _fetch_trello_cards, _is_relevant_trello, _is_due_near_term, _fetch_github_issues, _build_schedule

lists, cards = _fetch_trello_cards()
lists_by_id = {l['id']: l for l in lists}
relevant = [c for c in cards if _is_relevant_trello(c, lists_by_id) and _is_due_near_term(c)]
print('relevant trello', len(relevant))
for c in relevant[:5]:
    print('card', c.get('name'), c.get('due'))

issues = _fetch_github_issues()
print('github issues', len(issues))

# build fake ticket list
tickets = []
for c in relevant[:10]:
    tickets.append({
        'source': 'trello',
        'id': c['id'],
        'summary': c.get('name',''),
        'due': c.get('due'),
        'priority': 5,
        'minutes': 60,
    })
placements = _build_schedule(tickets)
print('placements', len(placements))
for p in placements[:5]:
    print(p['date'], p['start'].isoformat(), p['end'].isoformat(), p['item']['summary'])
