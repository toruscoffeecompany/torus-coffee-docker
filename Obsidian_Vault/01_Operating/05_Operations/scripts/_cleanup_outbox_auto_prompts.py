#!/usr/bin/env python3
"""Cleanup duplicate auto-prompt replies in outbox."""
from pathlib import Path
from datetime import datetime

OUTBOX = Path(r"D:\Work\Torus Coffee Company LLC\02_Business_Operations\Communications\Outbox")
ARCHIVE = OUTBOX / "_archive_auto_prompts"

files = sorted(OUTBOX.glob("RE_*.msg.md"))
seen = {}
for path in files:
    name = path.name
    if "AUTO_CYCLE" in name or "unknown" in name:
        key = "_".join(name.split("_")[7:]) if "AUTO_CYCLE" in name else name
        if key not in seen:
            seen[key] = []
        seen[key].append(path)

moved = 0
for key, paths in seen.items():
    if len(paths) > 1:
        keep = paths[-1]
        for old in paths[:-1]:
            target = ARCHIVE / old.name
            ARCHIVE.mkdir(parents=True, exist_ok=True)
            old.rename(target)
            moved += 1

print(f"Archived {moved} duplicate auto-prompt replies to {ARCHIVE}")
