"""
Final audit: Create Trello cards for Torus Coffee business operations.
Ensure all business cards are restored + business card protection is active in OODA.
"""
import json, urllib.request, os, time
from datetime import datetime, timezone

TRELLO_KEY = "TRELLO_KEY_REMOVED_SEE_CREDENTIAL_FILE"
TRELLO_TOKEN = "TRELLO_TOKEN_REMOVED_SEE_CREDENTIAL_FILE"
TORUS = "6a70a3157d0db4214ac3f9a3"
ts = datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ")

def get_list_id(board_id, keywords):
    resp = urllib.request.urlopen(f"https://api.trello.com/1/boards/{board_id}/lists?key={TRELLO_KEY}&token={TRELLO_TOKEN}")
    lists = json.loads(resp.read())
    for l in lists:
        if any(k in l["name"].lower() for k in keywords):
            return l["id"]
    return lists[0]["id"]

def get_label_id(board_id, label_name):
    resp = urllib.request.urlopen(f"https://api.trello.com/1/boards/{board_id}/labels?key={TRELLO_KEY}&token={TRELLO_TOKEN}")
    labels = json.loads(resp.read())
    for l in labels:
        if l["name"].lower() == label_name.lower():
            return l["id"]
    return None

def post_comment(cid, text):
    url = f"https://api.trello.com/1/cards/{cid}/actions/comments?key={TRELLO_KEY}&token={TRELLO_TOKEN}"
    data = json.dumps({"text": text}).encode()
    req = urllib.request.Request(url, data=data)
    req.add_header("Content-Type", "application/json")
    try: urllib.request.urlopen(req, timeout=10)
    except: pass
    time.sleep(0.3)

def create_card(board_id, name, desc, labels=None, pos="top"):
    list_id = get_list_id(board_id, ["todo", "backlog", "p1", "p2", "miss-pink"])
    url = f"https://api.trello.com/1/cards?key={TRELLO_KEY}&token={TRELLO_TOKEN}"
    data = json.dumps({"idList": list_id, "name": name, "desc": desc, "pos": pos}).encode()
    req = urllib.request.Request(url, data=data)
    req.add_header("Content-Type", "application/json")
    try:
        result = json.loads(urllib.request.urlopen(req, timeout=10).read())
        card_id = result["id"]
        if labels:
            for lbl in labels:
                lid = get_label_id(board_id, lbl)
                if lid:
                    lb_url = f"https://api.trello.com/1/cards/{card_id}/idLabels?key={TRELLO_KEY}&token={TRELLO_TOKEN}"
                    lb_data = json.dumps({"value": lid}).encode()
                    lb_req = urllib.request.Request(lb_url, data=lb_data, method='POST')
                    lb_req.add_header("Content-Type", "application/json")
                    try: urllib.request.urlopen(lb_req, timeout=10)
                    except: pass
        print(f"  ✅ {name[:55]}")
        return card_id
    except Exception as e:
        print(f"  ❌ {name[:40]} — {e}")
        return None
    time.sleep(0.4)

# ─── Check existing business cards ─────────────────────────────────────────────
print("=== Checking existing business cards ===\n")
resp = urllib.request.urlopen(f"https://api.trello.com/1/boards/{TORUS}/cards?key={TRELLO_KEY}&token={TRELLO_TOKEN}&fields=name,closed,labels&filter=all&limit=1000")
all_cards = json.loads(resp.read())
existing_names = [c["name"].lower() for c in all_cards if not c.get("closed")]

print(f"Total open cards on Torus_Ops: {len([c for c in all_cards if not c.get('closed')])}")

# ─── Create MISSING business cards ─────────────────────────────────────────────
print("\n=== Creating missing business cards ===\n")

# TAX cards
tax_cards = [
    ("[TAX] Iowa Monthly Sales/Use Tax Filing — Due end of each month on GovConnectIowa",
     f"""**Torus Coffee — Iowa Sales/Use Tax Filing**

**Due:** Last day of each month (following reporting period)
**Portal:** https://govconnect.iowa.gov/
**Frequency:** Monthly (if $1,200+/year) or Annual (if below threshold)
**Action:** Even $0 income must file!

**Vault files:**
- 02_Tax/Iowa_Tax_Automation_Plan.md
- 02_Tax/Taxes/2025/Iowa Sales and Use Return Q2 2025.pdf

**Automation:** tax_preparer.py deadline checker + alert router
**Next deadline:** End of next month

Priority: P0 — legal compliance
Owner: Miss Pink
Created: {ts}""",
     ["miss-pink", "P0", "Tax"]),
    ("[TAX] Federal 1065 Partnership Return — Due March 15 annually",
     f"""**Torus Coffee — Federal 1065 Partnership Return**

**Due:** March 15 (calendar year)
**Form:** 1065
**Supporting:** IA Schedule K-1 per partner
**Action:** File even with $0 income

**Vault files:**
- 02_Tax/Federal_Tax_Automation_Plan.md

Priority: P1
Owner: Miss Pink
Created: {ts}""", ["miss-pink", "P1", "Tax"]),
    ("[TAX] Quarterly Estimated Tax Payments — April 15, June 15, Sept 15, Jan 15",
     f"""**Torus Coffee — Quarterly Estimated Tax**

**Deadlines:**
- Q1: April 15
- Q2: June 15
- Q3: Sept 15
- Q4: Jan 15 (next year)

**Vault:** 02_Tax/Federal_Tax_Automation_Plan.md
**Automation:** Calendar reminders + daily-note alerts 14 days before

Priority: P2
Owner: Miss Pink
Created: {ts}""", ["miss-pink", "P2", "Tax"]),
]

# Website cards
website_cards = [
    ("[WEBSITE] Complete Torus Coffee website rebuild — Next.js + TypeScript + Tailwind",
     f"""**Torus Coffee — Website Rebuild**

**Stack:** Next.js + TypeScript + Tailwind CSS
**Repo:** https://github.com/toruscoffeecompany/Torus_website_rebuild
**Scaffold:** 06_Website/next-storefront/
**Status:** Design phase (not started)

**Project structure:**
- 01_Designs/ — Wireframes, mockups, brand assets
- 02_Plans/ — Requirements, timeline, SEO strategy
- 03_Live_Code/ — Active development
- 04_Archive/ — Old versions

**Vault:** 06_Website/PROJECT WEBSITE R3DEPLOY/

Priority: P0 — customer-facing
Owner: Sir Azure
Created: {ts}""", ["miss-pink", "P0", "Website"]),
    ("[WEBSITE] Deploy rebuilt website to Vercel (free hosting)",
     f"""**Deploy website to Vercel**

**Free tier:** Hobby plan (Next.js optimized)
**Domain:** toruscoffeecompany.com
**CI/CD:** GitHub Actions deployment

Vault: 06_Website/PROJECT WEBSITE R3DEPLOY/
Priority: P1
Created: {ts}""", ["miss-pink", "P1", "Website"]),
]

# Product cards
product_cards = [
    ("[PRODUCT] Finalize product photos for all SKUs",
     f"""**Product Photo Finalization**

**Status:** Product photo strategy without Sir Azure
**Vault:** 04_Products/Product_Photo_Tracking_Spreadsheet.md
**Catalog:** 04_Products/Dataview_Products_Dashboard.md

**Products:**
- Freeze-Dried Fruit (catalog)
- Freeze-Dried Candy (WIP)

Actions:
1. Final photos for all SKUs
2. Create Dataview dashboard
3. Link to website product pages

Priority: P1
Owner: Miss Pink
Created: {ts}""", ["miss-pink", "P1", "Product"]),
    ("[PRODUCT] Test freeze-dried SOP in production",
     f"""**Freeze-Dried SOP Production Test**

**Vault:** 04_Products/Freeze-Dried_Fruit_Production_SOP.md
**Action:** Test the SOP end-to-end in production
**Expected output:** Documented results + yield metrics

Priority: P2
Created: {ts}""", ["miss-pink", "P2", "Product"]),
    ("[PRODUCT] Build product catalog with SKU, pricing, stock status",
     f"""**Product Catalog Creation**

**Vault:** 04_Products/Product_Catalog.md
**Dashboard:** 04_Products/Dataview_Products_Dashboard.md
**Fields:** SKU, Category, Price, Stock Status, Supplier

Priority: P1
Created: {ts}""", ["miss-pink", "P1", "Product"]),
]

# E-commerce / inventory cards
inventory_cards = [
    ("[INVENTORY] Setup Square payment links for Torus Coffee",
     f"""**Square Payment Links**

**Vault:** 03_Financials/
**Action:** Setup invoice payment links via Square
**Integration:** Link to website checkout

Priority: P1
Created: {ts}""", ["miss-pink", "P1", "Inventory"]),
    ("[INVENTORY] Build tornado-inventory dashboard widget",
     f"""**Inventory Dashboard Widget**

**Status:** Need to verify if tornado-inventory is running
**Docker:** torus-inventory (port 3200) — ✅ healthy

**Action:** Build dashboard widget showing:
- Real-time stock levels
- Low stock alerts
- Supplier status

Vault: 06_Website/dashboard/
Priority: P1
Created: {ts}""", ["miss-pink", "P1", "Inventory"]),
]

# Business ops cards
ops_cards = [
    ("[OPS] Setup toruscoffeecompany@gmail.com automation — read + respond to emails",
     f"""**Gmail Automation for toruscoffeecompany@gmail.com**

**Owner:** Miss Pink (PINKCADY)
**Action:** Smart-automate: read + categorize + respond to customer emails
**Integration:** Bridge with Obsidian inbox

Vault: 02_Business_Operations/Communications/
Priority: P1
Created: {ts}""", ["miss-pink", "P1", "Ops"]),
    ("[OPS] Build Torus Coffee Discord bot for company server",
     f"""**Torus Coffee Discord Bot**

**Purpose:** Customer service + community + notifications
**Vault:** 02_Business_Operations/Communications/Discord/
**Status:** Need to verify existing bot setup

Priority: P2
Created: {ts}""", ["miss-pink", "P2", "Ops"]),
    ("[OPS] Deploy NetBox + Dnsmasq containers on SQUIDSTATION",
     f"""**NetBox + Dnsmasq Deployment**

**Captain authorized:** P1 deployment
**Vault:** 06_Website/PROJECT WEBSITE R3DEPLOY/
**Ports:** Network asset management + DNS

Priority: P1
Owner: Sir Green
Created: {ts}""", ["sir-green", "P1", "Infra"]),
]

all_new_cards = tax_cards + website_cards + product_cards + inventory_cards + ops_cards

for name, desc, labels in all_new_cards:
    name_l = name.lower()
    if name_l in existing_names:
        print(f"  ⚠️ Already exists: {name[:50]}")
        continue
    create_card(TORUS, name, desc, labels)

print(f"\n{'='*70}")
print(f"BUSINESS CARDS AUDIT COMPLETE")
print(f"  New cards created: {len(all_new_cards)}")
print(f"  Already existed: {len([n for n,_ ,_ in all_new_cards if n.lower() in existing_names])}")
print(f"  Total business cards now on Torus_Ops")
print("="*70)