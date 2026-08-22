#!/usr/bin/env python3
"""
Buffer Automation Script - Torus Coffee Company
Schedules and manages social media posts via Buffer GraphQL API.
"""
import sys
import json
import logging
from pathlib import Path
from datetime import datetime, timedelta

VAULT = Path(r"D:\Work\Torus Coffee Company LLC")
AUTOMATION_DIR = VAULT / "10_Skills_Library" / "05_Operations"
sys.path.insert(0, str(AUTOMATION_DIR / "scripts"))

from automation_core import (
    load_json, save_json, get_credential, retry,
    logger, CredentialError, AutomationError
)

BUFFER_URL = "https://api.buffer.com/graphql"
CONFIG_FILE = AUTOMATION_DIR / "scripts" / "buffer_config.json"

# Known working organization ID from API inspection
KNOWN_ORG_ID = "6a710dae3feea14b3c4acc76"


@retry(max_attempts=3, delay=2, backoff=2)
def graphql_request(query: str, variables: dict = None) -> dict:
    """
    Make a GraphQL request to Buffer API.
    
    Args:
        query: GraphQL query string
        variables: Optional variables dict
    
    Returns:
        Response data dict
    """
    api_key = get_credential('buffer', 'access_token')  # FIX: was 'api_key', credential file uses 'access_token'
    payload = {"query": query}
    if variables:
        payload["variables"] = variables
    
    import urllib.request
    data = json.dumps(payload).encode()
    req = urllib.request.Request(
        BUFFER_URL,
        data=data,
        method="POST"
    )
    req.add_header('Authorization', f'Bearer {api_key}')
    req.add_header('Content-Type', 'application/json')
    
    with urllib.request.urlopen(req, timeout=15) as r:
        response = json.loads(r.read())
        
        if 'errors' in response:
            errors = response['errors']
            error_messages = [e.get('message', str(e)) for e in errors]
            raise AutomationError(f"Buffer GraphQL errors: {', '.join(error_messages)}")
        
        return response.get('data', {})


def get_account_info() -> dict:
    """Get Buffer account information."""
    query = '{ account { id name email organizations { id name } } }'
    data = graphql_request(query)
    return data.get('account', {})


def get_channels() -> list:
    """Get connected social media channels."""
    query = '''
    query GetChannels($organizationId: OrganizationId!) {
      channels(input: { organizationId: $organizationId }) {
        id
        service
        displayName
        isDisconnected
      }
    }
    '''
    
    variables = {"organizationId": KNOWN_ORG_ID}
    data = graphql_request(query, variables)
    return data.get('channels', [])


def create_text_post(text: str, channel_id: str, scheduled_at: str = None) -> dict:
    """
    Create a text post for specified channel via Buffer GraphQL API.

    Uses the buffer.create update mutation to schedule a post.
    """
    query = """
    mutation CreateUpdate($input: CreateUpdateInput!) {
      createUpdate(input: $input) {
        id
      }
    }
    """
    variables = {
        "input": {
            "data": {
                "text": text,
            },
            "channel_ids": [channel_id],
        }
    }
    if scheduled_at:
        variables["input"]["data"]["scheduled_at"] = scheduled_at

    try:
        data = graphql_request(query, variables)
        if data.get("createUpdate"):
            logger.info(f"✓ Created Buffer post on channel {channel_id}")
            return {"status": "created", "post_id": data["createUpdate"]["id"]}
        else:
            logger.error("✗ Buffer createUpdate returned no ID")
            return {"status": "error", "error": "No post ID returned"}
    except Exception as e:
        logger.error(f"✗ Buffer post creation failed: {e}")
        return {"status": "error", "error": str(e)}


def schedule_weekly_posts() -> list:
    """Generate and schedule a week of posts."""
    channels = get_channels()
    
    if not channels:
        logger.warning("No channels connected. Connect channels in Buffer first.")
        return []
    
    channel_id = channels[0]['id']
    logger.info(f"Using channel: {channels[0]['service']} ({channels[0].get('displayName', 'N/A')})")
    
    content_plan = [
        ("Monday", "Product Highlight: Aurora Bites - Cosmic freeze-dried skittles that burst with flavor! #TorusCoffee #FreezeDried"),
        ("Wednesday", "Behind the Scenes: Ever wondered how we freeze-dry our snacks? It's like magic, but with science! #TorusCoffee"),
        ("Friday", "Weekend Market: Find us at Iowa City Farmers Market this Saturday! 8am-12pm. Bring your cosmic appetite! #FarmersMarket"),
        ("Saturday", "Customer Love: Thanks for all the love this weekend! You guys are the best. #TorusCoffee"),
    ]
    
    results = []
    base_date = datetime.now() + timedelta(days=7)
    
    for i, (day, text) in enumerate(content_plan):
        scheduled_at = (base_date + timedelta(days=i)).strftime("%Y-%m-%dT%H:%M:%SZ")
        
        try:
            post = create_text_post(text, channel_id, scheduled_at)
            results.append({
                "day": day,
                "status": post.get('status', 'pending'),
                "post_id": post.get('post_id', 'N/A')
            })
        except Exception as e:
            logger.error(f"✗ Exception scheduling {day} post: {e}")
            results.append({"day": day, "status": "error", "error": str(e)})
    
    return results


def get_status() -> dict:
    """Get Buffer integration status."""
    try:
        account = get_account_info()
        channels = get_channels()
        
        status = {
            "service": "Buffer",
            "connected": True,
            "account": account.get('name', 'N/A'),
            "email": account.get('email', 'N/A'),
            "channels_count": len(channels),
            "channels": [f"{c['service']}: {c.get('displayName', 'N/A')}" for c in channels],
            "last_check": datetime.now().isoformat()
        }
        
        print(f"\n=== BUFFER STATUS ===")
        print(f"Account: {status['account']} ({status['email']})")
        print(f"Channels: {status['channels_count']}")
        for ch in status['channels']:
            print(f"  - {ch}")
        
        return status
        
    except Exception as e:
        logger.error(f"Buffer status check failed: {e}")
        return {
            "service": "Buffer",
            "connected": False,
            "error": str(e)
        }


def main():
    """Main automation entry point."""
    logger.info("=== TORUS COFFEE BUFFER AUTOMATION ===")
    
    if len(sys.argv) > 1:
        command = sys.argv[1]
        
        if command == "status":
            get_status()
        elif command == "schedule":
            results = schedule_weekly_posts()
            print(f"\n✓ Processed {len(results)} posts")
        elif command == "channels":
            channels = get_channels()
            print(f"\nFound {len(channels)} channels:")
            for c in channels:
                print(f"  {c['service']}: {c.get('displayName', 'N/A')} ({c['id']})")
        elif command == "test":
            account = get_account_info()
            print(f"✓ Buffer connected as: {account.get('name')} ({account.get('email')})")
        else:
            print(f"Unknown command: {command}")
            print("Usage: buffer_automation.py [status|schedule|channels|test]")
    else:
        get_status()


if __name__ == "__main__":
    main()
