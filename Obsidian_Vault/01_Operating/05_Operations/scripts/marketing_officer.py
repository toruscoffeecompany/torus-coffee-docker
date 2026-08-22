#!/usr/bin/env python3
"""
Marketing Officer automation for Torus Coffee Company.
Social media calendar, campaign tracker, content queue.
"""
import json
from pathlib import Path
from datetime import datetime

VAULT = Path(r"D:\Work\Torus Coffee Company LLC")
MARKETING_DIR = VAULT / "06_Growth_Marketing"
CAMPAIGN_FILE = MARKETING_DIR / "campaign_queue.json"

def load_campaign_queue():
    if CAMPAIGN_FILE.exists():
        with open(CAMPAIGN_FILE, "r", encoding="utf-8") as f:
            return json.load(f)
    return {"campaigns": [], "last_updated": datetime.now().isoformat()}

def check_campaign_schedule():
    data = load_campaign_queue()
    campaigns = data.get("campaigns", [])
    today = datetime.now().date()
    
    upcoming = []
    for campaign in campaigns:
        scheduled = datetime.strptime(campaign.get("scheduled_date", "2099-01-01"), "%Y-%m-%d").date()
        if scheduled >= today:
            upcoming.append({
                "name": campaign.get("name"),
                "date": campaign.get("scheduled_date"),
                "platform": campaign.get("platform"),
                "status": campaign.get("status", "draft")
            })
    
    return upcoming

def main():
    print("=== Marketing Officer - Torus Coffee Company ===\n")
    
    upcoming = check_campaign_schedule()
    if upcoming:
        print(f"Upcoming campaigns ({len(upcoming)}):\n")
        for c in upcoming:
            print(f"  {c['date']} | {c['platform']} | {c['name']} [{c['status']}]")
    else:
        print("✓ No upcoming campaigns scheduled")
        print("  Use Marketing_Campaign_Calendar_2026_2027.md to plan content")

if __name__ == "__main__":
    main()
