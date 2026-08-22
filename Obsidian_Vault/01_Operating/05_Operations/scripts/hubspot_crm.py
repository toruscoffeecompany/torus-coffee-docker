#!/usr/bin/env python3
"""
HubSpot CRM Automation Script - Torus Coffee Company
Manages contacts, deals, and companies via HubSpot REST API.
"""
import sys
import json
import logging
from pathlib import Path
from datetime import datetime

VAULT = Path(r"D:\Work\Torus Coffee Company LLC")
AUTOMATION_DIR = VAULT / "10_Skills_Library" / "05_Operations"
sys.path.insert(0, str(AUTOMATION_DIR / "scripts"))

from automation_core import (
    load_json, save_json, get_credential, retry,
    logger, CredentialError, AutomationError
)

HUBSPOT_URL = "https://api.hubapi.com/crm/v3/objects"
CONFIG_FILE = AUTOMATION_DIR / "scripts" / "hubspot_config.json"


@retry(max_attempts=3, delay=2, backoff=2)
def hubspot_request(method: str, endpoint: str, data: dict = None) -> dict:
    """
    Make a request to HubSpot REST API.
    
    Args:
        method: HTTP method (GET, POST, PATCH)
        endpoint: API endpoint (e.g., /contacts)
        data: Optional request body
    
    Returns:
        Response data dict
    """
    token = get_credential('hubspot', 'hubspot_api_key')
    if not token:
        # FIX: fallback to 'token' key for backward compatibility
        token = get_credential('hubspot', 'token')
    if not token or token.startswith("REPLACE_WITH"):
        raise CredentialError("HubSpot API key not configured. Get it from HubSpot settings → integrations")
    url = f"{HUBSPOT_URL}/{endpoint}"
    
    import urllib.request
    req_data = json.dumps(data).encode() if data else None
    req = urllib.request.Request(url, data=req_data, method=method)
    req.add_header('Authorization', f'Bearer {token}')
    req.add_header('Content-Type', 'application/json')
    
    try:
        with urllib.request.urlopen(req, timeout=15) as r:
            response = json.loads(r.read())
            return response
    except urllib.error.HTTPError as e:
        body = e.read().decode()
        raise AutomationError(f"HubSpot HTTP {e.code}: {body[:200]}")
    except Exception as e:
        raise AutomationError(f"HubSpot request failed: {e}")


def create_contact(email: str, first_name: str = None, last_name: str = None, phone: str = None) -> dict:
    """Create a contact in HubSpot."""
    properties = {"email": email}
    if first_name:
        properties["firstname"] = first_name
    if last_name:
        properties["lastname"] = last_name
    if phone:
        properties["phone"] = phone
    
    data = {"properties": properties}
    result = hubspot_request("POST", "contacts", data)
    return result.get('id', result)


def get_contacts(limit: int = 10) -> list:
    """Get contacts from HubSpot."""
    result = hubspot_request("GET", f"contacts?limit={limit}&archived=false")
    return result.get('results', [])


def create_deal(name: str, amount: float = None, stage: str = None) -> dict:
    """Create a deal in HubSpot."""
    properties = {"dealname": name}
    if amount:
        properties["amount"] = str(amount)
    if stage:
        properties["dealstage"] = stage
    
    data = {"properties": properties}
    result = hubspot_request("POST", "deals", data)
    return result.get('id', result)


def get_deals(limit: int = 10) -> list:
    """Get deals from HubSpot."""
    result = hubspot_request("GET", f"deals?limit={limit}&archived=false")
    return result.get('results', [])


def import_vault_contacts():
    """Import contacts from vault files into HubSpot.
    
    Scans vault for:
    1. Vendor_Packet_Checklist.md — vendor contact info
    2. Market_Research_Iowa_City_Area.md — vendor/market contact info
    3. Any .csv files in 02_Business_Operations with email columns
    4. Orders in 04_Products/orders.json (customer contacts)
    """
    import re as re_module
    import csv as csv_module

    imported = 0
    skipped = 0

    # FIX: Load token once at function level (was scoped inside try block)
    token = None
    try:
        token = get_credential('hubspot', 'hubspot_api_key')
    except Exception:
        token = None
    has_api = token and not token.startswith("REPLACE_WITH")

    # Pattern to match email addresses in text
    email_pattern = re_module.compile(r'[\w\.-]+@[\w\.-]+\.\w+')

    # 1. Scan markdown files for email addresses
    contact_files = [
        VAULT / "09_Projects" / "Vendor_Packet_Checklist.md",
        VAULT / "06_Growth_Marketing" / "Market_Research_Iowa_City_Area.md",
    ]

    for filepath in contact_files:
        if not filepath.exists():
            logger.info(f"Skipping {filepath.name}: not found")
            continue

        text = filepath.read_text(encoding="utf-8")
        emails = email_pattern.findall(text)
        logger.info(f"Found {len(emails)} email addresses in {filepath.name}")

        for email in emails:
            # FIX: Actually create contacts in HubSpot (dry-run if no API key)
            try:
                if has_api:
                    # Parse name from surrounding text
                    lines = text.split("\n")
                    for line in lines:
                        if email in line:
                            # Try to extract name from the line
                            name_match = re_module.search(r'([A-Z][a-z]+(?:\s+[A-Z][a-z]+)?)', line)
                            first_name = name_match.group(1).split()[0] if name_match else None
                            create_contact(email=email, first_name=first_name)
                            imported += 1
                            break
                else:
                    logger.info(f"  [DRY RUN] Would import contact: {email}")
                    imported += 1
                    skipped += 1
            except Exception as e:
                logger.warning(f"  Skipped {email}: {e}")
                skipped += 1

    # 2. Scan CSV files for contacts
    csv_files = list(VAULT.rglob("*.csv"))
    for csv_path in csv_files:
        if "vendor" in csv_path.name.lower() or "customer" in csv_path.name.lower() or "contact" in csv_path.name.lower():
            try:
                with open(csv_path, newline="", encoding="utf-8") as f:
                    reader = csv_module.DictReader(f)
                    for row in reader:
                        email = row.get("Email") or row.get("email") or row.get("Email Address")
                        if email and "@" in email:
                            first_name = row.get("First Name") or row.get("first_name")
                            last_name = row.get("Last Name") or row.get("last_name")
                            if has_api:
                                create_contact(email=email, first_name=first_name, last_name=last_name)
                            else:
                                logger.info(f"  [DRY RUN] Would import CSV contact: {email}")
                            imported += 1
            except Exception as e:
                logger.warning(f"  CSV import error for {csv_path.name}: {e}")

    # 3. Import customer contacts from recent orders
    orders_file = VAULT / "04_Products" / "orders.json"
    if orders_file.exists():
        order_data = json.loads(orders_file.read_text(encoding="utf-8"))
        for order in order_data.get("orders", []):
            cust = order.get("customer", {})
            email = cust.get("email")
            if email and "@" in email:
                if has_api:
                    create_contact(
                        email=email,
                        first_name=cust.get("name", "").split()[0] if cust.get("name") else None
                    )
                else:
                    logger.info(f"  [DRY RUN] Would import order customer: {email}")
                imported += 1

    return imported


def get_status() -> dict:
    """Get HubSpot integration status."""
    try:
        contacts = get_contacts(limit=1)
        deals = get_deals(limit=1)
        
        status = {
            "service": "HubSpot CRM",
            "connected": True,
            "contacts_count": len(contacts),
            "deals_count": len(deals),
            "last_check": datetime.now().isoformat()
        }
        
        print("\n=== HUBSPOT STATUS ===")
        print(f"Connected: True")
        print(f"Sample contacts: {len(contacts)}")
        print(f"Sample deals: {len(deals)}")
        
        return status
        
    except Exception as e:
        logger.error(f"HubSpot status check failed: {e}")
        return {
            "service": "HubSpot CRM",
            "connected": False,
            "error": str(e)
        }


def main():
    """Main automation entry point."""
    logger.info("=== TORUS COFFEE HUBSPOT CRM AUTOMATION ===")
    
    if len(sys.argv) > 1:
        command = sys.argv[1]
        
        if command == "status":
            get_status()
        elif command == "contacts":
            contacts = get_contacts()
            print(f"\nFound {len(contacts)} contacts:")
            for c in contacts:
                props = c.get('properties', {})
                print(f"  {props.get('firstname', 'N/A')} {props.get('lastname', 'N/A')} - {props.get('email', 'N/A')}")
        elif command == "deals":
            deals = get_deals()
            print(f"\nFound {len(deals)} deals:")
            for d in deals:
                props = d.get('properties', {})
                print(f"  {props.get('dealname', 'N/A')} - ${props.get('amount', '0')}")
        elif command == "import":
            count = import_vault_contacts()
            print(f"\n✓ Imported {count} contact sources")
        elif command == "test":
            status = get_status()
            if status.get('connected'):
                print("✓ HubSpot connected successfully")
            else:
                print(f"✗ HubSpot connection failed: {status.get('error')}")
        else:
            print(f"Unknown command: {command}")
            print("Usage: hubspot_crm.py [status|contacts|deals|import|test]")
    else:
        get_status()


if __name__ == "__main__":
    main()
