import os
import shutil
from pathlib import Path
from collections import defaultdict

outbox = Path("D:/Work/Torus Coffee Company LLC/02_Business_Operations/Communications/Outbox")
archive = outbox / "_archive"
archive.mkdir(exist_ok=True)

files = sorted(outbox.glob("*crew_queue_auto*.msg.md"), key=lambda f: f.stat().st_mtime, reverse=True)

groups = defaultdict(list)
for f in files:
    try:
        text = f.read_text(encoding="utf-8")
        to_line = next((l for l in text.splitlines() if l.startswith("to:")), "")
        crew = to_line.split(":", 1)[1].strip() if ":" in to_line else "unknown"
        name_line = next((l for l in text.splitlines() if l.startswith("- **Name:**")), "")
        card_name = name_line.replace("- **Name:**", "").strip() if name_line else "unknown"
        key = (crew, card_name)
        groups[key].append(f)
    except Exception as e:
        print(f"Error reading {f}: {e}")

moved = 0
kept = 0
for key, group_files in groups.items():
    for f in group_files[1:]:
        dest = archive / f.name
        shutil.move(str(f), str(dest))
        moved += 1
    kept += 1

print(f"Kept: {kept} groups")
print(f"Moved to archive: {moved} files")
