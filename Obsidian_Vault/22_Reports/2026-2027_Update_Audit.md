# Torus Coffee Company LLC — 2026/2027 Business Document Update Plan
_Read-only audit produced 2026-07-22. Excluded from review for modification: `02_Tax/Taxes/2025/` and `03_Financials/`._

---

## Priority List

### 1. 2026 Expense Tracker
- **Path:** `03_Financials/`
- **Current state:** Only 2025 files present; Vault Home explicitly flags the need to begin 2026 expense tracking.
- **Proposed changes:**
  - Add `Expense_Report_2026.xlsx` with monthly tabs and category encumbrances.
  - Add `Financial_Statements_2026.xlsx` for P&L, balance sheet, and cash-flow tracking.
  - Mirror a lightweight template from the 2025 workbook to preserve categorization.

### 2. Permits Checklist / Tracker
- **Path:** `05_Research/Licenses and Permits NEEDED.docx`
- **Current state:** Static list of permits with renewal notes; no tracked status, due dates, or completion flags.
- **Proposed changes:**
  - Create `05_Research/Licenses_and_Permits_Tracker.xlsx` (or `.md`) with columns: permit, issuing agency, fee, renewal cycle, next due date, status, documentation link.
  - Convert renewal knowledge into an actionable annual/biennial checklist.

### 3. Business Plan Refresh
- **Path:** `01_Operating/Sara's Business Plan (Torus Coffee Company).docx`
- **Current state:** Milestones stretch to Q4 2026 but overall tone reflects pre-launch; actuals vs plan are not reconciled.
- **Proposed changes:**
  - Update Section 7 Financial Plan with actual 2025 results and adjusted 2026/2027 targets.
  - Refresh SWOT/market section with current competitors and channel performance.
  - Add a concise “2026 Review” appendix and a 2027 roadmap.
  - Ensure product strategy includes coffee launch/status explicitly.

### 4. Product Prices / Catalog Sync
- **Paths:**
  - `04_Products/Product List and Prices.xlsx`
  - `04_Products/catalog_products.csv`
  - `04_Products/catalog_products.xlsx`
  - `08_Design_Brand/catalog_products.csv`
  - `08_Design_Brand/FB_Marketplace_catalog_products.xlsx`
- **Current state:** Multiple sources of truth for product/price data, which creates drift risk.
- **Proposed changes:**
  - Treat `04_Products/Product List and Prices.xlsx` as the master price list.
  - Reconcile SKUs, descriptions, and prices across CSV/XLSX exports.
  - Add currency/effective date columns and a change log tab.

### 5. Legal / Policy Review
- **Paths:**
  - `01_Operating/Terms & Conditions.docx`
  - `01_Operating/Privacy Policy.docx`
  - `01_Operating/Shipping Policy.docx`
  - `01_Operating/Refund & Returns Policy.docx`
- **Current state:** Policies dated 2025. Likely stale for 2026 operations and any new channels/coverage.
- **Proposed changes:**
  - Set explicit annual review dates in each doc footer or metadata.
  - Refresh contact details, carrier language, and return timelines if procedures changed.
  - Review privacy policy for current data handling, cookies, and any checkout changes.

### 6. Entity Summary
- **Paths:** `01_Operating/Operating Paperwork/*` (PDFs/MDs)
- **Current state:** Entity details are distributed across legal PDFs; no single concise summary file.
- **Proposed changes:**
  - Add `01_Operating/Entity_Summary.md` summarizing: legal name, state, formation date, EIN, registered agent, owner/officer roles, trademark status, and key compliance dates.
  - Link to the underlying PDFs for provenance.

### 7. Filing Template
- **Path:** Potentially new under `01_Operating/` or `05_Research/`
- **Current state:** No general filing/reporting template found.
- **Proposed changes:**
  - Create reusable `.xlsx` or `.md` templates for:
    - Annual LLC biennial report reminder/status
    - Sales tax period closeout checklist
    - FDA Food Facility Registration renewal reminder

---

## Audit Method
- Read-only enumeration of `01_Operating`, `04_Products`, `05_Research`, `06_Website`, `07_Photos`, `08_Archive`, `08_Design_Brand`, `08_Reports`, and relevant non-tax financial docs.
- Excluded per task constraints: `02_Tax/Taxes/2025/` and `03_Financials/`.
