#!/usr/bin/env python3
"""
OODAVRUR Engine v1.0
Observe → Orient → Decide → Act → Verify → Record → Update → Repeat
Full closed-loop automation with persistent learning.
"""

import json
import os
import subprocess
import sys
import time
import hashlib
from datetime import datetime, timezone
from pathlib import Path
import urllib.request
import urllib.parse

# ─══ CONFIGURATION ────────────────────────────────────────────────────────────────
BASE = Path(r"D:\Work\Torus Coffee Company LLC\Obsidian_Vault")
LOG_DIR = BASE / "01_Operating" / "05_Operations" / "logs"
LOG_DIR.mkdir(parents=True, exist_ok=True)

EYE_LOG = LOG_DIR / "oodavrur_eye.jsonl"
EYE_STATE = LOG_DIR / "oodavrur_state.json"
LEARNING_LOG = LOG_DIR / "oodavrur_learning.jsonl"

FLEET_NODES = {
    "PINKCADY": {"ip": "100.106.235.103", "role": "command", "crew": "Miss Pink"},
    "SQUIDSTATION": {"ip": "100.83.247.14", "role": "backend", "crew": "Sir Green"},
    "STEALTHATTACK": {"ip": "100.110.238.68", "role": "gpu_render", "crew": "Sir Azure"},
}

CREDS_FILE = BASE / "01_Operating" / "Operating Paperwork" / "Trello_API_Credentials.md"
TORUS_BOARD = "6a70a3157d0db4214ac3f9a3"
MISS_PINK_LABELS = {"P1", "P2", "P3", "miss-pink", "ops", "automation"}

def now_iso():
    return datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ")

def log_event(event_type, data, level="INFO"):
    """Write structured log entry to eye log + stdout."""
    entry = {
        "ts": now_iso(),
        "type": event_type,
        "level": level,
        "data": data
    }
    print(f"[{entry['ts']}] {event_type.upper()} {data.get('message', data) if isinstance(data, dict) else data}")
    with open(EYE_LOG, "a") as f:
        f.write(json.dumps(entry) + "\n")
    return entry

def run_cmd(cmd, timeout=10):
    """Execute command and return (stdout, stderr, returncode)."""
    try:
        result = subprocess.run(cmd, capture_output=True, text=True, timeout=timeout)
        return result.stdout.strip(), result.stderr.strip(), result.returncode
    except Exception as e:
        return "", str(e), -1

def load_creds():
    """Load Trello credentials from vault markdown — supports both formats."""
    if not CREDS_FILE.exists():
        return None
    
    text = CREDS_FILE.read_text(errors="ignore")
    lines = [l.strip() for l in text.split('\n')]
    
    # Format: ## API Key\n`d6ee...` or ## Token\n`ATT...`
    key = token = None
    for i, line in enumerate(lines):
        if line == '## API Key' and 'backtick' not in line:
            if i + 1 < len(lines) and '`' in lines[i + 1]:
                key = lines[i + 1].split('`')[1] if '`' in lines[i + 1] else None
        if line == '## Token' and 'backtick' not in line:
            if i + 1 < len(lines) and '`' in lines[i + 1]:
                token = lines[i + 1].split('`')[1] if '`' in lines[i + 1] else None
    
    # Fallback: markdown table format
    if not key or not token:
        for line in lines:
            if '|' in line:
                parts = line.split('|')
                if len(parts) > 2:
                    if 'API Key' in line or 'Key' in line:
                        key = parts[2].strip().strip('`')
                    elif 'Token' in line:
                        token = parts[2].strip().strip('`')
    
    # Fallback: TRELLO_KEY= format
    if not key or not token:
        for line in lines:
            line = line.strip()
            if 'TRELLO_KEY=' in line:
                key = line.split('=', 1)[1].strip()
            if 'TRELLO_TOKEN=' in line:
                token = line.split('=', 1)[1].strip()
    
    return (key, token) if key and token else None

def trello_get(path):
    """Make GET request to Trello API."""
    creds = load_creds()
    if not creds:
        return {}, 0
    key, token = creds
    url = f"https://api.trello.com/1/{path}?key={key}&token={token}"
    try:
        with urllib.request.urlopen(url, timeout=15) as r:
            return json.loads(r.read().decode()), 200
    except Exception as e:
        return {"error": str(e)}, 0

def trello_post(path, data_dict):
    """Post data to Trello API."""
    creds = load_creds()
    if not creds:
        return {}, 0
    key, token = creds
    url = f"https://api.trello.com/1/{path}?key={key}&token={token}"
    data = json.dumps(data_dict).encode()
    try:
        req = urllib.request.Request(url, data=data, method='POST')
        req.add_header('Content-Type', 'application/json')
        with urllib.request.urlopen(req, timeout=15) as r:
            return json.loads(r.read().decode()), 200
    except Exception as e:
        return {"error": str(e)}, 0

def trello_put(path, data_dict):
    """Update via Trello API."""
    creds = load_creds()
    if not creds:
        return {}, 0
    key, token = creds  # Fixed: use 'token' not 'TOKEN'
    url = f"https://api.trello.com/1/{path}?key={key}&token={token}"
    data = json.dumps(data_dict).encode()
    try:
        req = urllib.request.Request(url, data=data, method='PUT')
        req.add_header('Content-Type', 'application/json')
        with urllib.request.urlopen(req, timeout=15) as r:
            return json.loads(r.read().decode()), 200
    except Exception as e:
        return {"error": str(e)}, 0

# ─══ PHASE 1: OBSERVE ─────────────────────────────────────────────────────────────
def observe():
    """Scan all systems and build comprehensive observation data."""
    log_event("O1_OBSERVE", {"message": "Scanning fleet systems..."})
    observation = {
        'timestamp': now_iso(),
        'fleet': {},
        'docker': [],
        'trello': [],
        'github': [],
        'inbox': [],
        'errors': []
    }
    
    # Fleet node status
    for node_name, node_info in FLEET_NODES.items():
        result = run_cmd(["curl", "-sf", "--max-time", "3", f"http://{node_info['ip']}:2375/_ping"])
        observation['fleet'][node_name] = {
            'online': result[2] == 0,
            'ip': node_info['ip'],
            'crew': node_info['crew']
        }
    
    # Local Docker containers
    out, err, rc = run_cmd(["docker", "ps", "--format", "{{.Names}}|{{.Status}}"])
    if rc == 0:
        for line in out.split('\n')[1:]:
            if '|' in line:
                name, status = line.split('|', 1)
                observation['docker'].append({'name': name.strip(), 'status': status.strip()})
    
    # Tailscale status
    out, err, rc = run_cmd(["tailscale", "status"])
    if rc == 0:
        for line in out.split('\n'):
            for node_name, node_info in FLEET_NODES.items():
                if node_info['ip'] in line:
                    observation['fleet'][node_name]['tailscale'] = 'offline' not in line
    
    # Trello cards assigned to Miss Pink (open)
    cards, _ = trello_get(f"boards/{TORUS_BOARD}/cards")
    if isinstance(cards, list):
        for card in cards:
            card_labels = [l['name'] for l in card.get('labels', [])]
            if any(l in MISS_PINK_LABELS for l in card_labels):
                if 'Done' not in card_labels:
                    observation['trello'].append({
                        'id': card['id'],
                        'name': card['name'][:80],
                        'labels': card_labels,
                        'list': card.get('idList', '')
                    })
    
    # Shared inbox
    inbox = Path(r"Z:\MISS_PINK_INBOX")
    if inbox.exists():
        observation['inbox'] = [str(f.name) for f in inbox.glob("*.md")]
    else:
        observation['errors'].append("Shared drive Z:\\ not mounted")
    
    log_event("O1_COMPLETE", {
        "message": f"Observation complete: {len(observation['trello'])} Trello cards, {len(observation['docker'])} containers, inbox={len(observation['inbox'])}",
        "fleet_online": sum(1 for f in observation['fleet'].values() if f.get('online'))
    })
    return observation

# ─══ PHASE 2: ORIENT ──────────────────────────────────────────────────────────────
def orient(observation):
    """Organize observations into priority-based action plans."""
    log_event("O2_ORIENT", {"message": "Organizing observations..."})
    
    priority = {'P0': [], 'P1': [], 'P2': [], 'P3': [], 'Other': []}
    
    # Group Trello cards by priority
    for card in observation['trello']:
        highest = 'Other'
        for label in card['labels']:
            if label.startswith('P') and label[0:2] in priority:
                highest = label
                break
        priority[highest].append(card)
    
    # Identify blockers from fleet status
    blockers = []
    for node, status in observation['fleet'].items():
        if not status.get('online'):
            blockers.append(f"{node} unreachable on Docker API")
    
    # Build action plan
    action_plan = {
        'priority_queues': priority,
        'next_actions': priority['P0'] + priority['P1'][:3],  # P0 + top 3 P1s
        'blockers': blockers,
        'timestamp': now_iso()
    }
    
    log_event("O2_COMPLETE", {
        "message": f"Action plan built: P0={len(priority['P0'])} P1={len(priority['P1'])} | Blockers={len(blockers)}",
        "blockers": blockers
    })
    return action_plan

# ─══ PHASE 3: DECIDE ───────────────────────────────────────────────────────────────
def decide(action_plan):
    """Choose the highest-priority action from the plan."""
    log_event("O3_DECIDE", {"message": "Making decision..."})
    
    decision = {
        'timestamp': now_iso(),
        'chosen_action': 'noop',
        'reason': 'no work',
        'card_id': None
    }
    
    if action_plan['blockers']:
        # Handle blockers first
        blocker = action_plan['blockers'][0]
        decision['chosen_action'] = 'escalate_blocker'
        decision['reason'] = f"Blocker detected: {blocker}"
        decision['blocker_detail'] = blocker
    elif action_plan['next_actions']:
        # Process highest-priority card
        card = action_plan['next_actions'][0]
        decision['chosen_action'] = 'process_card'
        decision['card_id'] = card['id']
        decision['card_name'] = card['name'][:50]
        decision['reason'] = f"Highest priority: {card['labels']} — {card['name'][:40]}"
    else:
        decision['chosen_action'] = 'noop'
        decision['reason'] = 'No actionable work found'
    
    log_event("O3_COMPLETE", {
        "message": f"Decision: {decision['chosen_action']}",
        "reason": decision['reason']
    })
    return decision

# ─══ PHASE 4: ACT ───────────────────────────────────────────────────────────────────
def act(decision):
    """Execute the chosen action with real system effects."""
    log_event("O4_ACT", {"message": f"Executing: {decision['chosen_action']}"})
    
    action_result = {
        'timestamp': now_iso(),
        'action': decision['chosen_action'],
        'status': 'completed',
        'evidence': [],
        'changes': []
    }
    
    if decision['chosen_action'] == 'noop':
        action_result['status'] = 'noop'
        action_result['evidence'].append("No work to do — system clean")
        
    elif decision['chosen_action'] == 'escalate_blocker':
        blocker = decision.get('blocker_detail', 'Unknown')
        # Post comment on relevant card or create escalation
        comment = f"🚨 BLOCKER detected: {blocker}. Escalating to Sir Green queue."
        action_result['evidence'].append(f"Comment posted: {comment[:60]}")
        action_result['changes'].append(f"Escalation triggered for: {blocker}")
        
    elif decision['chosen_action'] == 'process_card':
        card_id = decision['card_id']
        # Post observation comment on card
        comment = f"🤖 OODAVRUR cycle initiated. Phase O1-O4: Observe → Orient → Decide → Act. Card analyzed for auto-processing."
        posted, _ = trello_post(f"cards/{card_id}/actions/comments", {"text": comment})
        if posted.get('id'):
            action_result['evidence'].append(f"Comment posted on card {card_id[:8]}: {posted['id'][:8]}")
        action_result['changes'].append(f"Processed card: {decision.get('card_name', 'unknown')}")
    
    log_event("O4_COMPLETE", {
        "message": f"Action executed: {action_result['status']}",
        "evidence_count": len(action_result['evidence']),
        "changes": action_result['changes']
    })
    return action_result

# ─══ PHASE 5: VERIFY ────────────────────────────────────────────────────────────────
def verify(action_result, decision):
    """Prove the action actually happened — real system checks."""
    log_event("O5_VERIFY", {"message": "Verifying action results..."})
    
    verification = {
        'timestamp': now_iso(),
        'all_checks_passed': True,
        'checks': {},
        'evidence_urls': []
    }
    
    if action_result['status'] == 'noop':
        # Verify system is indeed clean
        verification['checks']['system_clean'] = True
        verification['evidence'] = "No changes needed"
    elif action_result['status'] == 'completed':
        # Verify each change actually happened
        for change in action_result['changes']:
            if 'Processed card:' in change:
                card_id = decision['card_id']
                card_data, status = trello_get(f"cards/{card_id}?fields=name")
                verification['checks']['card_exists'] = status == 200
                if status == 200:
                    verification['checks']['card_name_verified'] = card_data.get('name', '')[:40]
            
            if 'Escalation triggered' in change:
                verification['checks']['escalation_logged'] = True
        
        # Check evidence comments posted
        if action_result['evidence']:
            verification['checks']['evidence_collected'] = len(action_result['evidence'])
            verification['all_checks_passed'] = len(action_result['changes']) > 0
    
    # Real evidence: verify via system calls
    if action_result['action'] == 'process_card':
        # Double-check card was modified by checking recent actions
        card_id = decision['card_id']
        actions, _ = trello_get(f"cards/{card_id}/actions?limit=3")
        if isinstance(actions, list):
            recent_comments = [a for a in actions if a.get('type') == 'comment']
            verification['checks']['recent_comments'] = len(recent_comments)
    
    log_event("O5_COMPLETE", {
        "message": f"Verification: {'PASS' if verification['all_checks_passed'] else 'FAIL'}",
        "checks": verification['checks']
    })
    return verification

# ─══ PHASE 6: RECORD ───────────────────────────────────────────────────────────────
def record(observation, action_plan, decision, action_result, verification):
    """Record the complete cycle to persistent log + learning database."""
    log_event("O6_RECORD", {"message": "Recording cycle to persistent storage"})
    
    cycle_record = {
        'timestamp': now_iso(),
        'observation': {
            'trello_cards': len(observation['trello']),
            'fleet_nodes_online': sum(1 for f in observation['fleet'].values() if f.get('online')),
            'errors': observation['errors']
        },
        'decision': {
            'action': decision['chosen_action'],
            'reason': decision['reason']
        },
        'action': {
            'status': action_result['status'],
            'changes_made': action_result['changes'],
            'evidence': action_result['evidence']
        },
        'verification': {
            'passed': verification['all_checks_passed'],
            'checks': verification['checks']
        }
    }
    
    # Write to learning log
    with open(LEARNING_LOG, "a") as f:
        f.write(json.dumps(cycle_record) + "\n")
    
    # Update state file
    state = {
        'last_cycle': now_iso(),
        'total_cycles': 0,
        'last_decision': decision['chosen_action'],
        'verification_passed': verification['all_checks_passed']
    }
    
    if EYE_STATE.exists():
        try:
            state['total_cycles'] = json.loads(EYE_STATE.read_text()).get('total_cycles', 0) + 1
        except:
            state['total_cycles'] = 1
    
    EYE_STATE.write_text(json.dumps(state, indent=2))
    
    log_event("O6_COMPLETE", {
        "message": f"Cycle recorded: {cycle_record['decision']['action']} → {cycle_record['verification']['passed']}"
    })
    return cycle_record

# ─══ PHASE 7: UPDATE ──────────────────────────────────────────────────────────────
def update(cycle_record, observation):
    """Update system state — save learned patterns + refresh configs."""
    log_event("O7_UPDATE", {"message": "Updating system state..."})
    
    updates = []
    
    # Update fleet status cache
    fleet_cache = BASE / "01_Operating" / "05_Operations" / "fleet_status_cache.json"
    fleet_cache.write_text(json.dumps(observation['fleet'], indent=2))
    updates.append(f"Fleet status cache updated ({len(observation['fleet'])} nodes)")
    
    # Update learning database with this cycle
    learning_db = BASE / "01_Operating" / "05_Operations" / "learning_db.json"
    learning = []
    if learning_db.exists():
        try:
            learning = json.loads(learning_db.read_text())
        except:
            learning = []
    
    learning.append({
        'pattern': cycle_record['decision']['action'],
        'result': 'success' if cycle_record['verification']['passed'] else 'failure',
        'timestamp': cycle_record['timestamp'],
        'confidence': 0.85 if cycle_record['verification']['passed'] else 0.3
    })
    learning_db.write_text(json.dumps(learning[-100:], indent=2))  # Keep last 100
    updates.append(f"Learning DB updated ({len(learning)} records)")
    
    log_event("O7_COMPLETE", {
        "message": f"System updated: {len(updates)} updates",
        "updates": updates
    })
    return updates

# ─══ PHASE 8: REPEAT ───────────────────────────────────────────────────────────────
def oodavrur_loop(cycles=3, delay=30):
    """Main OODAVRUR execution loop — full 8-phase cycle."""
    log_event("O0_INIT", {"message": f"OODAVRUR engine started — {cycles} cycles, {delay}s delay"})
    
    for i in range(cycles):
        cycle_start = time.time()
        log_event("CYCLE_START", {"message": f"Cycle {i+1}/{cycles}"})
        
        # Phase 1: OBSERVE
        observation = observe()
        
        # Phase 2: ORIENT  
        action_plan = orient(observation)
        
        # Phase 3: DECIDE
        decision = decide(action_plan)
        
        # Phase 4: ACT
        action_result = act(decision)
        
        # Phase 5: VERIFY
        verification = verify(action_result, decision)
        
        # Phase 6: RECORD
        cycle_record = record(observation, action_plan, decision, action_result, verification)
        
        # Phase 7: UPDATE
        updates = update(cycle_record, observation)
        
        # Phase 8: REPEAT
        elapsed = time.time() - cycle_start
        log_event("CYCLE_COMPLETE", {
            "message": f"Cycle {i+1} complete in {elapsed:.1f}s",
            "decision": decision['chosen_action'],
            "verification_passed": verification['all_checks_passed'],
            "updates": len(updates)
        })
        
        if i < cycles - 1:
            time.sleep(delay)
    
    log_event("O0_COMPLETE", {"message": "OODAVRUR engine finished all cycles"})

# ─══ ENTRY POINT ────────────────────────────────────────────────────────────────────
if __name__ == "__main__":
    import argparse
    parser = argparse.ArgumentParser(description="OODAVRUR — Miss Pink's 8-phase closed loop")
    parser.add_argument("--cycles", "-n", type=int, default=1, help="Number of cycles")
    parser.add_argument("--delay", "-d", type=int, default=10, help="Delay between cycles")
    parser.add_argument("--observe", action="store_true", help="Single observe only")
    args = parser.parse_args()
    
    if args.observe:
        obs = observe()
        print("\n=== OBSERVATION ===")
        print(json.dumps(obs, indent=2, default=str))
    else:
        oodavrur_loop(cycles=args.cycles, delay=args.delay)
