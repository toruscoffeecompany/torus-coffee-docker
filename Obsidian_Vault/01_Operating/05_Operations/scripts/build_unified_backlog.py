#!/usr/bin/env python3
"""
Torus Coffee Company — Unified OODA Backlog Builder
Reads live Trello boards and writes Unified_OODA_Backlog_2026-08-04.md.
"""
import importlib.util
import json
from pathlib import Path
from datetime import datetime, timezone

VAULT = Path(r"D:\Work\Torus Coffee Company LLC")
OUTBOX = VAULT / "02_Business_Operations/Communications/Outbox"
BACKLOG = VAULT / "08_Reports/Unified_OODA_Backlog_2026-08-04.md"
TRELLO_SYNC = VAULT / "10_Skills_Library/05_Operations/scripts/trello_sync.py"


def now_iso() -> str:
    return datetime.now(timezone.utc).isoformat()


def load_trello_sync():
    """Load trello_sync module to reuse credentials/API helpers."""
    import sys

    scripts_dir = TRELLO_SYNC.parent.resolve()
    if str(scripts_dir) not in sys.path:
        sys.path.append(str(scripts_dir))
    spec = importlib.util.spec_from_file_location("trello_sync", TRELLO_SYNC)
    mod = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(mod)
    return mod


def fetch_cards_for_board(sync_mod, board_name, board_id):
    """Fetch all cards for a board grouped by list."""
    lists = sync_mod.api(
        "GET",
        f"https://api.trello.com/1/boards/{board_id}/lists?key={sync_mod.API_KEY}&token={sync_mod.TOKEN}&fields=name,id",
    )
    cards = sync_mod.api(
        "GET",
        f"https://api.trello.com/1/boards/{board_id}/cards?key={sync_mod.API_KEY}&token={sync_mod.TOKEN}&fields=name,idList,desc,dateLastActivity,labels",
    )
    list_map = {l["id"]: l["name"] for l in lists}
    grouped = {name: [] for name in ["Backlog", "To_Do", "In_Progress", "Review", "Done"]}
    for card in cards:
        list_name = list_map.get(card.get("idList"), "Backlog")
        grouped.setdefault(list_name, []).append(card)
    return grouped


def build_backlog(sync_mod):
    """Build unified backlog from all Trello boards."""
    boards = {
        "Torus_Ops": ("Torus_Ops", "6a70a3157d0db4214ac3f9a3"),
        "Business_Docs": ("Business_Docs", "6a70a3152b3a1f6dca3fa08c"),
        "Website_Rebuild": ("Website_Rebuild", "6a70a316f884c39f2dc5e6a6"),
    }

    lines = [
        "# Torus Coffee Company — Unified OODA Backlog",
        "",
        f"**Date:** {datetime.now().strftime('%Y-%m-%d')}  ",
        "**Owner:** Miss Pink  ",
        "**Status:** Active — Trello-backed",
        "",
        "## Source of Truth",
        "",
        "- **Trello Boards:** Torus Ops / Website Rebuild / Business Docs",
        "- **Local Backup:** `08_Reports/Master_OODA_Execution_Tasklist_2026-08-04.md`",
        "",
        "---",
        "",
        "## P0 — Revenue Launch",
        "",
        "- `🚫` Square payment links — Captain must create in Square dashboard",
        "- `🚫` Social accounts — Substack, YouTube, Discord",
        "- `🚫` Live alerts — Discord webhook, Gmail app password",
        "- `🔄` Contact/wholesale inquiry flow backend",
        "",
        "## P1 — Full Stack Build",
        "",
        "- `✅` Minimal FastAPI scaffold: products, orders, customers, admin",
        "- `⏳` Connect website to API layer",
        "- `⏳` Customer account system",
        "- `⏳` Inventory admin dashboard",
        "- `⏳` Order management system",
        "- `⏳` Automated tax filing",
        "- `⏳` Automated backup system",
        "- `⏳` Zapier Zaps for social/email/CRM",
        "",
        "## P2 — Scale",
        "",
        "- `⏳` Substack newsletter",
        "- `⏳` YouTube channel automation",
        "- `⏳` Discord community automation",
        "- `⏳` SEO/social auto-posting",
        "- `⏳` Product review system",
        "- `⏳` Referral/affiliate tracking",
        "- `⏳` Gift cards/subscriptions",
        "- `⏳` 50+ SKU inventory",
        "",
        "## P3 — Local Network Monitoring & Dashboard",
        "",
        "- `⏳` Deploy dashboard_server.py on SQUIDSTATION",
        "- `⏳` Connect PINKCADY watcher stats",
        "- `⏳` Local network defense/monitoring tools",
        "- `⏳` Crew Discord bot activation",
        "",
        "## P4 — Crew Personas",
        "",
        "- `⏳` Accountant persona script",
        "- `⏳` Tax preparer persona script",
        "- `⏳` Lawyer/compliance persona script",
        "- `⏳` Strategy officer persona script",
        "- `⏳` Ops officer persona script",
        "- `⏳` Marketing officer persona script",
        "- `⏳` Inventory manager persona script",
        "- `⏳` Order manager persona script",
        "",
        "---",
        "",
        "## Live Trello Card Counts",
        "",
        f"**Generated:** {now_iso()}",
        "",
    ]

    for name, (display_name, board_id) in boards.items():
        try:
            grouped = fetch_cards_for_board(sync_mod, display_name, board_id)
            total = sum(len(v) for v in grouped.values())
            lines.append(f"### {display_name}")
            lines.append("")
            lines.append(f"| List | Count |")
            lines.append(f"|------|-------|")
            for list_name in ["Backlog", "To_Do", "In_Progress", "Review", "Done"]:
                count = len(grouped.get(list_name, []))
                lines.append(f"| {list_name} | {count} |")
            lines.append("")
            lines.append(f"**Total:** {total}")
            lines.append("")
        except Exception as e:
            lines.append(f"### {display_name}")
            lines.append("")
            lines.append(f"**Error:** {e}")
            lines.append("")

    lines.extend(
        [
            "---",
            "",
            "## Blockers & Human Actions Required",
            "",
            "| Blocker | Required By | Notes |",
            "|---------|-------------|-------|",
            "| Discord webhook | Captain | Create in `#torus-coffee`, store via secure handoff |",
            "| Gmail app password | Captain | Generate in Google Account security settings |",
            "| Backup path | Captain | Confirm `D:/backups` or `Z:/backups` |",
            "| Vercel login | Captain | Run `vercel login` or provide token |",
            "| Supabase decision | Captain + owner | Vercel account approval, Supabase start decision |",
            "| Square links | Captain | Create payment links in Square dashboard |",
            "| GitHub auth | Captain | Provide GitHub API token for issue sync |",
            "",
            "---",
            "",
            "## Evidence",
            "",
            "- `08_Reports/Master_OODA_Execution_Tasklist_2026-08-04.md`",
            "- `08_Reports/automation_verification_2026-08-04.md`",
            "- `09_Projects/Full_Automation_Build_List.md`",
            "- `09_Projects/Full_Scope_Automation_Build_Plan.md`",
            "- `09_Projects/Pre_Website_Automation_Checklist.md`",
            "",
        ]
    )

    return "\n".join(lines)


def main():
    sync_mod = load_trello_sync()
    backlog = build_backlog(sync_mod)
    BACKLOG.write_text(backlog, encoding="utf-8")
    print(f"✓ Wrote unified backlog: {BACKLOG}")

    ts = datetime.now(timezone.utc).strftime("%Y%m%dT%H%M%SZ")
    out_path = OUTBOX / f"{ts}_trello_sync_unified_backlog.msg.md"
    out_path.write_text(backlog, encoding="utf-8")
    print(f"✓ Mirrored to outbox: {out_path}")


if __name__ == "__main__":
    main()
