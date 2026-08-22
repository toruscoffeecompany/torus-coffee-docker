#!/usr/bin/env python3
"""
Miss Pink — C: DRIVE SPACE AUDIT
Find ALL space consumers on C: — including protected dirs.
Uses os.scandir for speed + skips permission-denied.
"""
import os, sys

def get_dir_size(path, max_depth=5, _depth=0):
    """Get directory size without following symlinks."""
    if _depth > max_depth:
        return 0
    total = 0
    try:
        with os.scandir(path) as it:
            for entry in it:
                try:
                    if entry.is_symlink():
                        continue
                    if entry.is_file(follow_symlinks=False):
                        total += entry.stat(follow_symlinks=False).st_size
                    elif entry.is_dir(follow_symlinks=False):
                        total += get_dir_size(entry.path, max_depth, _depth + 1)
                except (PermissionError, OSError):
                    pass
    except (PermissionError, OSError):
        pass
    return total

print("=== C: DRIVE SPACE AUDIT ===\n")

# Check major C: locations
locations = [
    (r"C:\Users", "Users"),
    (r"C:\ProgramData", "ProgramData"),
    (r"C:\Program Files", "Program Files"),
    (r"C:\Program Files (x86)", "Program Files (x86)"),
    (r"C:\Windows", "Windows"),
    (r"C:\VM", "VM"),
    (r"C:\torus_cad", "torus_cad"),
    (r"C:\Ollama", "Ollama"),
    (r"C:\node", "node"),
    (r"C:\Python314", "Python314"),
]

grand_total = 0
results = []
for path, name in locations:
    if os.path.exists(path):
        sz = get_dir_size(path, max_depth=3)
        grand_total += sz
        results.append((name, sz))

# Sort by size descending
for name, sz in sorted(results, key=lambda x: -x[1]):
    print(f"  {name:25s} {sz/(1024**3):10.2f} GB")

print(f"\n  {'TOTAL SCANNED':25s} {grand_total/(1024**3):10.2f} GB")

# Get actual disk usage
import shutil
t, u, f = shutil.disk_usage("C:/")
print(f"\n=== ACTUAL C: USAGE ===")
print(f"  Total: {t/(1024**3):.1f} GB")
print(f"  Used:  {u/(1024**3):.1f} GB")
print(f"  Free:  {f/(1024**3):.1f} GB")
print(f"\n  Unaccounted: {(u - grand_total)/(1024**3):.1f} GB")
print(f"  (likely in Windows/system protected dirs we can't scan)")
