#!/usr/bin/env python3
"""Crew API — lightweight HTTP status endpoint for fleet mesh.
Serves ship health on port 8090 as expected by SQUIDSTATION dashboard.
Runs as a daemon via pythonw.exe — no console window.
"""
import json
import os
import socket
import subprocess
from datetime import datetime, timezone
from pathlib import Path

BASE = Path(r"D:\Work\Torus Coffee Company LLC")
LOG_FILE = BASE / "10_Skills_Library/05_Operations/logs/crew_api.log"
SHIP_NAME = "PINKCADY"
SHIP_IP = "192.168.0.3"
SHIP_ROLE = "Torus Coffee Commander (Miss Pink)"

def log(msg: str) -> None:
    try:
        line = f"[{datetime.now(timezone.utc).isoformat()}] {msg}"
        LOG_FILE.parent.mkdir(parents=True, exist_ok=True)
        with open(LOG_FILE, "a", encoding="utf-8") as f:
            f.write(line + "\n")
        print(line)
    except Exception:
        pass

def get_docker_status() -> dict:
    """Check Docker containers."""
    try:
        r = subprocess.run(
            ["docker", "ps", "--format", "{{json .}}"],
            capture_output=True, text=True, timeout=10,
            creationflags=0x08000000  # CREATE_NO_WINDOW
        )
        if r.returncode == 0:
            containers = [json.loads(line) for line in r.stdout.strip().split("\n") if line]
            healthy = sum(1 for c in containers if "healthy" in c.get("Status", ""))
            total = len(containers)
            return {"running": total, "healthy": healthy, "containers": [c.get("Names", "") for c in containers]}
    except Exception as e:
        return {"error": str(e)}
    return {"running": 0, "healthy": 0}

def get_tailscale_status() -> dict:
    """Check Tailscale."""
    try:
        r = subprocess.run(["tailscale", "status"], capture_output=True, text=True, timeout=5)
        if r.returncode == 0:
            for line in r.stdout.split("\n"):
                if SHIP_NAME.lower() in line.lower():
                    parts = line.split()
                    return {"ip": parts[0] if parts else "unknown", "status": "online", "raw": line.strip()[:200]}
        return {"status": "offline"}
    except Exception:
        return {"status": "unknown"}

def get_disk_usage() -> dict:
    try:
        usage = os.statvfs(str(BASE))
        free_gb = (usage.f_bavail * usage.f_frsize) / 1024 / 1024 / 1024
        total_gb = (usage.f_blocks * usage.f_frsize) / 1024 / 1024 / 1024
        return {"free_gb": round(free_gb, 1), "total_gb": round(total_gb, 1)}
    except Exception:
        return {"free_gb": 0, "total_gb": 0}

def build_status() -> dict:
    return {
        "ship": SHIP_NAME,
        "ip": SHIP_IP,
        "role": SHIP_ROLE,
        "status": "online",
        "timestamp": datetime.now(timezone.utc).isoformat(),
        "docker": get_docker_status(),
        "tailscale": get_tailscale_status(),
        "disk": get_disk_usage(),
        "port_8090": "listening",
        "crew_api_version": "1.0.0"
    }

def handle_request(conn, addr):
    """Handle a single HTTP request."""
    try:
        data = conn.recv(4096)
        request_line = data.decode("utf-8", errors="ignore").split("\r\n")[0]
        path = request_line.split(" ")[1] if " " in request_line else "/"
        
        if path in ("/health", "/api/health", "/"):
            status = build_status()
            if path == "/" or path == "/health":
                # Return full status
                body = json.dumps(status, indent=2, default=str)
            else:
                body = json.dumps(status, default=str)
            response = f"HTTP/1.1 200 OK\r\nContent-Type: application/json\r\nContent-Length: {len(body)}\r\n\r\n{body}"
        else:
            body = json.dumps({"error": "not found", "path": path})
            response = f"HTTP/1.1 404 Not Found\r\nContent-Type: application/json\r\nContent-Length: {len(body)}\r\n\r\n{body}"
        
        conn.sendall(response.encode("utf-8"))
    except Exception as e:
        log(f"REQUEST_ERROR: {e}")
    finally:
        conn.close()

def main():
    log("CREW_API_STARTED — port 8090")
    host = "0.0.0.0"
    port = 8090
    with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
        s.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
        s.bind((host, port))
        s.listen(5)
        log(f"Listening on {host}:{port}")
        while True:
            try:
                conn, addr = s.accept()
                handle_request(conn, addr)
            except Exception as e:
                log(f"ACCEPT_ERROR: {e}")

if __name__ == "__main__":
    main()
