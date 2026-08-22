#!/usr/bin/env python3
"""
Cleanup duplicate outbox messages safely.
Moves older duplicate auto-cycle/auto-prompt replies to _archive/.
Keeps the latest of each series and all non-duplicate messages.
"""
import shutil
from pathlib import Path
from collections import defaultdict

VAULT = Path(r"D:\Work\Torus Coffee Company LLC")
OUTBOX = VAULT / "02_Business_Operations/Communications/Outbox"
ARCHIVE = OUTBOX / "_archive"
ARCHIVE.mkdir(exist_ok=True)

files = sorted(OUTBOX.glob("*.msg.md"))
series = defaultdict(list)

for path in files:
    name = path.name
    if name.startswith("RE_"):
        # Extract series key: AUTO_CYCLE_* or AUTO_PROMPT_*
        if "AUTO_CYCLE_" in name:
            key = name.split("AUTO_CYCLE_")[1].rsplit(".", 1)[0]
            series[f"AUTO_CYCLE_{key}"].append(path)
        elif "AUTO_PROMPT_" in name:
            key = name.split("AUTO_PROMPT_")[1].rsplit(".", 1)[0]
            series[f"AUTO_PROMPT_{key}"].append(path)
        elif "unknown" in name:
            series["unknown"].append(path)

moved = []
for key, paths in series.items():
    if len(paths) > 1:
        # Keep the newest, archive the rest
        keep = paths[-1]
        for old in paths[:-1]:
            dest = ARCHIVE / old.name
            shutil.move(str(old), str(dest))
            moved.append((old.name, dest))

print(f"Archived {len(moved)} duplicate messages to _archive/")
for old, new in moved:
    print(f"  {old} -> {new}")
