#!/usr/bin/env python3
"""Finalized Trello automation with Top 10 enforcement, priority sort, label, index, and cross-board duplicate check."""
import json
import time
import requests
from pathlib import Path
from datetime import datetime, timedelta
from collections import defaultdict

SCRIPT_DIR = Path(__file__).resolve().parent
REPO_ROOT = SCRIPT_DIR.parent.parent.parent
CREDENTIALS_PATH = REPO_ROOT / "01_Operating/Operating Paperwork/Trello_API_Credentials.md"
TORUS_BOARD_ID = "6a70a3157d0db4214ac3f9a3"
VOID_BOARD_ID = "6a595669b8f8f99c93392f4f"
INDEX_PATH = REPO_ROOT / "10_Skills_Library/05_Operations/TRELLO_CARD_INDEX.json"

# List ID mappings
# Primary bucket IDs used for card placement
LIST_IDS = {
    'P0': '6a74cbd440270147ff04bd5b',
    'Top 10': '6a74cbd3aa052ed2b30c5644',
    'P1': '6a74cbd5e3d54d2d08be82e7',
    'P2': '6a74cbd4148f814483a64589',
    'P3': '6a70a32923622d3e00107d70',
    'P4': '6a74cbd573259cffe8a23cc0',
    'P5': '6a70a3282e405a2460afc170',
    'P6': '6a74cbd67bbe3ef35a634495',
    'Future Ideas': '6a74cbd56a538340582a8897',
    "Sir Azure's Queue": '6a74cbd51b2662f6cdc37cce',
    "Sir Green's Queue": '6a74cbd679972be49ea46dae',
    'To Do': '6a74cbd4b333e64566823e06',
    'Follow-up': '6a74cbd6274d0c132843b049',
    'Done': '6a70a32a723c0312a3d5fbb4',
}

# Exact board list names returned by Trello API
LIST_NAMES = {
    '6a74cbd440270147ff04bd5b': 'P0 - Alert / Critical / Do Now',
    '6a74cbd3aa052ed2b30c5644': 'Top 10 — Focus Fleet',
    '6a74cbd4b333e64566823e06': 'To Do',
    '6a74cbd5e3d54d2d08be82e7': 'P1 - High / Doing Now',
    '6a74cbd4148f814483a64589': 'P2 - Med High / This Week',
    '6a70a32923622d3e00107d70': 'P3 - Medium / Follow Up',
    '6a74cbd573259cffe8a23cc0': 'P4 - Medium Low / Backlog',
    '6a70a3282e405a2460afc170': 'P5 - Low / Review',
    '6a74cbd67bbe3ef35a634495': 'P6 - Very Low / Blocked / Waiting',
    '6a74cbd56a538340582a8897': "Torus Coffee's Future Ideas",
    '6a74cbd51b2662f6cdc37cce': "Sir Azure's Queue",
    '6a74cbd679972be49ea46dae': "Sir Green's Queue",
    '6a74cbd6274d0c132843b049': 'Follow-up',
    '6a70a32a723c0312a3d5fbb4': 'Done',
}

# Priority graduation hierarchy: P6 -> P5 -> P4 -> P3 -> P2 -> P1 -> P0
# Cards graduate up when completed or when dependencies resolve
PRIORITY_GRADUATION = {
    'P6': 'P5',
    'P5': 'P4',
    'P4': 'P3',
    'P3': 'P2',
    'P2': 'P1',
    'P1': 'P0',
    'P0': 'Done',
    'Top 10': 'Top 10',  # Top 10 stays until explicitly moved
    'Future Ideas': 'Future Ideas',
    "Sir Azure's Queue": "Sir Azure's Queue",
    "Sir Green's Queue": "Sir Green's Queue",
}

# Due date policy by priority (days from now)
DUE_DATE_POLICY = {
    'P0': 1,        # Due tomorrow - critical
    'Top 10': 2,    # Due in 2 days - highest priority
    'P1': 3,        # Due in 3 days - high priority
    'P2': 7,        # Due in 1 week
    'P3': 14,       # Due in 2 weeks
    'P4': 30,       # Due in 1 month
    'P5': 60,       # Due in 2 months
    'P6': 90,       # Due in 3 months
    'Future Ideas': 180,  # Due in 6 months
    "Sir Azure's Queue": 14,
    "Sir Green's Queue": 14,
}

# Follow-up date policy (days from now)
FOLLOWUP_POLICY = {
    'P0': 0,        # Follow up today
    'Top 10': 1,    # Follow up tomorrow
    'P1': 2,        # Follow up in 2 days
    'P2': 5,        # Follow up in 5 days
    'P3': 10,       # Follow up in 10 days
    'P4': 21,       # Follow up in 3 weeks
    'P5': 42,       # Follow up in 6 weeks
    'P6': 60,       # Follow up in 2 months
    'Future Ideas': 90,
    "Sir Azure's Queue": 7,
    "Sir Green's Queue": 7,
}

# Checklist templates by card type
CHECKLIST_TEMPLATES = {
    'Top 10': [
        'Define success metrics',
        'Identify dependencies',
        'Create timeline',
        'Assign owner',
        'Verify completion',
    ],
    'P0': [
        'Assess impact',
        'Identify root cause',
        'Implement fix',
        'Verify resolution',
        'Update documentation',
    ],
    'P1': [
        'Create task breakdown',
        'Set deadline',
        'Begin implementation',
        'Test changes',
        'Review and deploy',
    ],
    'P2': [
        'Plan approach',
        'Execute work',
        'Test functionality',
        'Document changes',
        'Review with team',
    ],
    'P3': [
        'Research requirements',
        'Draft content/solution',
        'Get feedback',
        'Implement revisions',
        'Publish/Deploy',
    ],
    'P4': [
        'Assess feasibility',
        'Plan implementation',
        'Execute when capacity allows',
    ],
    'P5': [
        'Gather information',
        'Present options',
        'Get approval',
        'Proceed or defer',
    ],
    'P6': [
        'Monitor external dependency',
        'Re-evaluate when unblocked',
    ],
    'Future Ideas': [
        'Research feasibility',
        'Cost-benefit analysis',
        'Create proposal',
        'Get approval',
        'Schedule for future',
    ],
}

# Member assignments based on queue
MEMBER_ASSIGNMENTS = {
    "Sir Azure's Queue": "sir-azure",
    "Sir Green's Queue": "sir-green",
    'P0': 'miss-pink',
    'Top 10': 'miss-pink',
    'P1': 'miss-pink',
}

# Top 10 enforcement: exactly 10 cards max
TOP_10_MAX = 10

def get_trello_credentials():
    creds = CREDENTIALS_PATH.read_text(encoding="utf-8")
    key = next(line for line in creds.splitlines() if line.startswith("`d6ee")).strip("`")
    token = next(line for line in creds.splitlines() if line.startswith("`ATTA")).strip("`")
    return key, token

def load_index():
    if INDEX_PATH.exists():
        try:
            return json.loads(INDEX_PATH.read_text(encoding="utf-8"))
        except (json.JSONDecodeError, OSError):
            backup = INDEX_PATH.with_suffix('.json.bak')
            try:
                INDEX_PATH.replace(backup)
            except OSError:
                pass
            return {"cards": [], "last_checked": None}
    return {"cards": [], "last_checked": None}

def save_index(index):
    data = json.dumps(index, indent=2)
    INDEX_PATH.write_text(data, encoding="utf-8")

def classify_card(card):
    """Classify card into priority bucket with 24/7 execution model."""
    name = card.get('name', '').lower()
    labels = [l['name'].lower() for l in card.get('labels', [])]
    desc = card.get('desc', '').lower() if card.get('desc') else ''
    
    # P0: True production blockers only - system down, security breach, revenue stopped
    p0_signals = [
        '🚨', 'alert', 'blocked', '403', '502', 'critical', 'emergency',
        'security', 'breach', 'down', 'outage', 'production down',
        'revenue stopped', 'payment failure', 'data loss',
        'dashboard 502', 'dashboard down', 'website down', 'pos down',
        'inventory down', 'square payment failure', 'sqausre payments down'
    ]
    if any(k in name for k in p0_signals):
        return 'P0'
    
    # Top 10: ONLY items directly generating revenue this week or actively blocking revenue
    # Max 10 items - absolute most critical
    top10_signals = [
        'freeze-dried production', 'square developer', 'payments live',
        'pos deployment', 'inventory deployment', 'website launch',
        'production sop', 'revenue stream plan', 'first sale',
        'confirm pat works', 'github auth for toruscoffeecompany repos',
        'first dollar', 'first paid', 'launch payment', 'go live',
        'torus-inventory deployment blocked', 'launch freeze-dried'
    ]
    if any(k in name for k in top10_signals):
        return 'Top 10'
    if 'top 10' in labels:
        return 'Top 10'
    
    # P1: Immediate blockers, must-do this week, actively blocking revenue
    # Broader but still selective for Torus Coffee ops blockers
    p1_signals = [
        'critical', 'urgent', 'emergency', 'blocker', 'p0', 'alert', 'do now',
        'dashboard 502', 'dashboard down', 'website down', 'website offline',
        'auth broken', 'github connection broken', 'data loss',
        'docker build failed', 'docker push failed', 'docker down',
        'production down', 'revenue stopped', 'payment failure', 'pos down',
        'inventory down', 'square payment failure', 'sqausre payments down',
        'squidstation', 'void pirate github blocked'
    ]
    if any(k in name for k in p1_signals):
        return 'P1'
    if any(k in name for k in ['launch', 'deploy', 'go live', 'production', 'revenue', 'first sale', 'first dollar']) and any(k in name for k in ['now', 'asap', 'today', 'immediate', 'this week']):
        return 'P1'
    if any(k in name for k in ['blocker', 'broken', 'failed', 'offline', 'down']) and any(k in name for k in ['dashboard', 'docker', 'github', 'trello', 'automation']):
        return 'P1'
    
    # Crew queues must come AFTER P0/P1/Top 10 so true blockers don't get swallowed
    crew_queue_keywords = {
        "Sir Azure's Queue": [
            'sir azure', 'sirazure', 'security tools', 'stealthattack',
            'pinkcady security', 'windows spy', 'autohotkey', 'ahkv2',
            'nikto', 'tshark', 'yara', 'comfyui', 'minio', 'postgres', 'nginx'
        ],
        "Sir Green's Queue": [
            'sir green', 'sirgreen', 'fleet', 'swarm', 'compose',
            'api route', 'missing route', 'dashboard_server',
            'prometheus', 'grafana', 'redis secured', 'docker hub'
        ]
    }
    
    for queue, keywords in crew_queue_keywords.items():
        if any(k in name for k in keywords) or any(k in desc for k in keywords):
            return queue
    
    # P2: Med High / This Week - important but not blocking, planned work
    # Only explicit active project/work items that are CURRENTLY being worked on
    p2_signals = [
        'implement discord', 'integrate buffer', 'connect zapier',
        'deploy torus-pos', 'deploy torus-inventory', 'deploy torus-website',
        'deploy dashboard', 'fix dashboard', 'fix docker',
        'setup square', 'square payments', 'pos live', 'inventory live',
        'website launch', 'launch payment', 'go live',
        'production sop', 'freeze-dried production',
        'first sale', 'first dollar', 'revenue stream'
    ]
    if any(k in name for k in p2_signals):
        return 'P2'
    
    # P2 context: active project work with explicit this-week signal
    p2_context = [
        'build', 'create', 'implement', 'integrate', 'connect',
        'design', 'write', 'develop', 'test', 'verify', 'validate',
        'update', 'configure', 'fix', 'debug', 'optimize', 'improve'
    ]
    if any(k in name for k in p2_context) and any(k in name for k in ['this week', 'now', 'active', 'current', 'in progress']):
        return 'P2'
    
    # P3: Medium / Follow Up - ongoing work, maintenance, documentation
    # Default for most remaining cards
    p3_signals = [
        'setup', 'install', 'run', 'deploy', 'launch', 'setup github',
        'research', 'investigate', 'review', 'audit', 'plan', 'analyze',
        'website content', 'social post', 'schedule',
        'track ', 'monitor', 'report', 'update doc', 'document',
        'discord bot', 'bot script', 'keep live', 'maintenance',
        'weekly', 'monthly', 'inventory count', 'count'
    ]
    if any(k in name for k in p3_signals):
        return 'P3'
    
    # P4: Medium Low / Backlog - nice-to-haves, polish items, non-urgent improvements
    p4_signals = [
        'backlog', 'later', 'maybe', 'park', 'hold', 'someday',
        'polish', 'cleanup', 'refactor', 'renovate', 'redesign',
        'enhancement', 'nice to have', 'optional', 'future improvement',
        'branding', 'template design'
    ]
    if any(k in name for k in p4_signals):
        return 'P4'
    
    # P5: Low / Review - needs assessment, approval, validation, post-launch items
    p5_signals = [
        'assess', 'evaluate', 'validate', 'check', 'approval', 'review needed',
        'review required', 'decision needed', 'approval needed',
        'get ', 'confirm ', 'verify ', 'check if', 'find out',
        'username', 'credential', 'access', 'account',
        'substack', 'youtube', 'discord', 'tiktok', 'content calendar',
        'ai video', 'ai image', 'social media', 'marketing campaign',
        'future:', 'future ', 'paid upgrade', 'voice ai', 'ar menu',
        'drone delivery', 'blockchain', 'loyalty token'
    ]
    if any(k in name for k in p5_signals):
        return 'P5'
    
    # P6: Very Low / Blocked / Waiting - seasonal, waiting on external, explicitly blocked
    p6_signals = [
        'blocked', 'waiting', 'dependency', 'external', 'waiting on', 'blocked by',
        'seasonal', 'event', 'campaign', 'holiday', '2027', '2028',
        'halloween', 'christmas', 'thanksgiving', 'easter', 'valentine',
        'mothers day', 'fathers day', 'black friday', 'cyber monday'
    ]
    if any(k in name for k in p6_signals):
        return 'P6'
    
    # Future Ideas explicitly
    future_signals = [
        'future ideas', 'future', 'ai answering', 'phone number', 'sms', 'text automation',
        'google voice', 'research free', 'evaluate ai', 'voice ai receptionist',
        'ar menu preview', 'paid upgrade', 'after revenue proof', 'someday',
        'next year', 'future campaign', 'new year new'
    ]
    if any(k in name for k in future_signals):
        return 'Future Ideas'
    
    # Default to P3 for everything else
    return 'P3'

def check_cross_board_duplicate(key, token, card_name):
    """Check if card exists on VOID Ops board."""
    name_lower = card_name.strip().lower()
    try:
        void_cards = requests.get(
            f"https://api.trello.com/1/boards/{VOID_BOARD_ID}/cards",
            params={"key": key, "token": token, "fields": "id,name", "limit": 1000, "filter": "all"},
            timeout=30,
        ).json()
        for c in void_cards:
            if c.get('name', '').strip().lower() == name_lower:
                return c
    except:
        pass
    return None

def enforce_top_10_limit(key, token, list_id, label_map):
    """Ensure Top 10 list has exactly 10 cards. Demote oldest if over, promote highest-value if under."""
    top10_label_id = label_map.get('Top 10')
    
    # Fetch all board cards and derive Top 10 by label to avoid label-cards endpoint issues
    board_cards = requests.get(
        f"https://api.trello.com/1/boards/{TORUS_BOARD_ID}/cards",
        params={"key": key, "token": token, "fields": "id,name,idList,labels,dateLastActivity", "filter": "all"},
        timeout=30,
    ).json()
    labeled_cards = []
    for c in board_cards:
        if any(l.get('id') == top10_label_id for l in c.get('labels', [])):
            labeled_cards.append(c)
    
    # Get cards in the canonical Top 10 list
    list_cards = requests.get(
        f"https://api.trello.com/1/lists/{list_id}/cards",
        params={"key": key, "token": token, "fields": "id,name,dateLastActivity", "filter": "all"},
        timeout=10,
    ).json()
    
    # List membership and label must match exactly
    list_card_ids = {c['id'] for c in list_cards}
    labeled_not_in_list = [c for c in labeled_cards if c['id'] not in list_card_ids]
    
    # Ensure every card in the list has the Top 10 label
    missing_label_in_list = [c for c in list_cards if not any(l.get('id') == top10_label_id for l in c.get('labels', []))]
    for card in missing_label_in_list:
        if top10_label_id:
            requests.post(
                f"https://api.trello.com/1/cards/{card['id']}/idLabels",
                params={"key": key, "token": token},
                data={"value": top10_label_id},
                timeout=15,
            )
    
    # Remove Top 10 label from cards outside canonical list
    for card in labeled_not_in_list:
        if top10_label_id:
            requests.delete(
                f"https://api.trello.com/1/cards/{card['id']}/idLabels/{top10_label_id}",
                params={"key": key, "token": token},
                timeout=10,
            )
    
    # Refresh list cards after cleanup
    list_cards = requests.get(
        f"https://api.trello.com/1/lists/{list_id}/cards",
        params={"key": key, "token": token, "fields": "id,name,dateLastActivity", "filter": "all"},
        timeout=10,
    ).json()
    
    if len(list_cards) > TOP_10_MAX:
        # Sort by dateLastActivity, demote oldest excess cards to P1
        sorted_cards = sorted(list_cards, key=lambda x: x.get('dateLastActivity', '') or '')
        excess = sorted_cards[TOP_10_MAX:]
        
        p1_list_id = LIST_IDS.get('P1')
        for card in excess:
            # Remove Top 10 label
            if top10_label_id:
                requests.delete(
                    f"https://api.trello.com/1/cards/{card['id']}/idLabels/{top10_label_id}",
                    params={"key": key, "token": token},
                    timeout=10,
                )
            
            # Move to P1
            if p1_list_id:
                requests.put(
                    f"https://api.trello.com/1/cards/{card['id']}",
                    params={"key": key, "token": token},
                    data={"idList": p1_list_id},
                    timeout=15,
                )
        
        return f"Demoted {len(excess)} cards from Top 10 to P1, cleaned {len(labeled_not_in_list)} stray labels"
    
    elif len(list_cards) < TOP_10_MAX:
        # Promote highest-value P0/P1 cards to fill Top 10
        candidates = []
        for c in board_cards:
            c_labels = {l['name'] for l in c.get('labels', [])}
            if 'Top 10' in c_labels:
                continue
            score = 0
            if 'P0' in c_labels:
                score += 10
            if 'P1' in c_labels:
                score += 5
            name_lower = c.get('name', '').lower()
            top10_signals = ['launch', 'deploy', 'revenue', 'payment', 'square', 'website', 'dashboard', 'docker', 'production', 'first sale', 'go live']
            if any(s in name_lower for s in top10_signals):
                score += 3
            if score > 0:
                candidates.append((score, c))
        
        candidates.sort(key=lambda x: (-x[0], x[1].get('dateLastActivity', '') or ''))
        promoted = 0
        for score, card in candidates[:TOP_10_MAX - len(list_cards)]:
            r = requests.put(
                f"https://api.trello.com/1/cards/{card['id']}",
                params={"key": key, "token": token},
                data={"idList": list_id},
                timeout=15,
            )
            if r.status_code == 200 and top10_label_id:
                requests.post(
                    f"https://api.trello.com/1/cards/{card['id']}/idLabels",
                    params={"key": key, "token": token},
                    data={"value": top10_label_id},
                    timeout=15,
                )
                promoted += 1
        return f"Promoted {promoted} cards into Top 10, cleaned {len(labeled_not_in_list)} stray labels"
    
    return f"Top 10 at capacity: {TOP_10_MAX}/{TOP_10_MAX}, cleaned {len(labeled_not_in_list)} stray labels"

def process_card(key, token, card, list_map, label_map, board_username_to_id=None, board_fullname_to_id=None):
    """Auto-process a single card: classify, label, move, index, enforce Top 10 limit, set due dates, checklists, members."""
    card_id = card['id']
    card_name = card.get('name', '')
    updates = {}
    
    # Member lookup caches
    board_username_to_id = board_username_to_id or {}
    board_fullname_to_id = board_fullname_to_id or {}
    
    # 1. Classify
    t0 = datetime.now()
    classification = classify_card(card)
    target_list_id = LIST_IDS.get(classification)
    current_list_id = card.get('idList')
    t1 = datetime.now()
    print(f"    [classify] {(t1-t0).total_seconds():.2f}s -> {classification}")
    
    # 2. Move to correct list
    if target_list_id and target_list_id != current_list_id:
        # Special handling for Top 10 - enforce limit
        if classification == 'Top 10' and target_list_id == LIST_IDS.get('Top 10'):
            top10_list_id = LIST_IDS.get('Top 10')
            current_top10 = requests.get(
                f"https://api.trello.com/1/lists/{top10_list_id}/cards",
                params={"key": key, "token": token, "fields": "id", "filter": "all"},
                timeout=10,
            ).json()
            
            if len(current_top10) >= TOP_10_MAX:
                # Demote oldest Top 10 card
                sorted_top10 = sorted(current_top10, key=lambda x: x.get('dateLastActivity', '') or '')
                oldest = sorted_top10[0]
                
                # Remove Top 10 label from oldest
                top10_label_id = label_map.get('Top 10')
                if top10_label_id:
                    requests.delete(
                        f"https://api.trello.com/1/cards/{oldest['id']}/idLabels/{top10_label_id}",
                        params={"key": key, "token": token},
                        timeout=10,
                    )
                
                # Move oldest to P1
                p1_list_id = LIST_IDS.get('P1')
                if p1_list_id:
                    requests.put(
                        f"https://api.trello.com/1/cards/{oldest['id']}",
                        params={"key": key, "token": token},
                        data={"idList": p1_list_id},
                        timeout=15,
                    )
                    updates['demoted'] = oldest['id']
        
        r = requests.put(
            f"https://api.trello.com/1/cards/{card_id}",
            params={"key": key, "token": token},
            data={"idList": target_list_id},
            timeout=15,
        )
        updates['moved'] = classification if r.status_code == 200 else None
        print(f"    [move] {r.status_code}")
    
    # 3. Ensure priority labels
    priority_labels = ['P0', 'P1', 'P2', 'P3', 'P4', 'P5', 'P6', 'Top 10', 'Future Ideas', "Sir Azure's Queue", "Sir Green's Queue"]
    for label_name in priority_labels:
        label_id = label_map.get(label_name)
        if label_id and label_name not in [l['name'] for l in card.get('labels', [])]:
            if classification == label_name:
                r = requests.post(
                    f"https://api.trello.com/1/cards/{card_id}/idLabels",
                    params={"key": key, "token": token},
                    data={"value": label_id},
                    timeout=15,
                )
                if r.status_code == 200:
                    updates.setdefault('labeled', []).append(label_name)
    print(f"    [labels] {updates.get('labeled', [])}")
    
    # 4. Set due date and follow-up date
    now = datetime.now()
    
    # Set due date
    due_days = DUE_DATE_POLICY.get(classification, 7)
    due_date = now + timedelta(days=due_days)
    due_iso = due_date.isoformat()
    
    current_due = card.get('due')
    if not current_due:
        r = requests.put(
            f"https://api.trello.com/1/cards/{card_id}",
            params={"key": key, "token": token},
            data={"due": due_iso},
            timeout=15,
        )
        if r.status_code == 200:
            updates['due'] = due_iso
    
    # Set follow-up date in description
    followup_days = FOLLOWUP_POLICY.get(classification, 7)
    followup_date = now + timedelta(days=followup_days)
    followup_iso = followup_date.isoformat()
    
    desc = card.get('desc', '') or ''
    if 'Follow-up:' not in desc and 'Auto-indexed:' not in desc:
        desc = f"Auto-indexed: {card_name}\n\n"
        desc += f"Priority: {classification}\n"
        desc += f"Board: Torus_Ops | List: {list_map.get(current_list_id, 'Unknown')}\n"
        desc += f"Source: automation\n"
        desc += f"Trello Card ID: {card_id}\n"
        desc += f"Indexed: {datetime.now().isoformat()}\n"
        desc += f"Due: {due_iso}\n"
        desc += f"Follow-up: {followup_iso}\n"
        if classification in {"Sir Azure's Queue", "Sir Green's Queue"}:
            desc += f"Queue: {classification}\n"
            desc += "Check VOID Ops board for mirrored tracking card.\n"
        desc += "\n---\nCheck TRELLO_CARD_INDEX.json before creating similar cards.\n"
        r = requests.put(
            f"https://api.trello.com/1/cards/{card_id}",
            params={"key": key, "token": token},
            data={"desc": desc},
            timeout=15,
        )
        if r.status_code == 200:
            updates['description'] = 'added'
    print(f"    [desc] {updates.get('description')}")
    
    # 5. Ensure checklist exists
    checklist_name = f"Priority: {classification}"
    existing_checklists = requests.get(
        f"https://api.trello.com/1/cards/{card_id}/checklists",
        params={"key": key, "token": token},
        timeout=10,
    ).json()
    
    checklist_id = None
    for cl in existing_checklists:
        if cl.get('name') == checklist_name:
            checklist_id = cl['id']
            break
    
    if not checklist_id:
        template = CHECKLIST_TEMPLATES.get(classification, ['Complete task', 'Verify completion'])
        r = requests.post(
            f"https://api.trello.com/1/cards/{card_id}/checklists",
            params={"key": key, "token": token},
            data={"name": checklist_name},
            timeout=15,
        )
        if r.status_code == 200:
            checklist_id = r.json().get('id')
            for item in template:
                requests.post(
                    f"https://api.trello.com/1/checklists/{checklist_id}/checkItems",
                    params={"key": key, "token": token},
                    data={"name": item, "checked": "false"},
                    timeout=10,
                )
            updates['checklist'] = f"added {len(template)} items"
    print(f"    [checklist] {updates.get('checklist')}")
    
    # 6. Assign member based on priority/queue
    member_id = MEMBER_ASSIGNMENTS.get(classification)
    if member_id:
        target_member = board_username_to_id.get(member_id.lower()) or board_fullname_to_id.get(member_id.lower())
        
        if target_member:
            current_members = requests.get(
                f"https://api.trello.com/1/cards/{card_id}/members",
                params={"key": key, "token": token},
                timeout=10,
            ).json()
            
            if not any(m.get('id') == target_member for m in current_members):
                r = requests.post(
                    f"https://api.trello.com/1/cards/{card_id}/idMembers",
                    params={"key": key, "token": token},
                    data={"value": target_member},
                    timeout=15,
                )
                if r.status_code == 200:
                    updates['member'] = member_id
    print(f"    [member] {updates.get('member')}")
    
    # 7. Check cross-board duplicates
    duplicate = check_cross_board_duplicate(key, token, card_name)
    if duplicate:
        updates['duplicate'] = f"{duplicate['id']} on VOID Ops"
    
    # 8. Update index
    index = load_index()
    existing = next((c for c in index['cards'] if c['id'] == card_id), None)
    if existing:
        existing['labels'] = [l['name'] for l in card.get('labels', [])]
        existing['last_updated'] = datetime.now().isoformat()
    else:
        index['cards'].append({
            "id": card_id,
            "name": card_name,
            "board": "Torus_Ops",
            "list": list_map.get(current_list_id, ''),
            "labels": [l['name'] for l in card.get('labels', [])],
            "indexed_at": datetime.now().isoformat(),
        })
    index['last_checked'] = datetime.now().isoformat()
    save_index(index)
    updates['indexed'] = True
    print(f"    [index] indexed={updates['indexed']}")
    
    return updates

def audit_card_classifications():
    """Audit current vs proposed classification without changing cards."""
    key, token = get_trello_credentials()

    lists = requests.get(
        f"https://api.trello.com/1/boards/{TORUS_BOARD_ID}/lists",
        params={"key": key, "token": token, "fields": "id,name,pos", "filter": "all"},
        timeout=10,
    ).json()
    list_map = {l["id"]: l["name"] for l in lists}

    cards = requests.get(
        f"https://api.trello.com/1/boards/{TORUS_BOARD_ID}/cards",
        params={"key": key, "token": token, "fields": "id,name,desc,idList,labels", "limit": 1000, "filter": "all"},
        timeout=30,
    ).json()

    labels = requests.get(
        f"https://api.trello.com/1/boards/{TORUS_BOARD_ID}/labels",
        params={"key": key, "token": token, "fields": "id,name,color"},
        timeout=10,
    ).json()
    label_map = {l["name"]: l["id"] for l in labels}

    proposed_counts = {
        'Top 10 — Focus Fleet': 0,
        "Torus Coffee's Future Ideas": 0,
        'P0 - Alert / Critical / Do Now': 0,
        'To Do': 0,
        'P1 - High / Doing Now': 0,
        'P2 - Med High / This Week': 0,
        'P3 - Medium / Follow Up': 0,
        'P4 - Medium Low / Backlog': 0,
        'P5 - Low / Review': 0,
        'P6 - Very Low / Blocked / Waiting': 0,
        "Sir Azure's Queue": 0,
        "Sir Green's Queue": 0,
        'Follow-up': 0,
        'Done': 0,
        'UNCLASSIFIED': 0,
    }
    label_changes = []
    moves = []

    for card in cards:
        classification = classify_card(card)
        target_list_id = LIST_IDS.get(classification)
        target_list_name = LIST_NAMES.get(target_list_id) if target_list_id else None
        current_list_name = LIST_NAMES.get(card.get("idList"), list_map.get(card.get("idList"), "Unknown"))
        proposed_counts[target_list_name or 'UNCLASSIFIED'] += 1

        current_label_names = {l["name"] for l in card.get("labels", [])}
        needed_labels = {classification}
        if classification in {"Sir Azure's Queue", "Sir Green's Queue"}:
            needed_labels.add(classification)
        missing = needed_labels - current_label_names
        if missing:
            label_changes.append((card["name"], sorted(missing)))

        if target_list_name and target_list_name != current_list_name:
            moves.append((card["name"], current_list_name, target_list_name))

    print("\n=== PROPOSED CLASSIFICATION AUDIT ===\n")
    for name, count in proposed_counts.items():
        print(f"{name}: {count}")

    print(f"\nProposed moves: {len(moves)}")
    for m in moves[:40]:
        print(f"  MOVE: {m[0]} | {m[1]} -> {m[2]}")

    print(f"\nProposed label additions: {len(label_changes)}")
    for lc in label_changes[:40]:
        print(f"  LABEL: {lc[0]} +{lc[1]}")

    return {
        "proposed_counts": proposed_counts,
        "moves": moves,
        "label_changes": label_changes,
    }

def run_full_sort():
    """Full board sort and cleanup with Top 10 enforcement. Batched and resumable."""
    import time
    key, token = get_trello_credentials()
    
    # Get all data
    lists = requests.get(
        f"https://api.trello.com/1/boards/{TORUS_BOARD_ID}/lists",
        params={"key": key, "token": token, "fields": "id,name,pos", "filter": "all"},
        timeout=10,
    ).json()
    list_map = {l['id']: l['name'] for l in lists}
    name_to_ids = {}
    for l in lists:
        name_to_ids.setdefault(l['name'], []).append(l['id'])
    
    cards = requests.get(
        f"https://api.trello.com/1/boards/{TORUS_BOARD_ID}/cards",
        params={"key": key, "token": token, "fields": "id,name,desc,idList,labels,dateLastActivity", "limit": 1000, "filter": "all"},
        timeout=30,
    ).json()
    
    labels = requests.get(
        f"https://api.trello.com/1/boards/{TORUS_BOARD_ID}/labels",
        params={"key": key, "token": token, "fields": "id,name,color"},
        timeout=10,
    ).json()
    label_map = {l['name']: l['id'] for l in labels}
    
    # Prefetch board members once to avoid N× member lookups
    try:
        board_members = requests.get(
            f"https://api.trello.com/1/boards/{TORUS_BOARD_ID}/members",
            params={"key": key, "token": token, "fields": "id,username,fullName"},
            timeout=10,
        ).json()
        username_to_id = {m.get('username','').lower(): m['id'] for m in board_members}
        fullname_to_id = {m.get('fullName','').lower(): m['id'] for m in board_members}
    except Exception:
        username_to_id = {}
        fullname_to_id = {}
    
    # Normalize duplicate lists: move cards from extras into canonical list IDs
    canonical = {
        'Top 10 — Focus Fleet': LIST_IDS.get('Top 10'),
        'P0 - Alert / Critical / Do Now': LIST_IDS.get('P0'),
        'P1 - High / Doing Now': LIST_IDS.get('P1'),
        'P2 - Med High / This Week': LIST_IDS.get('P2'),
        'P3 - Medium / Follow Up': LIST_IDS.get('P3'),
        'P4 - Medium Low / Backlog': LIST_IDS.get('P4'),
        'P5 - Low / Review': LIST_IDS.get('P5'),
        'P6 - Very Low / Blocked / Waiting': LIST_IDS.get('P6'),
        "Torus Coffee's Future Ideas": LIST_IDS.get('Future Ideas'),
        "Sir Azure's Queue": LIST_IDS.get("Sir Azure's Queue"),
        "Sir Green's Queue": LIST_IDS.get("Sir Green's Queue"),
    }
    normalized = 0
    for name, canonical_id in canonical.items():
        if not canonical_id:
            continue
        extras = [lid for lid in name_to_ids.get(name, []) if lid != canonical_id]
        if not extras:
            continue
        for card in cards:
            if card.get('idList') in extras:
                try:
                    r = requests.put(
                        f"https://api.trello.com/1/cards/{card['id']}",
                        params={"key": key, "token": token},
                        data={"idList": canonical_id},
                        timeout=15,
                    )
                    if r.status_code == 200:
                        normalized += 1
                except Exception:
                    pass
    print(f"Normalized duplicate-list cards: {normalized}")
    
    # Load index to skip already-processed cards
    index = load_index()
    indexed_ids = {c['id'] for c in index.get('cards', [])}
    
    # Only process unindexed cards; keep indexing as the resume marker
    unindexed = [c for c in cards if c['id'] not in indexed_ids]
    unindexed_sorted = sorted(unindexed, key=lambda x: x.get('dateLastActivity', '') or '')
    cards_to_process = unindexed_sorted
    
    print(f"Total cards: {len(cards)}")
    print(f"Already indexed: {len(indexed_ids)}")
    print(f"To process: {len(unindexed_sorted)}")
    
    # Process in batches
    BATCH_SIZE = 20
    PAUSE_SECONDS = 2
    results = {
        'moved': 0,
        'labeled': 0,
        'indexed': 0,
        'duplicates': 0,
        'errors': 0,
        'top10_demoted': 0
    }
    
    for batch_start in range(0, len(cards_to_process), BATCH_SIZE):
        batch = cards_to_process[batch_start:batch_start + BATCH_SIZE]
        print(f"\n--- Batch {batch_start // BATCH_SIZE + 1}/{(len(cards_to_process) + BATCH_SIZE - 1) // BATCH_SIZE} ---")
        
        for i, card in enumerate(batch, 1):
            t0 = datetime.now()
            updates = process_card(key, token, card, list_map, label_map, username_to_id, fullname_to_id)
            dt = (datetime.now() - t0).total_seconds()
            if updates.get('moved'):
                results['moved'] += 1
            if updates.get('labeled'):
                results['labeled'] += len(updates['labeled'])
            if updates.get('indexed'):
                results['indexed'] += 1
            if updates.get('duplicate'):
                results['duplicates'] += 1
            if updates.get('demoted'):
                results['top10_demoted'] += 1
            
            # Progress
            global_idx = batch_start + i
            print(f"  [{global_idx}/{len(cards_to_process)}] {dt:.1f}s | {card.get('name','')[:60]}")
        
        # Pause between batches
        if batch_start + BATCH_SIZE < len(cards_to_process):
            print(f"  Pausing {PAUSE_SECONDS}s...")
            time.sleep(PAUSE_SECONDS)
    
    # Enforce Top 10 limit
    top10_list_id = LIST_IDS.get('Top 10')
    if top10_list_id:
        limit_result = enforce_top_10_limit(key, token, top10_list_id, label_map)
        print(f"Top 10 enforcement: {limit_result}")
    
    # Archive exact duplicates
    name_groups = defaultdict(list)
    for c in cards:
        name = c.get('name', '').strip().lower()
        if name:
            name_groups[name].append(c)
    
    archived = 0
    for name, dupes in name_groups.items():
        if len(dupes) > 1:
            dupes_sorted = sorted(dupes, key=lambda x: x.get('dateLastActivity', '') or '')
            for d in dupes_sorted[1:]:
                try:
                    r = requests.put(
                        f"https://api.trello.com/1/cards/{d['id']}",
                        params={"key": key, "token": token},
                        data={"closed": "true"},
                        timeout=15,
                    )
                    if r.status_code == 200:
                        archived += 1
                except Exception:
                    pass
    
    print("\n=== TRELLO AUTOMATION COMPLETE ===")
    print(f"Normalized duplicate-list cards: {normalized}")
    print(f"Moved: {results['moved']}")
    print(f"Labeled: {results['labeled']}")
    print(f"Indexed: {results['indexed']}")
    print(f"Cross-board duplicates: {results['duplicates']}")
    print(f"Top 10 demoted: {results['top10_demoted']}")
    print(f"Archived duplicates: {archived}")
    print(f"Errors: {results['errors']}")
    
    return results

def watch_new_cards():
    """Watch for new cards and auto-process them with Top 10 enforcement."""
    key, token = get_trello_credentials()
    
    lists = requests.get(
        f"https://api.trello.com/1/boards/{TORUS_BOARD_ID}/lists",
        params={"key": key, "token": token, "fields": "id,name", "filter": "all"},
        timeout=10,
    ).json()
    list_map = {l['id']: l['name'] for l in lists}
    
    labels = requests.get(
        f"https://api.trello.com/1/boards/{TORUS_BOARD_ID}/labels",
        params={"key": key, "token": token, "fields": "id,name,color"},
        timeout=10,
    ).json()
    label_map = {l['name']: l['id'] for l in labels}
    
    current_cards = requests.get(
        f"https://api.trello.com/1/boards/{TORUS_BOARD_ID}/cards",
        params={"key": key, "token": token, "fields": "id,name,desc,idList,labels", "limit": 1000, "filter": "all"},
        timeout=30,
    ).json()
    
    index = load_index()
    indexed_ids = {c['id'] for c in index['cards']}
    
    new_cards = [c for c in current_cards if c['id'] not in indexed_ids]
    processed = 0
    
    for card in new_cards:
        try:
            updates = process_card(key, token, card, list_map, label_map)
            processed += 1
            print(f"Processed: {card.get('name', '')[:60]} -> {updates}")
        except Exception as e:
            print(f"Error: {e}")
    
    # Enforce Top 10 limit after processing new cards
    top10_list_id = LIST_IDS.get('Top 10 — Focus Fleet')
    if top10_list_id:
        limit_result = enforce_top_10_limit(key, token, top10_list_id, label_map)
        print(f"Top 10 enforcement: {limit_result}")
    
    print(f"\nProcessed {processed} new cards")
    return processed

if __name__ == "__main__":
    import sys
    if len(sys.argv) > 1 and sys.argv[1] == "audit":
        audit_card_classifications()
    elif len(sys.argv) > 1 and sys.argv[1] == "watch":
        watch_new_cards()
    else:
        run_full_sort()
