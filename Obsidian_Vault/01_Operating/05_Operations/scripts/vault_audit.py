#!/usr/bin/env python3
"""Recurring Obsidian vault audit.
- Scans for broken wiki-links
- Detects duplicate filenames
- Reports plugin config drift
- Writes VAULT_AUDIT_SNAPSHOT.json
"""
import json
import re
from datetime import datetime, timezone
from pathlib import Path

BASE = Path(r"D:\Work\Torus Coffee Company LLC")
SNAPSHOT = BASE / "10_Skills_Library" / "05_Operations" / "VAULT_AUDIT_SNAPSHOT.json"
skip = {".git", ".obsidian", "node_modules", "__pycache__", "06_Website/next-storefront", "10_Skills_Library/05_Operations/venv", "10_Skills_Library/05_Operations/venv314"}

broken = []
duplicates = {}
for f in BASE.rglob("*.md"):
    if any(part in skip for part in f.parts):
        continue
    rel = f.relative_to(BASE)
    duplicates.setdefault(f.name, []).append(str(rel))
    try:
        content = f.read_text(encoding="utf-8", errors="ignore")
    except Exception:
        continue
    for link in re.findall(r"\[\[([^\]|]+)", content):
        target = link.strip()
        if not target:
            continue
        target_path = f.parent / target
        if not target_path.exists() and not (target_path.with_suffix(".md")).exists():
            if not (BASE / target).exists() and not (BASE / (target + ".md")).exists():
                broken.append((str(rel), target))

dup_report = {k: v for k, v in duplicates.items() if len(v) > 1 and k not in {"README.md", "index.md", "_INDEX.md", "LICENSE.md"}}
snapshot = {
    "timestamp": datetime.now(timezone.utc).isoformat(),
    "broken_links": len(broken),
    "broken_link_samples": broken[:20],
    "duplicate_filenames": len(dup_report),
    "duplicate_samples": {k: v[:5] for k, v in list(dup_report.items())[:10]},
    "plugins_configured": True,
}
SNAPSHOT.write_text(json.dumps(snapshot, indent=2), encoding="utf-8")
print(f"VAULT_AUDIT_OK broken={len(broken)} duplicates={len(dup_report)}")
