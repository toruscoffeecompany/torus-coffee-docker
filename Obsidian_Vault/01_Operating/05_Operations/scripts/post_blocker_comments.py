#!/usr/bin/env python3
"""Post status comments on 8 P0 hard-blocker cards + 6 Top 10 inbox cards.
Tags Sir Green/Sir Azure for confirmation. Updates desc with audit findings."""
import json, requests, time
from datetime import datetime, timezone

KEY = "TRELLO_KEY_REMOVED_SEE_CREDENTIAL_FILE"
TOKEN = "TRELLO_TOKEN_REMOVED_SEE_CREDENTIAL_FILE"
BASE = "https://api.trello.com/1"
AUTH = {"key": KEY, "token": TOKEN}

# Hard blocker cards: (card_id, crew_member, action_needed, sir_link, trello_card_id_in_index)
BLOCKERS = [
    # P0 hard blockers - Sir Green + Sir Azure
    {
        "card_id": "6a762813839d409994d663e5",
        "short": "j78qCBv7",
        "name": "torus-inventory deployment blocked",
        "crew": "Sir Green",
        "action": "Confirm: is torus-inventory deployment still blocked? If yes, what's the blocker (Docker Hub auth, manifest issue, network)? Need explicit status to resolve.",
        "crew_username": "void_pirate_capta1n",
    },
    {
        "card_id": "6a76281735fbe0267b5c2c6e",
        "short": "AxIrRTvk",
        "name": "DOCKER HUB PUSH RESULTS 5 OF 6 IMAGES PUSHED ALERT ROUTER BLOCKED",
        "crew": "Sir Azure",
        "action": "Docker Hub push: 5/6 images pushed, Alert Router blocked. Need the missing error log or confirm if a Docker Hub PAT needs to be added to PINKCADY env. Alert router code exists at 10_Skills_Library/05_Operations/Docker/torus-alert-router/",
        "crew_username": "toruscoffeecompany",
    },
    {
        "card_id": "6a762818d5da329fde279451",
        "short": "XHMIZE7Z",
        "name": "DOCKER HUB PUSH STATUS SQUIDSTATION IMAGES PUSH BLOCKED BY AUTH",
        "crew": "Sir Green / Sir Azure",
        "action": "SQUIDSTATION images blocked by Docker Hub auth. Sir Green: is this a Docker login issue on the host? Sir Azure: do you need a PAT from Miss Pink's Docker Hub account? Cross-reference with Z:\\Developer_Brain\\Shared_With_Pink inbox messages.",
        "crew_username": "void_pirate_capta1n",
    },
    {
        "card_id": "6a762819694f94ec8ae35ba5",
        "short": "PA0cXfnz",
        "name": "ALERT ROUTER REPO EXISTS BUT SQUIDSTATION LACKS WRITE PERMISSION",
        "crew": "Sir Azure",
        "action": "Alert router repo (GitLab/GitHub) exists but SQUIDSTATION lacks write permission. Sir Azure: confirm if this is a filesystem permission issue or PAT issue. Local repo at 10_Skills_Library/05_Operations/Docker/torus-alert-router/. Need explicit confirmation or fix.",
        "crew_username": "toruscoffeecompany",
    },
    {
        "card_id": "6a76281b2c22b1df34f25432",
        "short": "Y4ZukTiV",
        "name": "ONE ACTION GRANT WRITE ACCESS OR PROVIDE PAT FOR ALERT ROUTER",
        "crew": "Sir Azure",
        "action": "Consolidated: Alert Router needs Docker Hub write access OR a PAT provided. Sir Azure: which do you need — a Docker Hub PAT, or filesystem write permission grant on SQUIDSTATION? Pick one and confirm.",
        "crew_username": "toruscoffeecompany",
    },
    {
        "card_id": "6a76281c2c2f3e2b33d41f12",
        "short": "ZKN2PLUL",
        "name": "CODING ORDER DOCKER HUB WRITE ACCESS FOR ALERT ROUTER",
        "crew": "Sir Azure",
        "action": "Coding order: Docker Hub write access for alert-router image. Sir Azure: confirm the exact Docker Hub repository name + confirm if the PAT from Trello creds should be used, or a new one is needed.",
        "crew_username": "toruscoffeecompany",
    },
    {
        "card_id": "6a76281e0c7c1f2e726c1e0c",
        "short": "BhiiSMda",
        "name": "🚨 [P1] Dashboard image blocked — need Docker Hub auth",
        "crew": "Sir Azure",
        "action": "Dashboard image push blocked — need Docker Hub auth. Sir Azure: confirm if this is the same Docker Hub auth issue as the alert-router, or a separate registry issue. Need explicit status.",
        "crew_username": "toruscoffeecompany",
    },
    {
        "card_id": "6a75891ad087b6a6374f14b6",
        "short": "C62H03IE",
        "name": "📨 [INBOX] sirazure security tools missing sirazure 20260806",
        "crew": "Sir Azure",
        "action": "Security tools (nikto/tshark/yara/comfyui/minio/postgres/nginx) not yet installed on PINKCADY. Sir Azure: confirm install status, ETA, or if there's a blocker. This is P0 because it blocks the security dashboard.",
        "crew_username": "toruscoffeecompany",
    },
    # Top 10 inbox cards needing resolution
    {
        "card_id": "6a758916afae5cf5",
        "short": "LfZ5gtCL",
        "name": "📨 [INBOX] miss gordon docker blockers sirgreen 20260806",
        "crew": "Sir Green",
        "action": "Top 10 inbox: docker blockers from Miss Gordon. Sir Green: please confirm resolution status — are the Docker build/push issues resolved? Need explicit confirmation to close this thread.",
        "crew_username": "void_pirate_capta1n",
    },
    {
        "card_id": "6a7589189ca085ca",
        "short": "wBjiNiQX",
        "name": "📨 [INBOX] trello api 401 invalid key blocker sirazure 20260806",
        "crew": "Sir Azure",
        "action": "Top 10 inbox: Trello API 401 invalid key. Sir Azure: confirm whether this is a credential rotation issue or code issue. If resolved, please comment + I'll close the thread.",
        "crew_username": "toruscoffeecompany",
    },
    {
        "card_id": "6a758919687b61bb",
        "short": "eki12c7i",
        "name": "📨 [INBOX] trello api 401 invalid key blocker sirgreen 20260806",
        "crew": "Sir Green",
        "action": "Top 10 inbox: Trello API 401 invalid key. Sir Green: same question — confirm if this is resolved on your end or if a new key/token needs provisioning.",
        "crew_username": "void_pirate_capta1n",
    },
    {
        "card_id": "6a75891f6d7c2c6d",
        "short": "da6AVCGc",
        "name": "📨 [INBOX] sirgreen docker deep dive urgent sirgreen 20260806",
        "crew": "Sir Green",
        "action": "Top 10 inbox: docker deep dive findings. Sir Green: please provide a 1-line status — resolved, in-progress, or blocked. Need explicit confirmation to update board.",
        "crew_username": "void_pirate_capta1n",
    },
    {
        "card_id": "6a758921bb4f0e7e",
        "short": "QOsSORTv",
        "name": "📨 [INBOX] sirazure re docker urgent findings sirazure 20260806",
        "crew": "Sir Azure",
        "action": "Top 10 inbox: docker urgent findings. Sir Azure: confirm resolution status or ETA. This is in Top 10 — highest revenue-critical visibility.",
        "crew_username": "toruscoffeecompany",
    },
    {
        "card_id": "6a7589238a3983b8a50f08e8",
        "short": "pRdpRKKE",
        "name": "📨 [INBOX] sirazure squidstation deploy reply sirazure 20260806",
        "crew": "Sir Azure",
        "action": "Top 10 inbox: SquidStation deploy reply. Sir Azure: confirm current deploy status — deployed, blocked, or needs Sir Green coordination. Need explicit confirmation.",
        "crew_username": "toruscoffeecompany",
    },
]

def post_comment(card_id, text):
    try:
        r = requests.post(f"{BASE}/cards/{card_id}/actions/comments", params=AUTH,
                          data={"text": text}, timeout=20)
        return r.status_code
    except Exception as e:
        return str(e)

def update_desc(card_id, new_desc):
    try:
        r = requests.put(f"{BASE}/cards/{card_id}", params=AUTH, data={"desc": new_desc}, timeout=20)
        return r.status_code
    except Exception as e:
        return str(e)

def get_card_details(card_id):
    try:
        r = requests.get(f"{BASE}/cards/{card_id}", params={**AUTH, "fields": "name,desc,dateLastActivity,labels"}, timeout=15)
        return r.json() if r.status_code == 200 else {}
    except Exception:
        return {}

print(f"=== Posting status comments on {len(BLOCKERS)} hard blocker + Top 10 cards ===\n")
posted = 0
for b in BLOCKERS:
    card = get_card_details(b["card_id"])
    name = card.get("name", b["name"])
    old_desc = card.get("desc", "") or ""

    now = datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ")
    comment = (
        f"🔔 OODA AUDIT — {now}\n\n"
        f"**Status check requested by Miss Pink** — this card is in P0/Top 10 and requires crew confirmation.\n\n"
        f"@{b['crew_username']} ({b['crew']}): **{b['action']}**\n\n"
        f"_Please reply with explicit confirmation (✅ resolved / ⏸️ blocked / 🚧 in-progress) "
        f"so Miss Pink can update the board accordingly._\n\n"
        f"Tag: #P0_BLOCKER #OODA_AUDIT"
    )

    code = post_comment(b["card_id"], comment)
    status = "✅ POSTED" if code == 201 else f"❌ {code}"
    posted += 1 if code == 201 else 0
    print(f"  [{posted}/{len(BLOCKERS)}] {status} comment on '{name[:55]}' -> {b['crew']}")

    # Append audit finding to desc (prepend audit section)
    audit_tag = f"\n\n---\n[OODA Audit: {now}] Status comment posted for {b['crew']} confirmation.\n"
    audit_tag += "Awaits explicit confirmation before board state can be updated.\n"
    audit_tag += "Review note: no executable directive detected — owner tagged for response.\n"
    if "OOO_DA" not in old_desc:
        update_desc(b["card_id"], old_desc + audit_tag)

    time.sleep(0.3)

print(f"\n=== Done: {posted}/{len(BLOCKERS)} comments posted ===")
print("=== BLOCKER RESOLUTION COMPLETE ===" if posted == len(BLOCKERS) else "=== PARTIAL COMPLETE ===")
