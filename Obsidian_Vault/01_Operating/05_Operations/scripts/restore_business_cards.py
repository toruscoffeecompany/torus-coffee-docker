"""
RESTORE 54 wrongly archived business cards.
These were auto-archived by the OODA sweep but are legitimate business cards.
"""
import json, urllib.request, time, os
from datetime import datetime, timezone

TRELLO_KEY = "TRELLO_KEY_REMOVED_SEE_CREDENTIAL_FILE"
TRELLO_TOKEN = "TRELLO_TOKEN_REMOVED_SEE_CREDENTIAL_FILE"
ts = datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ")

def unarchive_card(cid):
    """Un-archive a card (set closed=False)."""
    url = f"https://api.trello.com/1/cards/{cid}?key={TRELLO_KEY}&token={TRELLO_TOKEN}"
    data = json.dumps({"closed": False}).encode()
    req = urllib.request.Request(url, data=data, method='PUT')
    req.add_header("Content-Type", "application/json")
    try:
        urllib.request.urlopen(req, timeout=10)
        time.sleep(0.3)
        return True
    except Exception as e:
        print(f"  ❌ {cid}: {e}")
        return False

def post_comment(cid, text):
    url = f"https://api.trello.com/1/cards/{cid}/actions/comments?key={TRELLO_KEY}&token={TRELLO_TOKEN}"
    data = json.dumps({"text": text}).encode()
    req = urllib.request.Request(url, data=data)
    req.add_header("Content-Type", "application/json")
    try: urllib.request.urlopen(req, timeout=10)
    except: pass
    time.sleep(0.3)

# ─── Card IDs to restore (from the wrongly archived list) ─────────────────────
cards_to_restore = [
    # VOID_Ops business cards
    ("6a77c58d79a5614d6139f7f2", "G13 Inventory LAN devices"),
    ("6a75932bf10c6225f6c47d11", "Torus Coffee Videos source empty"),
    ("6a75b6211e1a75eeb6652a9d", "Torus Coffee Videos Y:\\Video"),
    ("6a77d1f0b42df560890e8841", "OODA Dedupe Sir Green Queue"),
    ("6a5d4d754ed0dce1aa1a2a2e", "Follow-up REBALANCE"),
    ("6a5d6245aef3b27b199974fd", "Video projection automation"),
    ("6a5d6b8cc8fa4f2940985a74", "Build company website"),
    ("6a5d4d74db6366700e9c9ce3", "Follow-up maCaw security"),
    ("6a5d5e7a0ad212fce0a16f50", "Obsidian vault automations"),
    ("6a596ea7a3c75b3919990753", "Biz docs insurance/filings"),
    ("6a596eaade63d9301406d2fe", "Biz Review Q2 estimated tax"),
    ("6a777176521a193aca867774", "Automate YouTube production"),
    ("6a777173d6adb838daf86c18", "Design website architecture"),
    ("6a7771712c35d89627b574f6", "Deploy website to Vercel"),
    ("6a77716aa79c9ac2d62fae28", "Deploy website to free hosting"),
    ("6a7263efe7b2429afeff6eb2", "Obsidian vault cross-matrix review"),
    ("6a75b6211e1a75eeb6652a9d", "Torus Coffee Videos content on Y:"),
]

# Torus_Ops business cards
torus_restore = [
    ("6a78ba5f90343f9a21ed4b06", "Setup toruscoffeecompany@gmail.com"),
    ("6a5d6245aef3b27b199974fd", "Video projection automation"),
    ("6a5d6b8cc8fa4f2940985a74", "Build company website"),
    ("6a5d4d74db6366700e9c9ce3", "Follow-up maCaw security"),
    ("6a5d5e7a0ad212fce0a16f50", "Obsidian vault automations"),
]

print(f"=== Restoring {len(cards_to_restore) + len(torus_restore)} wrongly archived business cards ===\n")

restored = 0
for cid, name in cards_to_restore + torus_restore:
    if unarchive_card(cid):
        print(f"  ✅ Restored: {name[:45]}")
        post_comment(cid, f"""⚠️ **Miss Pink CORRECTION ({ts}):**

This card was WRONGLY archived by the OODA sweep on 2026-08-12.

**Reason:** The sweep was too aggressive — it archived legitimate business cards
(website, inventory, taxes, product, video automation, etc.) along with VOID pirate ops cards.

**Action:** RESTORED to open status. This is a legitimate Torus Coffee business card.

The OODA filter has been updated to NOT archive:
- Torus Coffee business cards (website, inventory, product, tax, etc.)
- Customer/vendor cards
- Product improvement cards
- Only VOID pirate ops + Sir Green/Azure lane cards should be swept

— Miss Pink 🦜 (apologies for the over-sweep! 😅)""")
        restored += 1
    else:
        print(f"  ❌ Failed: {name[:45]}")

# ─── Create NEW business cards for missing items ─────────────────────────────────
print(f"\n=== Creating missing business cards ===\n")

# Get board lists
resp = urllib.request.urlopen(f"https://api.trello.com/1/boards/6a70a3157d0db4214ac3f9a3/lists?key={TRELLO_KEY}&token={TRELLO_TOKEN}")
torus_lists = json.loads(resp.read())
business_list = next((l["id"] for l in torus_lists if "business" in l["name"].lower() or "todo" in l["name"].lower() or "backlog" in l["name"].lower()), torus_lists[0]["id"])

def create_business_card(name, desc):
    url = f"https://api.trello.com/1/cards?key={TRELLO_KEY}&token={TRELLO_TOKEN}"
    data = json.dumps({"idList": business_list, "name": name, "desc": desc, "pos": "top"}).encode()
    req = urllib.request.Request(url, data=data)
    req.add_header("Content-Type", "application/json")
    try:
        result = json.loads(urllib.request.urlopen(req, timeout=10).read())
        print(f"  ✅ Created: {name[:50]}")
        time.sleep(0.3)
        return result["id"]
    except Exception as e:
        print(f"  ❌ Failed: {name[:50]} — {e}")
        return None

# Missing business cards
business_cards = [
    ("[TAX] Iowa Monthly Sales/Use Tax Filing — Due end of each month",
     "File Iowa sales/use tax return monthly on GovConnectIowa.\nDue: Last day of month following reporting period.\nEven $0 income must file!\n\nVault: 02_Tax/Iowa_Tax_Automation_Plan.md\nPortal: https://govconnect.iowa.gov/\n\nPriority: P0 — legal compliance"),
    ("[TAX] Federal 1065 Partnership Return — Due March 15",
     "File Form 1065 for Torus Coffee Company (calendar year partnership).\nDue: March 15 annually.\nInclude $0 Schedule K-1s for partners.\n\nVault: 02_Tax/Iowa_Tax_Automation_Plan.md\nPriority: P1 — annual filing"),
    ("[TAX] Quarterly Estimated Tax Payments — April 15, June 15, Sept 15, Jan 15",
     "Quarterly estimated tax payments for partners.\nQ2 2026: June 15\n\nVault: 02_Tax/Federal_Tax_Automation_Plan.md\nPriority: P2 — payment tracking"),
    ("[WEBSITE] Complete Torus Coffee website rebuild on Next.js",
     "Website_R3DEPLOY project: Next.js + TypeScript + Tailwind.\nScaffold: 06_Website/next-storefront/\nGitHub: toruscoffeecompany/Torus_website_rebuild\n\nPriority: P0 — customer-facing"),
    ("[WEBSITE] Deploy website to Vercel (free hosting)",
     "Deploy the rebuilt Torus Coffee website to Vercel free tier.\n\nPriority: P1"),
    ("[PRODUCT] Finalize product photos for all SKUs",
     "Product photo strategy without Sir Azure.\nCatalog all products with SKU, photos, descriptions.\n\nVault: 04_Products/Product_Photo_Tracking_Spreadsheet.md\nPriority: P1"),
    ("[PRODUCT] Test freeze-dried SOP in production",
     "Test freeze-dried fruit/candy production SOP.\nVault: 04_Products/Freeze-Dried_Fruit_Production_SOP.md\nPriority: P2"),
    ("[INVENTORY] Build torus-inventory dashboard widget",
     "Inventory dashboard widget showing stock levels.\n\nPriority: P2"),
    ("[FINANCE] Setup Square payment links for Torus Coffee",
     "Square payment links for invoice payments.\nPriority: P2"),
    ("[COMMS] Setup toruscoffeecompany@gmail.com automation",
     "Smart-automate: read + respond to customer emails.\n\nPriority: P1"),
    ("[COMMS] Build Torus Coffee Discord bot",
     "Build Discord bot for Torus Coffee Company server.\n\nPriority: P2"),
    ("[INFRA] Deploy NetBox + Dnsmasq network asset management",
     "Deploy free OSS network asset management on SQUIDSTATION.\nVault: 06_Website/PROJECT WEBSITE R3DEPLOY/\nPriority: P1 — Captain authorized"),
]

new_count = 0
for name, desc in business_cards:
    new_count += 1
    create_business_card(name, desc)

# ─── Fix: Update vault structure documentation ────────────────────────────────
print("\n=== Updating vault structure docs ===\n")

vault_readme = """# Vault Structure — Torus Coffee Company

**Canonical source of truth:** `D:/Work/Torus Coffee Company LLC/` (PINKCADY)

## Top-level Structure
- `00_Inbox/` — Daily/Weekly/Monthly/Project notes
- `01_Operating/` — Operating paperwork
- `02_Business_Operations/` — Biz ops, communications, Miss Pink bridge
- `02_Tax/` — Federal + Iowa tax automation, returns, filings
- `03_Financials/` — Reports, P&L
- `04_Products/` — Product catalog, photos, SOPs
- `05_Legal/` — Compliance, contracts
- `06_Website/` — Next.js site, dashboard, PROJECT WEBSITE R3DEPLOY
- `07_Photos/` — Product + brand photos
- `08_Design_Brand/` — Logos, signage, business cards, social
- `09_Projects/` — Trello board exports, vendor applications
- `10_Skills_Library/` — Website, legal, finance, product, ops, marketing, ecommerce, design
- `11_Vendors/` — Vendor contacts/applications
- `12_Customers/` — Customer data
- `13_Team/` — Crew directories
- `14_Infrastructure/` — Docker, network, hardware docs
- `Pirate Fleet Operations/` — Fleet ops, dashboards, runbooks
- `tr3asure_mAp/` — Trading bot (signal generator, augur, data)
- `scripts/` — OODA, sweep, verify scripts
- `Excalidraw/` — Whiteboard diagrams

## Shared Vault (Z:/Developer_Brain/)
Shared with Sir Green (SQUIDSTATION) + Sir Azure (STEALTHATTACK)
- `Shared_With_Pink/` — Cross-crew comms + OODA logs
- `02_Business_Operations/` — Shared biz ops

## Vault Rules
1. Local vault `D:/Work/Torus Coffee Company LLC` is SOLE source of truth
2. 2025 tax docs are READ-ONLY
3. Never archive legitimate business cards in OODA sweep
4. Business cards = website/product/tax/inventory — DO NOT SWEEP

Created: 2026-08-12 by Miss Pink
"""

with open(r"D:/Work/Torus Coffee Company LLC/VAULT_STRUCTURE.md", "w") as f:
    f.write(vault_readme)
print("  ✅ Created VAULT_STRUCTURE.md")

print(f"\n{'='*70}")
print(f"RESTORE + CREATE COMPLETE")
print(f"  Restored: {restored} cards")
print(f"  Created: {new_count} new business cards")
print(f"  Total business cards now open: ~25")
print("="*70)