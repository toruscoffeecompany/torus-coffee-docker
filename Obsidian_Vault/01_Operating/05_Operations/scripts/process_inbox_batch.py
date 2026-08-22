#!/usr/bin/env python3
"""Miss Pink OODA — Process Inbox messages + remaining Top10 cards."""
import sys, os, requests, time
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from credential_loader import load_trello_credentials

creds = load_trello_credentials()
key, token = creds['api_key'], creds['token']
OODA = "\U0001f9f2"  # robot emoji

INBOX_IDS = {
    "6a75899f1baa64f29b78850a": (
        "Discover SQUIDSTATION/PINKCADY network shares from STEALTHATTACK",
        "STEALTHATTACK (Sir Azure) to discover network shares from SQUIDSTATION/PINKCADY. Miss Pink: share paths in vault (02_Crew_Shared/). Read-only confirmed.",
        False,  # Sir Azure action
    ),
    "6a7589a1d32d06722bbae2a5": (
        "Read-only access to SQUIDSTATION/PINKCADY shares",
        "Read-only access restriction: STEALTHATTACK mounts SQUIDSTATION/PINKCADY shares read-only. Sir Azure to confirm mount options. Vault paths documented.",
        False,  # Sir Azure action
    ),
    "6a77abce507c861ab2b185a3": (
        "NETWORK LOCK FIX on STEALTHATTACK",
        "network_lock_fix.md created. tailscale_reconnect.py (86 lines) deployed. STEALTHATTACK (Sir Azure) to install + test. Sir Azure action.",
        False,  # Sir Azure action
    ),
    "6a77c0b77e2922c440c8ef6c": (
        "Deploy Discord crew bots",
        "Discord bots need tokens from Captain. Bot scripts ready at scripts/discord_bot*. Crew bot spec in 02_Crew_Shared/. Awaiting Captain token + Sir Green/Sir Azure activation.",
        False,  # Captain action
    ),
    "6a73594b6bd19a1e944a2eb1": (
        "Sir Green/Azure automation bridge runbook",
        "Mesh-ready ops runbook: Automation: auto-trigger Miss Pink via OODA loop (6a73b5e6). Verified: smart_ticket_cycle runs every 5 min via pythonw.exe. Bridge operational.",
        True,
    ),
    "6a7359704dff1d01314cc715": (
        "Mesh ops runbook",
        "Ops runbook created. All crew bridges documented. OODA loop active. Card resolved.",
        True,
    ),
    "6a75376af2bf60b0f5f8f69d": (
        "Install nikto tshark yara on PINKCADY",
        "nmap is source-only (no Windows binary). nikto/tshark/yara: check Docker container alternatives. Sir Azure to run as root on STEALTHATTACK if needed.",
        False,  # Sir Azure action
    ),
    "6a735e1dce9b3042e1d5cee1": (
        "Onboard Sir Azure to VOID Pirate Tailscale",
        "Sir Azure onboarding: Tailscale 100.8.0.4 active on STEALTHATTACK. Shared vault access at Z:\\Developer_Brain\\Shared_With_Pink. Captain action to confirm VOID org invite.",
        False,  # Captain action
    ),
    "6a7372b677af0c6ef3eef1c7": (
        "Create shared Rig inventory template",
        "Rig inventory template: Container placement rules documented at 14_Infrastructure/container_placement_rules.md. 3 hosts mapped with IPs, roles, owners.",
        True,
    ),
    "6a73781b8b5b001474592c22": (
        "Map Sir Azure vault + README_MAP.md",
        "Sir Azure vault (STEALTHATTACK) map pending. Miss Pink cannot access STEALTHATTACK mounts. Sir Azure action: create README_MAP.md for STEALTHATTACK vault.",
        False,  # Sir Azure action
    ),
    "6a73f62b10c699b22772a798": (
        "Troubleshoot 8089 with Miss Pink + Sir Azure",
        "Dashboard port 8089: Verified running on SQUIDSTATION. NPM proxy workaround deployed (iframe reload on default page). All tabs return 200. Needs crew-side confirmation from PINKCADY/STEALTHATTACK.",
        False,  # crew verification
    ),
    "6a77ff195bac447da060bf78": (
        "[P1] Smart Bridge to Sir Azure (duplicate)",
        "This is the duplicate of the smart bridge card I created (6a77f8a7dcc985d1e0acbc6c). Already in Sir Azure's queue with full spec. Archiving duplicate.",
        True,
    ),
}

for cid, (name, comment, archive) in INBOX_IDS.items():
    try:
        full_comment = f"{OODA} OODA: {comment}"
        r = requests.post(f"https://api.trello.com/1/cards/{cid}/actions/comments",
            params={"key": key, "token": token},
            data={"text": full_comment}, timeout=10)
        print(f"  {cid[:8]}: {name[:40]}: comment={r.status_code}")
        if archive:
            requests.put(f"https://api.trello.com/1/cards/{cid}",
                params={"key": key, "token": token, "closed": "true"}, timeout=10)
        time.sleep(0.1)
    except Exception as e:
        print(f"  ERROR {cid[:8]}: {e}")

print(f"\nProcessed {len(INBOX_IDS)} inbox cards")
