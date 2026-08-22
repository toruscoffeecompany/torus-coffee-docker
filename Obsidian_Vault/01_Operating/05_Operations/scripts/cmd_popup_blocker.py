import subprocess, time, sys, os, signal
from pathlib import Path
from datetime import datetime, timezone

VAULT = Path(r'D:\Work\Torus Coffee Company LLC')
LOG = VAULT / '10_Skills_Library/05_Operations/logs/cmd_popup_blocker.log'
PID_FILE = VAULT / '10_Skills_Library/05_Operations/logs/pids/cmd_popup_blocker.pid'

CREATE_NO_WINDOW = 0x08000000  # subprocess.CREATE_NO_WINDOW

def log(msg):
    line = f'[{datetime.now(timezone.utc).isoformat()}] {msg}'
    try:
        LOG.parent.mkdir(parents=True, exist_ok=True)
        with open(LOG, 'a') as f:
            f.write(line + '\n')
    except:
        pass
    print(line, flush=True)

def find_popup_processes():
    """Returns list of (name, pid) for processes that can spawn visible cmd windows."""
    result = []
    try:
        r = subprocess.run(
            ['tasklist', '/FI', 'IMAGENAME eq cmd.exe', '/FI', 'IMAGENAME eq conhost.exe', '/FO', 'CSV', '/NH'],
            capture_output=True, text=True, timeout=5,
            creationflags=CREATE_NO_WINDOW,
        )
        for line in r.stdout.strip().split('\n'):
            line = line.strip()
            if not line:
                continue
            parts = [p.strip().strip('"') for p in line.split('","')]
            if len(parts) >= 2:
                result.append((parts[0], parts[1]))
    except Exception as e:
        log(f'ERROR scanning processes: {e}')
    return result

def main():
    log('CMD_POPUP_BLOCKER_START — aggressive no-window mode')
    PID_FILE.parent.mkdir(parents=True, exist_ok=True)
    PID_FILE.write_text(str(os.getpid()), encoding='utf-8')
    killed = 0
    while True:
        try:
            procs = find_popup_processes()
            for name, pid in procs:
                try:
                    subprocess.run(
                        ['taskkill', '/F', '/PID', pid],
                        capture_output=True, timeout=3,
                        creationflags=CREATE_NO_WINDOW,
                    )
                    killed += 1
                    log(f'KILLED {name} PID={pid} total={killed}')
                except Exception as e:
                    log(f'TASKKILL_FAILED PID={pid}: {e}')
            time.sleep(0.2)
        except KeyboardInterrupt:
            break
        except Exception as e:
            log(f'ERROR: {e}')
            time.sleep(1)

    log(f'CMD_POPUP_BLOCKER_STOP killed={killed}')
    try:
        PID_FILE.unlink(missing_ok=True)
    except:
        pass

if __name__ == '__main__':
    main()
