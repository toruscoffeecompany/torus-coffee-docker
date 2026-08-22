#!/usr/bin/env python3
"""Capacity-aware scheduler for Trello cards with Google Calendar sync."""
import json
import requests
from datetime import datetime, timedelta
from pathlib import Path

SCRIPT_DIR = Path(__file__).resolve().parent
REPO_ROOT = SCRIPT_DIR.parent.parent.parent
CREDENTIALS_PATH = REPO_ROOT / "01_Operating/Operating Paperwork/Trello_API_Credentials.md"
INDEX_PATH = REPO_ROOT / "10_Skills_Library/05_Operations/TRELLO_CARD_INDEX.json"
SCHEDULE_PATH = REPO_ROOT / "10_Skills_Library/05_Operations/WEEKLY_SCHEDULE.json"
CALENDAR_SYNC_PATH = REPO_ROOT / "10_Skills_Library/05_Operations/CALENDAR_SYNC_LOG.json"

# Weekly capacity limits by priority
WEEKLY_CAPACITY = {
    'P0': 14,        # 2 per day x 7 days
    'Top 10': 10,    # max list size, ~1-2 per day
    'P1': 25,        # 5 per day x 5 days
    'P2': 15,        # 3 per day x 5 days
    'P3': 10,        # 2 per day x 5 days
    'P4': 5,         # 1 per day x 5 days
    'P5': 3,         # 3 per week
    'P6': 2,         # 2 per week
    'Future Ideas': 0,  # No weekly commitment
    "Sir Azure's Queue": 10,
    "Sir Green's Queue": 10,
}

# Day assignments based on priority
DAY_ASSIGNMENTS = {
    'P0': ['Monday', 'Tuesday', 'Wednesday', 'Thursday', 'Friday', 'Saturday', 'Sunday'],
    'Top 10': ['Monday', 'Tuesday', 'Wednesday', 'Thursday', 'Friday'],
    'P1': ['Monday', 'Tuesday', 'Wednesday', 'Thursday', 'Friday'],
    'P2': ['Monday', 'Wednesday', 'Friday'],
    'P3': ['Tuesday', 'Thursday'],
    'P4': ['Wednesday'],
    'P5': ['Friday'],
    'P6': ['Friday'],
    'Future Ideas': [],
    "Sir Azure's Queue": ['Monday', 'Wednesday', 'Friday'],
    "Sir Green's Queue": ['Tuesday', 'Thursday'],
}

def get_trello_credentials():
    creds = CREDENTIALS_PATH.read_text(encoding="utf-8")
    key = next(line for line in creds.splitlines() if line.startswith("`d6ee")).strip("`")
    token = next(line for line in creds.splitlines() if line.startswith("`ATTA")).strip("`")
    return key, token

def load_index():
    if INDEX_PATH.exists():
        return json.loads(INDEX_PATH.read_text(encoding="utf-8"))
    return {"cards": [], "last_checked": None}

def save_index(index):
    INDEX_PATH.write_text(json.dumps(index, indent=2), encoding="utf-8")

def get_week_dates():
    """Get dates for the current week (Monday-Sunday)."""
    today = datetime.now()
    monday = today - timedelta(days=today.weekday())
    dates = {}
    for i, day in enumerate(['Monday', 'Tuesday', 'Wednesday', 'Thursday', 'Friday', 'Saturday', 'Sunday']):
        dates[day] = (monday + timedelta(days=i)).strftime('%Y-%m-%d')
    return dates

def create_weekly_schedule():
    """Create a weekly schedule for all Trello cards."""
    key, token = get_trello_credentials()
    
    # Get all cards
    cards = requests.get(
        f"https://api.trello.com/1/boards/6a70a3157d0db4214ac3f9a3/cards",
        params={"key": key, "token": token, "fields": "id,name,desc,idList,labels,due", "limit": 1000, "filter": "all"},
        timeout=30,
    ).json()
    
    # Group by priority
    priority_groups = {}
    for card in cards:
        # Extract priority from labels or description
        priority = None
        for label in card.get('labels', []):
            name = label['name']
            if name in ['P0', 'P1', 'P2', 'P3', 'P4', 'P5', 'P6', 'Top 10', 'Future Ideas']:
                priority = name
                break
        
        if not priority:
            # Try to extract from description
            desc = card.get('desc', '')
            if 'Priority: ' in desc:
                for line in desc.split('\n'):
                    if line.startswith('Priority: '):
                        priority = line.replace('Priority: ', '').strip()
                        break
        
        if not priority:
            priority = 'P3'  # Default
        
        priority_groups.setdefault(priority, []).append(card)
    
    # Create weekly schedule
    week_dates = get_week_dates()
    schedule = {
        "week_starting": week_dates['Monday'],
        "generated_at": datetime.now().isoformat(),
        "daily_schedule": {},
        "capacity_used": {},
        "overflow": []
    }
    
    # Initialize daily schedule
    for day in ['Monday', 'Tuesday', 'Wednesday', 'Thursday', 'Friday', 'Saturday', 'Sunday']:
        schedule["daily_schedule"][day] = []
        schedule["capacity_used"][day] = 0
    
    # Assign cards to days based on priority and capacity
    for priority, cards_list in sorted(priority_groups.items()):
        if priority not in WEEKLY_CAPACITY:
            continue
        
        allowed_days = DAY_ASSIGNMENTS.get(priority, [])
        
        if not allowed_days:
            # No weekly commitment - add to backlog
            for card in cards_list:
                schedule["overflow"].append({
                    "id": card['id'],
                    "name": card['name'],
                    "priority": priority,
                    "reason": "No weekly commitment"
                })
            continue
        
        daily_capacity = max(1, WEEKLY_CAPACITY[priority] // len(allowed_days))
        
        cards_assigned = 0
        for card in cards_list:
            if cards_assigned >= WEEKLY_CAPACITY[priority]:
                schedule["overflow"].append({
                    "id": card['id'],
                    "name": card['name'],
                    "priority": priority,
                    "reason": f"Exceeded weekly capacity of {WEEKLY_CAPACITY[priority]}"
                })
                continue
            
            # Find next available day
            assigned = False
            for day in allowed_days:
                if schedule["capacity_used"][day] < daily_capacity * 2:  # Max 2x daily capacity
                    schedule["daily_schedule"][day].append({
                        "id": card['id'],
                        "name": card['name'],
                        "priority": priority,
                        "due_date": card.get('due', ''),
                    })
                    schedule["capacity_used"][day] += 1
                    cards_assigned += 1
                    assigned = True
                    break
            
            if not assigned:
                schedule["overflow"].append({
                    "id": card['id'],
                    "name": card['name'],
                    "priority": priority,
                    "reason": "No capacity this week"
                })
    
    # Save schedule
    SCHEDULE_PATH.write_text(json.dumps(schedule, indent=2), encoding="utf-8")
    print(f"Weekly schedule created: {SCHEDULE_PATH}")
    print(f"Week starting: {schedule['week_starting']}")
    print("\nDaily breakdown:")
    for day, items in schedule["daily_schedule"].items():
        if items:
            print(f"  {day}: {len(items)} items")
            for item in items[:3]:
                print(f"    - {item['name'][:60]} [{item['priority']}]")
            if len(items) > 3:
                print(f"    ... and {len(items) - 3} more")
    
    print(f"\nOverflow items: {len(schedule['overflow'])}")
    if schedule['overflow']:
        print("  First 5 overflow items:")
        for item in schedule['overflow'][:5]:
            print(f"    - {item['name'][:60]} [{item['priority']}] - {item['reason']}")
    
    return schedule

if __name__ == "__main__":
    create_weekly_schedule()
