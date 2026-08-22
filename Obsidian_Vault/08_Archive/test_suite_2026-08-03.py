#!/usr/bin/env python3
"""
Torus Coffee Automation Test Suite
Honest end-to-end test of built automations.
"""
import sys
import json
import urllib.request
import ssl
from pathlib import Path
from datetime import datetime

VAULT = Path(r"D:\Work\Torus Coffee Company LLC")
SCRIPTS = VAULT / "10_Skills_Library" / "05_Operations" / "scripts"
REPORTS = VAULT / "08_Reports"

BUFFER_KEY = None
ZAPIER_WEBHOOK = None
HUBSPOT_KEY = None
TRELLO_KEY = None
TRELLO_TOKEN = None

results = []

def record(name, passed, details=""):
    results.append({
        "test": name,
        "status": "PASS" if passed else "FAIL",
        "details": details,
        "timestamp": datetime.now().isoformat(),
    })
    icon = "✓" if passed else "✗"
    print(f"{icon} [{'PASS' if passed else 'FAIL'}] {name}: {details}")


def load_credentials():
    global BUFFER_KEY, ZAPIER_WEBHOOK, HUBSPOT_KEY, TRELLO_KEY, TRELLO_TOKEN
    try:
        sys.path.insert(0, str(SCRIPTS))
        from automation_core import get_credential

        try:
            buffer_creds = get_credential('buffer')
            BUFFER_KEY = buffer_creds.get('api_key') or buffer_creds.get('access_token')
        except Exception:
            pass

        try:
            zapier_creds = get_credential('zapier')
            ZAPIER_WEBHOOK = zapier_creds.get('webhook_url')
        except Exception:
            pass

        try:
            hubspot_creds = get_credential('hubspot')
            HUBSPOT_KEY = hubspot_creds.get('token') or hubspot_creds.get('service_key')
        except Exception:
            pass
    except Exception as e:
        print(f"Warning: core credential loader unavailable: {e}")

    trello_path = VAULT / "01_Operating" / "Operating Paperwork" / "Trello_API_Credentials.md"
    if trello_path.exists():
        lines = trello_path.read_text(errors="ignore").splitlines()
        for i, line in enumerate(lines):
            if 'API Key' in line and i + 1 < len(lines):
                TRELLO_KEY = lines[i + 1].strip().strip('`')
            elif 'Token' in line and 'OAuth' not in line and i + 1 < len(lines):
                TRELLO_TOKEN = lines[i + 1].strip().strip('`')


def test_buffer_status():
    if not BUFFER_KEY:
        record("Buffer Status", False, "Missing BUFFER_KEY")
        return [], None
    try:
        ctx = ssl.create_default_context()
        query = '{ account { id name email organizations { id name } } }'
        payload = json.dumps({"query": query}).encode()
        req = urllib.request.Request("https://api.buffer.com/graphql", data=payload, method="POST")
        req.add_header('Authorization', f'Bearer {BUFFER_KEY}')
        req.add_header('Content-Type', 'application/json')
        with urllib.request.urlopen(req, context=ctx, timeout=15) as r:
            data = json.loads(r.read())
            account = data.get('data', {}).get('account')
            if not account:
                record("Buffer Status", False, f"No account in response: {data}")
                return [], None
            orgs = account.get('organizations', [])
            org_id = orgs[0]['id'] if orgs else None
            if not org_id:
                record("Buffer Status", False, "No organization ID")
                return [], None

            channels_query = '''
            query GetChannels($organizationId: OrganizationId!) {
              channels(input: { organizationId: $organizationId }) {
                id
                service
                displayName
              }
            }
            '''
            channels_payload = json.dumps({
                "query": channels_query,
                "variables": {"organizationId": org_id},
            }).encode()
            req2 = urllib.request.Request("https://api.buffer.com/graphql", data=channels_payload, method="POST")
            req2.add_header('Authorization', f'Bearer {BUFFER_KEY}')
            req2.add_header('Content-Type', 'application/json')
            with urllib.request.urlopen(req2, context=ctx, timeout=15) as r2:
                channels_data = json.loads(r2.read())
                channels = channels_data.get('data', {}).get('channels', [])
                record("Buffer Status", True, f"Account connected, {len(channels)} channels found")
                return channels, org_id
    except Exception as e:
        record("Buffer Status", False, str(e))
        return [], None


def test_buffer_idea_creation(channels):
    if not channels:
        record("Buffer Idea Creation", False, "No channels available")
        return False
    try:
        ctx = ssl.create_default_context()
        query = '''
        mutation CreateIdea($input: CreateIdeaInput!) {
          createIdea(input: $input) {
            ... on Idea {
              id
            }
          }
        }
        '''
        payload = json.dumps({
            "query": query,
            "variables": {
                "input": {
                    "organizationId": "6a710dae3feea14b3c4acc76",
                    "content": {"text": "Test idea from Torus Coffee automation"},
                }
            }
        }).encode()
        req = urllib.request.Request("https://api.buffer.com/graphql", data=payload, method="POST")
        req.add_header('Authorization', f'Bearer {BUFFER_KEY}')
        req.add_header('Content-Type', 'application/json')
        with urllib.request.urlopen(req, context=ctx, timeout=15) as r:
            data = json.loads(r.read())
            idea = data.get('data', {}).get('createIdea')
            if idea and idea.get('id'):
                record("Buffer Idea Creation", True, f"Idea created: {idea['id']}")
                return True
            record("Buffer Idea Creation", False, f"No idea ID in response: {data}")
            return False
    except Exception as e:
        record("Buffer Idea Creation", False, str(e))
        return False


def test_zapier_webhook():
    if not ZAPIER_WEBHOOK:
        record("Zapier Webhook", False, "Missing ZAPIER_WEBHOOK")
        return False
    try:
        ctx = ssl.create_default_context()
        payload = json.dumps({
            "test": True,
            "source": "automation_test_suite",
            "timestamp": datetime.now().isoformat(),
            "message": "Torus Coffee practice test from test suite",
        }).encode()
        req = urllib.request.Request(
            ZAPIER_WEBHOOK,
            data=payload,
            headers={'Content-Type': 'application/json'},
            method='POST',
        )
        with urllib.request.urlopen(req, context=ctx, timeout=15) as r:
            record("Zapier Webhook", r.status == 200, f"HTTP {r.status}")
            return r.status == 200
    except Exception as e:
        record("Zapier Webhook", False, str(e))
        return False


def test_hubspot_contacts():
    if not HUBSPOT_KEY:
        record("HubSpot Contacts", False, "Missing HUBSPOT_KEY")
        return False
    try:
        ctx = ssl.create_default_context()
        url = "https://api.hubapi.com/crm/v3/objects/contacts?limit=1"
        req = urllib.request.Request(url, method="GET")
        req.add_header('Authorization', f'Bearer {HUBSPOT_KEY}')
        req.add_header('Content-Type', 'application/json')
        with urllib.request.urlopen(req, context=ctx, timeout=15) as r:
            data = json.loads(r.read())
            total = data.get('total', 0)
            record("HubSpot Contacts", True, f"API connected, {total} contacts found")
            return True
    except Exception as e:
        record("HubSpot Contacts", False, str(e))
        return False


def test_hubspot_deals():
    if not HUBSPOT_KEY:
        record("HubSpot Deals", False, "Missing HUBSPOT_KEY")
        return False
    try:
        ctx = ssl.create_default_context()
        url = "https://api.hubapi.com/crm/v3/objects/deals?limit=1"
        req = urllib.request.Request(url, method="GET")
        req.add_header('Authorization', f'Bearer {HUBSPOT_KEY}')
        req.add_header('Content-Type', 'application/json')
        with urllib.request.urlopen(req, context=ctx, timeout=15) as r:
            data = json.loads(r.read())
            total = data.get('total', 0)
            record("HubSpot Deals", True, f"API connected, {total} deals found")
            return True
    except Exception as e:
        record("HubSpot Deals", False, str(e))
        return False


def test_trello_connection():
    if not TRELLO_KEY or not TRELLO_TOKEN:
        record("Trello Connection", False, "Missing Trello credentials")
        return False
    try:
        ctx = ssl.create_default_context()
        url = f"https://api.trello.com/1/members/me?key={TRELLO_KEY}&token={TRELLO_TOKEN}"
        req = urllib.request.Request(url)
        with urllib.request.urlopen(req, context=ctx, timeout=15) as r:
            data = json.loads(r.read())
            username = data.get('username', 'unknown')
            record("Trello Connection", True, f"Connected as {username}")
            return True
    except Exception as e:
        record("Trello Connection", False, str(e))
        return False


def test_orchestrator():
    try:
        python_exe = VAULT / "10_Skills_Library" / "05_Operations" / "venv" / "Scripts" / "python.exe"
        result = __import__('subprocess').run(
            [str(python_exe), str(SCRIPTS / "automation_orchestrator.py"), "run"],
            capture_output=True,
            text=True,
            timeout=120,
            cwd=str(SCRIPTS),
        )
        passed = result.returncode == 0 and "8/8" in result.stdout
        record("Automation Orchestrator", passed, "8/8 scripts verified" if passed else f"Return code {result.returncode}")
        return passed
    except Exception as e:
        record("Automation Orchestrator", False, str(e))
        return False


def test_inventory_tracker():
    try:
        python_exe = VAULT / "10_Skills_Library" / "05_Operations" / "venv" / "Scripts" / "python.exe"
        result = __import__('subprocess').run(
            [str(python_exe), str(SCRIPTS / "inventory_tracker.py"), "status"],
            capture_output=True,
            text=True,
            timeout=60,
            cwd=str(SCRIPTS),
        )
        passed = result.returncode == 0 and "Inventory" in result.stdout
        record("Inventory Tracker", passed, "Status check passed" if passed else f"Return code {result.returncode}")
        return passed
    except Exception as e:
        record("Inventory Tracker", False, str(e))
        return False


def test_social_media_status():
    try:
        python_exe = VAULT / "10_Skills_Library" / "05_Operations" / "venv" / "Scripts" / "python.exe"
        result = __import__('subprocess').run(
            [str(python_exe), str(SCRIPTS / "social_media_automation.py"), "status"],
            capture_output=True,
            text=True,
            timeout=60,
            cwd=str(SCRIPTS),
        )
        passed = result.returncode == 0 and ("FACEBOOK" in result.stdout or "TWITTER" in result.stdout)
        record("Social Media Status", passed, "Platform status check passed" if passed else f"Return code {result.returncode}")
        return passed
    except Exception as e:
        record("Social Media Status", False, str(e))
        return False


def test_daily_ops():
    try:
        python_exe = VAULT / "10_Skills_Library" / "05_Operations" / "venv" / "Scripts" / "python.exe"
        result = __import__('subprocess').run(
            [str(python_exe), str(SCRIPTS / "daily_ops_automation.py"), "status"],
            capture_output=True,
            text=True,
            timeout=60,
            cwd=str(SCRIPTS),
        )
        passed = result.returncode == 0 and "Daily" in result.stdout
        record("Daily Ops Automation", passed, "Daily check passed" if passed else f"Return code {result.returncode}")
        return passed
    except Exception as e:
        record("Daily Ops Automation", False, str(e))
        return False


def run_all_tests():
    print("=" * 60)
    print("TORUS COFFEE AUTOMATION TEST SUITE")
    print("=" * 60)
    print(f"Started: {datetime.now().isoformat()}")
    print("=" * 60)
    print()

    print("--- Core Integrations ---")
    channels, org_id = test_buffer_status()
    test_buffer_idea_creation(channels)
    test_zapier_webhook()
    test_hubspot_contacts()
    test_hubspot_deals()
    test_trello_connection()

    print()
    print("--- Automation Scripts ---")
    test_orchestrator()
    test_inventory_tracker()
    test_social_media_status()
    test_daily_ops()

    print()
    print("=" * 60)
    print("TEST RESULTS SUMMARY")
    print("=" * 60)
    total = len(results)
    passed = sum(1 for r in results if r['status'] == 'PASS')
    failed = total - passed
    print(f"Total Tests: {total}")
    print(f"Passed: {passed}")
    print(f"Failed: {failed}")
    print(f"Pass Rate: {passed/total*100:.1f}%" if total > 0 else "N/A")
    print()
    print("Failed Tests:")
    for r in results:
        if r['status'] == 'FAIL':
            print(f"  ✗ {r['test']}: {r['details']}")
    print()
    print("Passed Tests:")
    for r in results:
        if r['status'] == 'PASS':
            print(f"  ✓ {r['test']}: {r['details']}")
    print("=" * 60)

    REPORTS.mkdir(exist_ok=True)
    report_path = REPORTS / f"test_report_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json"
    report_path.write_text(json.dumps({
        "timestamp": datetime.now().isoformat(),
        "total": total,
        "passed": passed,
        "failed": failed,
        "pass_rate": f"{passed/total*100:.1f}%" if total > 0 else "N/A",
        "results": results,
    }, indent=2))
    print(f"Report saved: {report_path}")
    print("=" * 60)


if __name__ == "__main__":
    load_credentials()
    run_all_tests()
