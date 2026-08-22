# US Bank Account Integration — Automation Investigation

## Current State
- **Account:** USB Checking 5287 (from 2025 statements)
- **Location:** `02_Tax/Taxes/2025/U.S. Bank Statements/`
- **Access:** Manual PDF statements only
- **Automation:** None currently

## What We CAN Automate (Free Tier)

### 1. Manual CSV Export → Wave Accounting
**Cost:** Free  
**Effort:** 30 minutes/month

1. Log into US Bank online banking
2. Export monthly statement as CSV
3. Import to Wave Accounting (free)
4. Categorize transactions
5. Reconcile monthly

**Automation level:** Semi-automated (manual export, auto-import)

### 2. Zapier Integration (Paid Feature)
**Cost:** $19.99/month (Zapier Starter)  
**What it does:**
- Trigger: New transaction in US Bank
- Action: Create row in Google Sheets
- Action: Send Gmail alert
- Action: Create Trello card

**Verdict:** Not free, wait until revenue

### 3. US Bank Developer API
**Cost:** Requires business account + developer application  
**Reality:** Not available for small businesses without commercial agreement

**Verdict:** Not feasible right now

## What We SHOULD Build (Free)

### 1. Transaction Categorization System
**File:** `10_Skills_Library/05_Operations/scripts/bank_reconciler.py`

```python
"""
US Bank transaction categorizer.
Reads exported CSV, categorizes transactions, creates monthly report.
"""
import csv
from pathlib import Path
from datetime import datetime

VAULT = Path(r"D:\Work\Torus Coffee Company LLC")
BANK_CSV = VAULT / "02_Tax" / "Taxes" / "2025" / "U.S. Bank Statements" / "transactions.csv"
CATEGORIES_FILE = VAULT / "03_Financials" / "bank_categories.json"

# Categories
CATEGORIES = {
  "square_payment": ["SQUARE INC", "SQUARE"],
  "venmo": ["VENMO"],
  "supplies": ["AMAZON", "OFFICEDEPOT", "UBER"],
  "shipping": ["USPS", "FEDEX", "UPS"],
  "food": ["HY-VEE", "CASH STORE", "GATEWAY"],
  "gas": ["CIRCLE K", "KUM&GO", "PILOT"],
  "income": ["DEPOSIT", "TRANSFER"],
}

def categorize_transaction(description):
  desc_upper = description.upper()
  for category, keywords in CATEGORIES.items():
    if any(kw in desc_upper for kw in keywords):
      return category
  return "uncategorized"

def reconcile_month(csv_file):
  """Reconcile a month's transactions."""
  transactions = []
  
  with open(csv_file, newline='') as f:
    reader = csv.DictReader(f)
    for row in reader:
      txn = {
        "date": row.get("Date"),
        "description": row.get("Description"),
        "amount": float(row.get("Amount", 0)),
        "category": categorize_transaction(row.get("Description", "")),
      }
      transactions.append(txn)
  
  # Save categorized transactions
  output_file = BANK_CSV.parent / f"categorized_{datetime.now().strftime('%Y%m%d')}.json"
  with open(output_file, 'w') as f:
    json.dump(transactions, f, indent=2)
  
  return transactions

def generate_monthly_report(transactions):
  """Generate monthly spending report."""
  categories = {}
  total_spent = 0
  total_income = 0
  
  for txn in transactions:
    cat = txn['category']
    amount = txn['amount']
    
    if cat not in categories:
      categories[cat] = {"count": 0, "total": 0}
    
    categories[cat]["count"] += 1
    categories[cat]["total"] += amount
    
    if amount < 0:
      total_spent += abs(amount)
    else:
      total_income += amount
  
  report = {
    "month": datetime.now().strftime("%Y-%m"),
    "total_spent": total_spent,
    "total_income": total_income,
    "net": total_income - total_spent,
    "by_category": categories,
  }
  
  return report
```

**Task Scheduler:** Run on 1st of month  
**Input:** Manual CSV export from US Bank  
**Output:** Categorized JSON + monthly report

### 2. Monthly Bank Reconciliation Checklist
**File:** `03_Financials/Bank_Reconciliation_Checklist.md`

1. [ ] Export CSV from US Bank online banking
2. [ ] Run `bank_reconciler.py`
3. [ ] Review uncategorized transactions
4. [ ] Update `bank_categories.json` with new vendors
5. [ ] Verify totals match statement
6. [ ] Save report to `03_Financials/Reports/`
7. [ ] Update Revenue_Stream_Plan.md with actuals

### 3. Free Bookkeeping Stack

| Tool | Purpose | Cost |
|------|---------|------|
| Wave Accounting | Bookkeeping, invoicing, receipts | Free |
| US Bank CSV export | Transaction data | Free |
| bank_reconciler.py | Categorization | Free |
| Google Sheets | Monthly tracking | Free |
| Obsidian vault | Audit trail | Free |

**Total monthly cost: $0**

## What We CANNOT Do (Without Paying)

1. **Real-time transaction monitoring** — requires Zapier paid tier or US Bank API
2. **Automatic receipt matching** — requires Wave paid tier or custom OCR
3. **Multi-account aggregation** — requires Plaid/Teller ($)
4. **Automated tax estimates** — requires QuickBooks ($)

## Recommended Path

### Now (Free)
1. Set up Wave Accounting account
2. Export first US Bank CSV
3. Run bank_reconciler.py manually
4. Create monthly reconciliation routine

### When Revenue Hits $1,000/month
1. Upgrade Zapier to Starter ($20/mo)
2. Automate: US Bank → Google Sheets → Gmail alerts
3. Automate: Square → Wave → HubSpot

### When Revenue Hits $5,000/month
1. Upgrade Wave to paid tier ($25/mo)
2. Add receipt scanning automation
3. Integrate with tax software

## Next Steps

1. [ ] Create Wave Accounting account
2. [ ] Export latest US Bank statement as CSV
3. [ ] Test bank_reconciler.py with real data
4. [ ] Create monthly reconciliation Task Scheduler job
5. [ ] Document process in Obsidian vault

## Status

- ✅ Investigation complete
- ✅ Free-tier path identified
- ✅ Automation script designed
- ⏳ Awaiting first CSV export to test
