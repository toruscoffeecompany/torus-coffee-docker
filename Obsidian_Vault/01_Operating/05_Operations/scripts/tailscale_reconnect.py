#!/usr/bin/env python3
"""
Tailscale reconnection automation for STEALTHATTACK.
Monitors Tailscale IP changes and auto-reconnects on profile lock/unlock.
Designed to run as a Windows service via NSSM.
"""
import subprocess
import time
import logging
from datetime import datetime

LOG = r"D:\Work\Torus Coffee Company LLC\10_Skills_Library\05_Operations\logs\tailscale_reconnect.log"

def log(msg: str) -> None:
    line = f"[{datetime.now().isoformat()}] {msg}"
    print(line)
    try:
        with open(LOG, "a") as f:
            f.write(line + "\n")
    except Exception:
        pass

def get_tailscale_ip() -> str | None:
    try:
        r = subprocess.run(["tailscale", "ip"], capture_output=True, text=True, timeout=10)
        if r.returncode == 0 and r.stdout.strip():
            return r.stdout.strip()
    except Exception:
        pass
    return None

def is_tailscale_up() -> bool:
    ip = get_tailscale_ip()
    if ip and "100." in ip:  # Tailscale CGNAT range
        return True
    return False

def reconnect() -> bool:
    try:
        subprocess.run(["tailscale", "down"], capture_output=True, timeout=15)
        time.sleep(2)
        r = subprocess.run(["tailscale", "up", "--accept-dns", "--accept-routes"],
            capture_output=True, text=True, timeout=30)
        if r.returncode == 0:
            log("✅ Reconnected successfully")
            return True
        else:
            log(f"❌ Reconnect failed: {r.stderr[:200]}")
    except Exception as e:
        log(f"❌ Reconnect error: {e}")
    return False

def main():
    log("Tailscale reconnection daemon started")
    last_ip = get_tailscale_ip()
    log(f"Initial IP: {last_ip or 'NONE'}")
    
    while True:
        time.sleep(30)
        current_ip = get_tailscale_ip()
        
        if current_ip != last_ip:
            log(f"IP change detected: {last_ip or 'NONE'} -> {current_ip or 'NONE'}")
            if not current_ip or "100." not in (current_ip or ""):
                log("Tailscale appears down, attempting reconnect...")
                if reconnect():
                    last_ip = get_tailscale_ip()
                else:
                    last_ip = None
            else:
                last_ip = current_ip
        
        # Also check if Tailscale process is alive but IP lost
        if not is_tailscale_up():
            log("Tailscale unhealthy, attempting reconnect...")
            if reconnect():
                last_ip = get_tailscale_ip()
            else:
                last_ip = None

if __name__ == "__main__":
    try:
        main()
    except KeyboardInterrupt:
        log("Daemon stopped by user")
