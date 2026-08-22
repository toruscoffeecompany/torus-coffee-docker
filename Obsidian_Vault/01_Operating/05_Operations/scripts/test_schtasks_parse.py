import subprocess
out = subprocess.check_output(['schtasks','/query','/fo','csv','/nh'], text=True, timeout=20)
expected={'Torus_Smart_Ticket_Cycle','Torus_Continuous_OODA','Torus_Vault_Audit','Torus_Trello_Sync','Torus_Inventory_Sync','Torus_Order_Manager','Torus_Daily_Ops_Check','Torus_Social_Media_Check','Torus_Asset_Validator'}
found=set()
for line in out.splitlines():
    parts=[p.strip('"') for p in line.split(',')]
    if len(parts)>=2:
        raw=parts[0].strip()
        if raw.startswith(r'\\'):
            raw=raw.lstrip(r'\\')
        print('raw=',repr(raw))
        if any(raw.startswith(e) for e in expected):
            found.add(raw)
print('found=',sorted(found))
print('missing=',sorted(expected-found))
