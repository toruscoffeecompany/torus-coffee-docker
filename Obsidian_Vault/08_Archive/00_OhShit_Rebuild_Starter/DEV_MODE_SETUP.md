---
tags: [dev-mode, setup, local-tools, subagents, skills, priority-p1]
updated: 2026-07-15
author: Sir Greensail / Captain
---

# Dev Mode Setup - Full Local Toolchain

**Purpose:** Everything you need to run the full pirate stack offline on your PC. No cloud dependencies. No SaaS subscriptions. No lock-in.

**Captain's Rule:** All code and tools must be pirate-owned. You own the infrastructure. You control the data.

---

## Local Subagents (vault_audit.py)

**Location:** `C:\Users\kidsm\Documents\My Docs\VOID Pirate Trading Co\scripts\vault_audit.py`

**Run from anywhere:**
```
python "C:/Users/kidsm/Documents/My Docs/VOID Pirate Trading Co/scripts/vault_audit.py"
```

**Output:** `00_Vault_Index/AUDIT_YYYY-MM-DD_HHMM.md`

**Checks:**
- Rule 0: non-ASCII chars across active vault
- PII: unsealed emails, SSNs, phones, addresses
- Legacy paths: old folder refs outside ROOT_INDEX.md
- Brain consistency: NO AMENDMENT flags, Obsidian-primary rule, ONE-WAY drive sync
- Folder structure: required folders present
- Crownless design: real email leaks in project docs
- Drive sync: ONE-WAY backup rule enforced

**Scheduled run:** Add to Windows Task Scheduler or Granola when integrated.

---

## Skill Pack Management

**Location:** `03_AI_Operating_System/Skills_External/`

**Protocol:**
1. Captain approves repo URL per skill pack
2. Run: `git clone <repo> 03_AI_Operating_System/Skills_External/<SkillPack>/`
3. Verify with `vault_audit.py`
4. Update `SKILLS_EXTERNAL_INDEX.md` with status

**Current state:** 9 imported, 25 missing. See `SKILLS_EXTERNAL_INDEX.md` for full list.

**Captain approval required:** No skill pack downloads without explicit Captain approval per repo. No exceptions.

---

## AI Runtime Personalities

| AI | Brain Folder | Role | Write Scope |
|----|--------------|------|-------------|
| Hermes | `Brain_Hermes/` | Sir Greensail Boatswain | Full vault write |
| Claude | `Brain_Claude/` | Bosun Cobalt Deepkeel | Full vault write |
| Codex | `Brain_Codex/` | Sir Greenframe Signal Quartermaster | Full vault write |
| Gemini | `Brain_Gemini/` | Sir Silver Signalman | Drive + Hooks/ only |

**Each AI owns:** `PERSONALITY.md`, `MEMORY.md`, `RUNTIME_NOTES.md`
**Captain has:** Delete override on all AI files

---

## Folder Tree (Canonical)

```
Obsidian_Vault/
|-- 00_Vault_Index/          # Master index, audit reports, dev mode docs
|-- 00_VOID_BIZ_GDRIVE_SYNC/ # Business-only backup mirror
|-- 01_Projects/             # Active projects (Crownless only for now)
|-- 02_Business_Operations/  # Biz brains, legal, finance, records
|-- 03_AI_Operating_System/  # AI personalities, skills, hooks
|-- 04_Resources/            # Lore, legal refs, research, tools
|-- 05_Daily_Life/           # Daily logs, dashboards, heartbeats
|-- 06_Archive/              # Old backups, retired projects
|-- .obsidian/               # Obsidian config (must stay at root)
|-- ROOT_INDEX.md            # Legacy path map
```

---

## Git Push Rules

**Push ONLY after lock-down:**
- `Designs/`, `Plans/`, `Crownless_Fortune_live/`
- `TODO.md`, `WORK_NOTES.md`
- `scripts/`, state schemas
- `.gitignore`

**NEVER push:**
- `backups/`, `node_modules/`, binaries, secrets
- `treasure_map_keys.env`
- PII-tagged legal docs
- 80MB legal PDF collection

---

## Local Toolchain

| Tool | Purpose | Status |
|------|---------|--------|
| `vault_audit.py` | Local vault verification | [x] Built |
| `git` | Version control | [x] Available |
| `python` | Scripting, shutil for Drive | [x] Available |
| `pdfplumber` | PDF text extraction | [x] Available |
| `python-docx` | DOCX to Markdown | [x] Available |
| web_search/web_extract | Live web lookups | [x] Functional |
| Granola | Meeting notes sync | ... Pending CLI investigation |

---

## Next Steps

1. [x] Vault structure locked
2. [x] Rule 0 enforced across all active files
3. [x] PII sealed to legal-only files
4. [x] Legacy paths resolved
5. [x] BTB integration complete
6. [x] Audit engine built and tested
7. ... Skill pack downloads (pending Captain approval per repo)
8. ... Granola CLI integration (if possible)
9. ... Push to git after Crownless lock-down
10. ... Linear/Notion/NotebookLM sync

---

## Captain's Orders

- All other projects ON HOLD until Crownless design phase completes
- No skill pack downloads without per-repo approval
- No git push until full lock-down verified
- Drive sync: one-way only, no art/code/secrets/sensitive financials
- Real PII: locked to `LEGAL_ADDRESS_REQUIRED` files only

---

*This is the operating system. Everything else is design.*

- Sir Greensail, 2026-07-15
