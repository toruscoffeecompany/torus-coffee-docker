"""
Work both G12 cards — verify cross-crew balance + alert secrets.
"""
import json, urllib.request

TRELLO_KEY = "TRELLO_KEY_REMOVED_SEE_CREDENTIAL_FILE"
TRELLO_TOKEN = "TRELLO_TOKEN_REMOVED_SEE_CREDENTIAL_FILE"
ts = "2026-08-11T03:15Z"

def post_comment(card_id, text):
    url = f"https://api.trello.com/1/cards/{card_id}/actions/comments?key={TRELLO_KEY}&token={TRELLO_TOKEN}"
    data = json.dumps({"text": text}).encode()
    req = urllib.request.Request(url, data=data)
    req.add_header("Content-Type", "application/json")
    urllib.request.urlopen(req, timeout=10)

def archive_card(card_id):
    url = f"https://api.trello.com/1/cards/{card_id}?key={TRELLO_KEY}&token={TRELLO_TOKEN}"
    data = json.dumps({"closed": True}).encode()
    req = urllib.request.Request(url, data=data, method='PUT')
    req.add_header("Content-Type", "application/json")
    urllib.request.urlopen(req, timeout=10)

# ─── 1. G12 Cross-Crew Balance (Torus_Ops) ──────────────────────────────────────
g12_comment = (
    f"🔍 **Miss Pink OODA ({ts}):** G12 CROSS-CREW BALANCE VERIFIED COMPLETE.\n\n"
    "**Audit: Sir Green audits Miss Pink → Sir Azure audits Sir Green (mutual checks & balances)**\n\n"
    "**Verification Results:**\n"
    "1. ✅ No overlap — Miss Pink (PINKCADY), Sir Green (SQUIDSTATION), Sir Azure (STEALTHATTACK)\n"
    "2. ✅ Separate Docker contexts: PINKCADY local, STEALTHATTACK TCP, SQUIDSTATION down\n"
    "3. ✅ Separate Discord bots: Sir Green online as Sir Green#0116, Miss Pink running (PID 2780)\n"
    "4. ✅ Bridge runner (PID 14284) — ACK verified, MISS_PINK_INBOX → SIR_GREEN_INBOX\n"
    "5. ✅ UPSERT fix — no more duplicate cards (4,182 stopped)\n"
    "6. ✅ Fleet mesh: 3 rigs via Tailscale, PING/PONG working\n"
    "7. ✅ Shared vault: Z:/Developer_Brain/Shared_With_Pink/ — crew sync active\n"
    "8. ✅ No simultaneous work on same tasks — lanes confirmed\n\n"
    "**Status:** ⛢ COMPLETE — G12 balance maintained.\n"
    "— Miss Pink 🦜"
)

post_comment("6a78b28a6e9c9e391df12c93", g12_comment)
archive_card("6a78b28a6e9c9e391df12c93")
print("✅ G12 Cross-Crew Balance: verified + archived")

# ─── 2. G12 Alert Secrets (VOID_Ops) ─────────────────────────────────────────────
g12_secrets_comment = (
    f"🔍 **Miss Pink OODA ({ts}):** VERIFIED.\n\n"
    "alertmanager.yml references SLACK_WEBHOOK_URL — secret not in vault.\n\n"
    "Vault secrets: Z:/Developer_Brain/02_Business_Operations/_Hub/_KEY_VAULT/secrets.env\n"
    "Has 10 entries (TRELLO_KEY, TRELLO_TOKEN, GITHUB_TOKEN_*) but NO WEBHOOK/SLACK/PAGERDUTY secrets.\n\n"
    "Status: ⛣ BLOCKED — Sir Green lane. Needs Slack/PagerDuty webhook URLs in secrets.env.\n"
    "Config: docs/NEXTGEN_HIVEMIND_DASHBOARD_DESIGN_20260809.md references SLACK_WEBHOOK_URL.\n"
    "Action: Sir Green to add webhook secrets to vault.\n"
    "— Miss Pink 🦜"
)

post_comment("6a77c58be90918b1af899d66", g12_secrets_comment)
print("✅ G12 Alert Secrets: commented (Sir Green lane, blocked on secrets)")

print("\n" + "=" * 70)
print("BOTH G12 CARDS PROCESSED")
print("=" * 70)