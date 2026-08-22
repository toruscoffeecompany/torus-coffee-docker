from pathlib import Path
from datetime import datetime, timezone, timedelta
import sys
sys.path.insert(0, '10_Skills_Library/05_Operations/scripts')
from calendar_sync import _fetch_trello_cards, _is_relevant_trello, _is_due_near_term

lists, cards = _fetch_trello_cards()
lists_by_id = {l['id']: l for l in lists}
relevant = [c for c in cards if _is_relevant_trello(c, lists_by_id)]
print('relevant all', len(relevant))
near = [c for c in relevant if _is_due_near_term(c)]
print('relevant near-term', len(near))
for c in near[:10]:
    print(c.get('name'), c.get('due'))
print('...')
for c in relevant[10:20]:
    print(c.get('name'), c.get('due'))
