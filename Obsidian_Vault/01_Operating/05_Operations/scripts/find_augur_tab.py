import os

search_paths = [
    '//192.168.0.39/VOID Pirate Trading Co/PROJECT_tr3asure_mAp/tr3asure_mAp/frontend/',
    'D:/Work/Torus Coffee Company LLC/06_Website/dashboard/',
    '//192.168.0.39/VOID Pirate Trading Co/PROJECT_tr3asure_mAp/',
]

for base in search_paths:
    if not os.path.exists(base):
        print(f"NOT FOUND: {base}")
        continue
    count = 0
    for root, dirs, files in os.walk(base):
        if 'node_modules' in root:
            dirs.clear()
            continue
        for f in files:
            if f.endswith(('.html', '.py', '.js', '.jsx')):
                fpath = os.path.join(root, f)
                try:
                    with open(fpath, 'r', errors='ignore') as fh:
                        content = fh.read(10000)
                    if 'augur-trading' in content or ('tabnav' in content and 'Fleet HUD' in content):
                        print(f"FOUND: {fpath} ({os.path.getsize(fpath)} bytes)")
                        count += 1
                except:
                    pass
        if root.count(os.sep) > 7:
            dirs.clear()
    if count == 0:
        print(f"No matches in: {base}")
    else:
        print(f"  {count} files found")