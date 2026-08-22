# ⛩️ TORUS COFFEE PC ORGANIZATION PLAN — 2026-08-12T07:18Z
**Captain: Bryon Smith | PINKCADY | Lane: Full PC Organization**

---

## 📊 CURRENT STATE — FULL PC SCAN

### Drive Space
| Drive | Size | Used | Free | % Used |
|-------|------|------|------|--------|
| C: (System) | 466G | 454G | **12G** | **98%** ⚠️ CRITICAL |
| D: (Work) | 954G | 524G | 431G | 55% ✅ |
| G: | 15G | 4.3G | 11G | 29% ✅ |
| Z: (Vault) | 466G | 385G | 81G | 83% ✅ |

### Misplaced Items (outside `D:\Work\Torus Coffee Company LLC\`)

| Location | Contents | Action |
|----------|----------|--------|
| `D:\Work\02_Business_Operations\` | Communications/Outbox/1 file (`crew_queue_auto_sir-green...msg.md`) | **MERGE** into business root's 02_Business_Operations |
| `D:\Work\Torus_Ops_bare.git\` | Bare git repo (remote origin → Torus business root) | **MOVE** to 14_Infrastructure/ |
| `D:\Work\Hermes Alt Obsidian Vault Skills\External_Code\` | External code references | **MOVE** to 10_Skills_Library/ or delete |
| `D:\Work\Sir_Azure_Backup\pip-cache\ + tmp\` | pip cache + temp files | **DELETE** (safe, auto-regenerated) |
| `D:\Work\SQUIDSTATION_Archive_20260807\` | 19GB treasure_map.db + 275MB tools | **ARCHIVE** to Z:\ (Sir Green's data — don't delete) |

### Duplicate/Conflicting Directories (inside business root)

| Conflict | Resolution |
|----------|------------|
| `10\Skills_Library\` → **DUPLICATE** of `10_Skills_Library\` | **REMOVE** `10` dir (contents already in 10_Skills_Library) |
| `Obsidian_Vault\` | Empty — needs population |
| `PROJECT Torus website\` | Empty — needs population |
| `06_Website\` exists alongside new `PROJECT Torus website` | **MOVE** 06_Website contents → PROJECT Torus website |
| `nul` file (0 bytes) | **DELETE** (Windows artifact) |

### Existing Structure (inside `D:\Work\Torus Coffee Company LLC\`)
```
├── 00_Inbox/                    (vault home + inbox)
├── 00_Vault_Home.md             (vault dashboard)
├── 01_Operating/                ✅
├── 02_Business_Operations/      ✅ (Archive, Captain_Reports, Communications)
├── 02_Tax/                      ✅ (2025 docs read-only per vault rules)
├── 03_AI_Operating_System/      ✅
├── 03_Financials/               ✅
├── 04_Products/                 ✅
├── 05_Legal/                    ✅
├── 06_Growth_Marketing/         ✅
├── 06_Website/                  ✅ → MOVE to PROJECT Torus website/
├── 07_Photos/                   ✅
├── 07_Templates/                ✅
├── 08_Archive/                  ✅
├── 08_Design_Brand/             ✅
├── 08_Moon_Phase/               ✅
├── 08_Reports/                  ✅
├── 09_Projects/                 ✅
├── 10/                          ❌ DUPLICATE (Skills_Library)
├── 10_Skills_Library/           ✅
├── 10_World_Religious_Hobbies/  ✅
├── 11_Vendors/                  ✅
├── 12_Customers/                ✅
├── 12_Pirate_Philosophy/        ✅
├── 13_Team/                     ✅
├── 13_Theology/                 ✅
├── 14_Infrastructure/           ✅ → Torus_Ops_bare.git goes here
├── 14_Religion/                 ✅
├── 99_Inbox/                    ✅
├── Obsidian_Vault/              ❌ EMPTY — needs population
├── PROJECT Torus website/       ❌ EMPTY — needs population
├── Pirate Fleet Operations/     ✅ (existing)
├── scripts/                     ✅ (OODA, bug hunt scripts)
├── tr3asure_mAp/               ✅ (trading scanner)
└── .obsidian/                   ✅ (vault plugins)
```

---

## 🟡 PROPOSED ACTIONS (require user approval)

1. **MERGE** `D:\Work\02_Business_Operations/Communications/Outbox/crew_queue_auto...msg.md` → `D:\Work\Torus Coffee Company LLC/02_Business_Operations/Communications/Outbox/`
2. **MOVE** `D:\Work\Torus_Ops_bare.git` → `D:\Work\Torus Coffee Company LLC/14_Infrastructure/`
3. **REMOVE** `D:\Work\Torus Coffee Company LLC/10/` (duplicate of 10_Skills_Library)
4. **DELETE** `D:\Work\Torus Coffee Company LLC/nul` (0-byte Windows artifact)
5. **MOVE** `06_Website/` contents → `PROJECT Torus website/`
6. **POPULATE** `Obsidian_Vault/` from old Z:\Developer_Brain vault content
7. **DELETE** `D:\Work\Sir_Azure_Backup\pip-cache\ + tmp\` (safe — auto-regenerated)
8. **ARCHIVE** `SQUIDSTATION_Archive_20260807` (19GB db) — needs Sir Green input on whether to move to Z:\ or delete

❌ **NOT touching:** Z:\Developer_Brain (shared Sir Green vault), treasure_map.db, Discord tokens, Alpaca keys

---

## ✅ SAFE COMPLETED
- Full PC scan complete ✅
- All files inventoried ✅
- No data lost ✅
- Misplaced files identified ✅

---

**Awaiting Captain approval for destructive actions.**\
⛩ — Miss Pink, PINKCADY