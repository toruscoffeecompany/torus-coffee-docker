#!/usr/bin/env python3
"""
Miss Pink — FAST C: DRIVE SCAN
Finds all large files + duplicates on C: drive.
No recursion into Windows/Program Files (safe).
"""
import os, os.path, hashlib, time
from collections import defaultdict
from datetime import datetime

start = time.time()
C = "C:\\"
SKIP_DIRS = {"Windows", "Program Files", "Program Files (x86)", "ProgramData", "$Recycle.Bin", "$WinREAgent", "Recovery", "System Volume Information", "Intel", "AMD", "CUE5", "Dragon Center", "OneDriveTemp", "PerfLogs", "inetpub", "Python314", "Config.Msi", "Users/torus/OneDrive"}

seen_sizes = defaultdict(list)  # size → [paths] (duplicates)
big_files = []  # (size, path) for >100MB files

for root_dir in [C]:
    for item in os.listdir(root_dir):
        path = os.path.join(root_dir, item)
        if item.startswith("$") or item.startswith(".") or item in SKIP_DIRS:
            continue
        # Walk each top-level dir
        if os.path.isdir(path):
            for dirpath, dirnames, filenames in os.walk(path, followlinks=False):
                # Skip subdirs matching SKIP_DIRS
                dirnames[:] = [d for d in dirnames if d not in SKIP_DIRS and not d.startswith("$")]
                for fname in filenames:
                    fpath = os.path.join(dirpath, fname)
                    try:
                        sz = os.path.getsize(fpath)
                        if sz > 100 * 1024 * 1024:  # 100MB+
                            big_files.append((sz, fpath))
                        # Track potential duplicates by size
                        if sz > 10 * 1024 * 1024:  # 10MB+ candidates
                            seen_sizes[sz].append(fpath)
                    except (PermissionError, OSError):
                        pass

# Print big files
big_files.sort(key=lambda x: -x[0])
print(f"=== BIG FILES on C: (>100MB) — scan took {time.time()-start:.1f}s ===")
for sz, path in big_files[:30]:
    print(f"  {sz/(1024**3):8.2f} GB  {path.replace(C, '')}")

# Print duplicates (same size = likely same content)
print(f"\n=== POTENTIAL DUPLICATES (same size, 10MB+) ===")
dupes_found = 0
for sz, paths in sorted(seen_sizes.items(), key=lambda x: -x[0]):
    if len(paths) > 1:
        # Verify actual content with quick hash for small files (10-100MB)
        if sz < 100 * 1024 * 1024:
            hashes = {}
            for p in paths:
                try:
                    with open(p, "rb") as f:
                        h = hashlib.md5(f.read(1024*1024)).hexdigest()
                    hashes.setdefault(h, []).append(p)
                except:
                    pass
            for h, hpaths in hashes.items():
                if len(hpaths) > 1:
                    print(f"  {sz/(1024**3):6.2f} GB × {len(hpaths)} (md5 match):")
                    for p in hpaths:
                        print(f"    {p.replace(C, '')}")
                    dupes_found += len(hpaths)
        else:
            print(f"  {sz/(1024**3):6.2f} GB × {len(paths)} (size match — large file, verify manually):")
            for p in paths:
                print(f"    {p.replace(C, '')}")

print(f"\nPotential duplicates found: {dupes_found}")
print(f"\nTotal big files (>100MB): {len(big_files)}")
