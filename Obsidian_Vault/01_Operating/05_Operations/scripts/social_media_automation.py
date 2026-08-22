#!/usr/bin/env python3
"""
Social Media Automation Script - Torus Coffee Company
Schedules and manages social media posts across platforms.
"""
import os
import json
import sys
from datetime import datetime, timedelta
from pathlib import Path

VAULT = Path(r"D:\Work\Torus Coffee Company LLC")
SOCIAL_DIR = VAULT / "06_Growth_Marketing" / "Social_Media"
CONFIG_FILE = VAULT / "10_Skills_Library" / "05_Operations" / "scripts" / "social_media_config.json"

def load_config():
    """Load social media configuration."""
    if CONFIG_FILE.exists():
        with open(CONFIG_FILE, 'r') as f:
            return json.load(f)
    return {
        "platforms": {
            "facebook": {"enabled": True, "page_id": "61577390931175"},
            "twitter": {"enabled": True, "handle": "@TorusCoffee"},
            "youtube": {"enabled": True, "handle": "@TorusCoffeeCompany"},
            "instagram": {"enabled": False, "handle": "@glvwriter"},
            "pinterest": {"enabled": False, "handle": "@toruscoffeecompany"},
            "tiktok": {"enabled": False, "handle": "@toruscoffeecompany"},
            "linkedin": {"enabled": False, "company": "Torus Coffee Company LLC"}
        },
        "posting_schedule": {
            "monday": ["facebook", "twitter", "instagram"],
            "wednesday": ["facebook", "twitter", "pinterest"],
            "friday": ["facebook", "twitter", "instagram", "tiktok"],
            "saturday": ["facebook", "instagram"]
        },
        "content_calendar": [],
        "last_run": None,
        "auto_send_enabled": True  # FIX: default to True so Zapier delivery works
    }

def save_config(config):
    """Save social media configuration."""
    CONFIG_FILE.parent.mkdir(parents=True, exist_ok=True)
    with open(CONFIG_FILE, 'w') as f:
        json.dump(config, f, indent=2)
    print(f"✓ Saved config to {CONFIG_FILE}")

def generate_weekly_content():
    """Generate a week of social media content from vault assets."""
    config = load_config()
    
    # Content templates based on vault assets
    content_templates = [
        {
            "day": "Monday",
            "platforms": ["facebook", "twitter", "instagram"],
            "type": "product_highlight",
            "title": "Product of the Week",
            "body": "This week's spotlight: {product_name} - {product_desc}",
            "hashtags": ["#TorusCoffee", "#FreezeDried", "#IowaCity", "#FreezeDriedSnacks"]
        },
        {
            "day": "Wednesday",
            "platforms": ["facebook", "twitter", "pinterest"],
            "type": "behind_scenes",
            "title": "Behind the Scenes",
            "body": "Ever wondered how we make our freeze-dried snacks? Here's a peek!",
            "hashtags": ["#TorusCoffee", "#BehindTheScenes", "#SmallBusiness"]
        },
        {
            "day": "Friday",
            "platforms": ["facebook", "twitter", "instagram", "tiktok"],
            "type": "market_announcement",
            "title": "Weekend Market Schedule",
            "body": "Find us this weekend at {market_location}!",
            "hashtags": ["#TorusCoffee", "#FarmersMarket", "#IowaCity", "#WeekendVibes"]
        },
        {
            "day": "Saturday",
            "platforms": ["facebook", "instagram"],
            "type": "customer_spotlight",
            "title": "Customer Love",
            "body": "Shoutout to our amazing customers!",
            "hashtags": ["#TorusCoffee", "#CustomerLove", "#FreezeDried"]
        }
    ]
    
    return content_templates

def create_content_calendar():
    """Create a weekly content calendar."""
    config = load_config()
    content = generate_weekly_content()
    
    calendar = []
    today = datetime.now()
    
    for item in content:
        post_date = today + timedelta(days=7)  # Next week
        post = {
            "date": post_date.strftime("%Y-%m-%d"),
            "day": item["day"],
            "platforms": item["platforms"],
            "type": item["type"],
            "title": item["title"],
            "body": item["body"],
            "hashtags": item["hashtags"],
            "status": "draft",
            "created_at": datetime.now().isoformat()
        }
        calendar.append(post)
    
    config["content_calendar"] = calendar
    config["last_run"] = datetime.now().isoformat()
    save_config(config)
    
    print(f"✓ Created {len(calendar)} content items for next week")
    return calendar

def get_platform_status():
    """Get status of all social platforms."""
    config = load_config()
    print("\n=== SOCIAL MEDIA PLATFORM STATUS ===\n")
    
    for platform, settings in config["platforms"].items():
        status = "✅ Active" if settings.get("enabled") else "❌ Inactive"
        handle = settings.get("handle", settings.get("company", "N/A"))
        print(f"{platform.upper():12} {status:15} {handle}")
    
    return config["platforms"]

def generate_post_report():
    """Generate a report of scheduled posts."""
    config = load_config()
    calendar = config.get("content_calendar", [])
    
    print("\n=== CONTENT CALENDAR REPORT ===\n")
    print(f"Total posts scheduled: {len(calendar)}")
    
    for post in calendar:
        platforms = ", ".join(post["platforms"])
        print(f"\n📅 {post['date']} ({post['day']})")
        print(f"   Title: {post['title']}")
        print(f"   Type: {post['type']}")
        print(f"   Platforms: {platforms}")
        print(f"   Status: {post['status']}")
    
    return calendar

def main():
    """Main automation entry point."""
    print("=== TORUS COFFEE SOCIAL MEDIA AUTOMATION ===\n")
    
    if len(sys.argv) > 1:
        command = sys.argv[1]
        
        if command == "status":
            get_platform_status()
        elif command == "calendar":
            create_content_calendar()
        elif command == "report":
            generate_post_report()
        elif command == "init":
            config = load_config()
            save_config(config)
            print("✓ Social media automation initialized")
        else:
            print(f"Unknown command: {command}")
            print("Usage: social_media_automation.py [status|calendar|report|init]")
    else:
        # Default: show status and generate calendar
        get_platform_status()
        create_content_calendar()
        generate_post_report()

if __name__ == "__main__":
    main()
