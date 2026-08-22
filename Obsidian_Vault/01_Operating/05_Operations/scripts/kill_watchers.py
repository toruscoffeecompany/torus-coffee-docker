import subprocess, re
out = subprocess.check_output(['tasklist', '/FI', 'IMAGENAME eq python.exe', '/FO', 'CSV', '/NH'], text=True, encoding='utf-8', errors='ignore')
for line in out.splitlines():
    line=line.strip()
    if not line:
        continue
    m = re.match(r'"([^"]+)","(\d+)"', line)
    if not m:
        continue
    name, pid = m.group(1), m.group(2)
    try:
        cmd = subprocess.check_output(['wmic', 'process', 'where', f'ProcessId={pid}', 'get', 'CommandLine', '/value'], text=True, encoding='utf-8', errors='ignore')
    except Exception:
        continue
    cl = cmd.split('=',1)[1].strip() if '=' in cmd else ''
    if 'pinkcady_comms_watcher.py' in cl or 'ooda_self_prompt_loop.py' in cl:
        print(f'killing {pid} {cl}')
        subprocess.call(['taskkill', '/F', '/PID', pid])
