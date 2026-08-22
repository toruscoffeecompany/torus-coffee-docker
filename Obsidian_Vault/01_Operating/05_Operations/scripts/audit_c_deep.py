#!/usr/bin/env python3
"""
Miss Pink — C: DEEP DIVE
Check Windows system directories for space waste.
"""
import os, shutil

def safe_dir_size(path, max_depth=3, _depth=0):
    if _depth > max_depth: return 0
    total = 0
    try:
        with os.scandir(path) as it:
            for entry in it:
                try:
                    if entry.is_symlink(): continue
                    if entry.is_file(follow_symlinks=False):
                        total += entry.stat(follow_symlinks=False).st_size
                    elif entry.is_dir(follow_symlinks=False):
                        total += safe_dir_size(entry.path, max_depth, _depth + 1)
                except (PermissionError, OSError): pass
    except (PermissionError, OSError): pass
    return total

print("=== C: Windows System Directories ===\n")

locations = [
    (r"C:\Windows\WinSxS", "WinSxS (Windows Update cache)"),
    (r"C:\Windows.old", "Windows.old (previous install)"),
    (r"C:\Windows\System32", "System32"),
    (r"C:\Windows\Installer", "Installer"),
    (r"C:\Windows\Panther", "Panther (install files)"),
    (r"C:\System Volume Information", "System Volume Info (shadow copies)"),
    (r"C:\ProgramData\Microsoft\Windows", "ProgramData\\Microsoft\\Windows"),
    (r"C:\Users\torus\AppData\Local\Docker", "Docker (local)"),
    (r"C:\Users\torus\AppData\Local\Packages", "App Packages"),
    (r"C:\Users\torus\AppData\Local\Microsoft\WindowsApps", "WindowsApps"),
    (r"C:\Users\torus\Videos", "Videos"),
    (r"C:\Users\torus\Music", "Music"),
    (r"C:\Users\torus\Pictures", "Pictures"),
    (r"C:\Users\torus\Downloads", "Downloads"),
    (r"C:\$Recycle.Bin", "Recycle Bin"),
]

total_visible = 0
for path, name in locations:
    if os.path.exists(path):
        sz = safe_dir_size(path, max_depth=2)
        total_visible += sz
        print(f"  {name:45s} {sz/(1024**3):10.2f} GB  [{path[:60]}]")

t, u, f = shutil.disk_usage("C:/")
print(f"\n=== TOTAL C: ===")
print(f"  Used: {u/(1024**3):.1f} GB")
print(f"  Visible scanned: {total_visible/(1024**3):.1f} GB")
print(f"  Still hidden: {(u - total_visible - 98)/(1024**3):.1f} GB")
